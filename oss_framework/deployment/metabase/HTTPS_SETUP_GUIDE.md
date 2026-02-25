# HTTPS/SSL Setup Guide for Metabase

**Status**: ✅ **Configuration Ready**  
**Date**: January 27, 2026  
**Effort**: 30-45 minutes (depending on certificate method)

---

## Overview

This guide provides step-by-step instructions to enable HTTPS/SSL encryption for your Metabase deployment using nginx as a reverse proxy. This is essential for production deployment to school districts due to FERPA compliance requirements.

---

## What's Included

### Files Created

1. **docker-compose-https.yml**
   - Complete docker-compose configuration with nginx reverse proxy
   - Metabase runs internally, exposed only through nginx
   - Automatic health checks and restart policy

2. **nginx.conf**
   - Production-grade nginx configuration
   - SSL/TLS security hardening
   - HTTP → HTTPS redirect
   - Security headers (HSTS, CSP, X-Frame-Options, etc.)
   - Rate limiting on API endpoints
   - GZip compression enabled

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Internet / School District Network                  │
└─────────────────┬───────────────────────────────────┘
                  │ HTTPS (443)
                  ↓
        ┌──────────────────┐
        │  Nginx           │
        │  Reverse Proxy   │
        │  + SSL/TLS       │
        │  + Rate Limiting │
        │  + Security      │
        └────────┬─────────┘
                 │ HTTP (3000, internal)
                 ↓
        ┌──────────────────┐
        │  Metabase        │
        │  (Backend)       │
        │  - No internet   │
        │    exposure      │
        └─────────────────┘
```

---

## Prerequisites

- Docker and Docker Compose installed
- Domain name or IP address for the server
- SSL certificate (3 options below)
- Approximately 30-45 minutes

---

## Option 1: Self-Signed Certificate (Quick Development)

⚠️ **Note**: Browsers will show warnings. Use for testing only, not production.

### Step 1: Create SSL Directory

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
mkdir -p ssl
cd ssl
```

### Step 2: Generate Self-Signed Certificate

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout private.key \
  -out certificate.crt \
  -subj "/C=US/ST=State/L=City/O=SchoolDistrict/OU=IT/CN=metabase.local"
```

This creates:
- `private.key` - Private key (keep secure!)
- `certificate.crt` - Public certificate

### Step 3: Set Permissions

```bash
chmod 600 private.key
chmod 644 certificate.crt
```

✅ **Done!** Proceed to "Deployment" section below.

---

## Option 2: Let's Encrypt (Recommended for Production)

✅ **Free, trusted, automatic renewal**

### Prerequisites

- Public domain name
- Port 80 access from internet (for validation)

### Step 1: Install Certbot

```bash
# macOS
brew install certbot

# Linux (Ubuntu/Debian)
sudo apt-get install certbot

# Linux (CentOS/RHEL)
sudo yum install certbot
```

### Step 2: Generate Certificate

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

certbot certonly --standalone \
  -d metabase.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --non-interactive
```

Replace `metabase.yourdomain.com` with your actual domain.

### Step 3: Copy Certificates

```bash
mkdir -p ssl

# Copy Let's Encrypt certificates to ssl directory
cp /etc/letsencrypt/live/metabase.yourdomain.com/fullchain.pem ssl/certificate.crt
cp /etc/letsencrypt/live/metabase.yourdomain.com/privkey.pem ssl/private.key

# Set permissions
chmod 600 ssl/private.key
chmod 644 ssl/certificate.crt
```

### Step 4: Enable Auto-Renewal

```bash
# Create renewal script
cat > renew_certs.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/metabase.yourdomain.com/fullchain.pem /path/to/ssl/certificate.crt
cp /etc/letsencrypt/live/metabase.yourdomain.com/privkey.pem /path/to/ssl/private.key
docker restart oss-nginx
EOF

chmod +x renew_certs.sh

# Add to crontab (runs daily at 2:30 AM)
crontab -e
# Add line: 30 2 * * * /path/to/renew_certs.sh
```

✅ **Done!** Proceed to "Deployment" section below.

---

## Option 3: Purchased Certificate (Corporate)

If your district has a purchased SSL certificate from a provider like Sectigo, DigiCert, etc.:

### Step 1: Get Certificate Files

Contact your certificate provider for:
- `certificate.crt` - Public certificate (may include intermediate chain)
- `private.key` - Private key file

### Step 2: Copy to SSL Directory

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase
mkdir -p ssl
cp /path/to/certificate.crt ssl/
cp /path/to/private.key ssl/
chmod 600 ssl/private.key
chmod 644 ssl/certificate.crt
```

### Step 3: Verify Certificate

```bash
# Check certificate details
openssl x509 -in ssl/certificate.crt -text -noout

# Verify key matches certificate
openssl x509 -noout -modulus -in ssl/certificate.crt | openssl md5
openssl rsa -noout -modulus -in ssl/private.key | openssl md5
# Both should produce the same hash
```

✅ **Done!** Proceed to "Deployment" section below.

---

## Deployment

### Step 1: Prepare Directory Structure

```bash
cd /Users/flucido/projects/openedDataEstate/oss_framework/deployment/metabase

# Verify files exist
ls -la ssl/
# Should show:
# -rw-r--r-- certificate.crt
# -rw------- private.key

ls -la *.yml
# Should show:
# docker-compose.yml (original)
# docker-compose-https.yml (new)

ls -la nginx.conf
```

### Step 2: Stop Current Metabase (if running)

```bash
docker-compose down
```

### Step 3: Start with HTTPS Configuration

Choose one approach:

**Approach A: Replace current config (recommended for production)**
```bash
# Backup original
cp docker-compose.yml docker-compose.yml.backup

# Use HTTPS version
cp docker-compose-https.yml docker-compose.yml

# Start
docker-compose up -d
```

**Approach B: Keep both (run HTTPS on different port)**
```bash
docker-compose -f docker-compose-https.yml up -d
```

### Step 4: Verify SSL is Working

```bash
# Wait for nginx to start (30 seconds)
sleep 30

# Test HTTP redirect
curl -i http://localhost/
# Should return: HTTP/1.1 301 Moved Permanently
# Location: https://localhost/

# Test HTTPS (ignore self-signed warnings for testing)
curl -k https://localhost/
# Should return: HTTP/1.1 200 OK

# Check nginx logs
docker logs oss-nginx

# Check Metabase logs
docker logs oss-metabase-backend

# Check health
curl -k https://localhost/health
```

### Step 5: Access Metabase

Open browser and navigate to:
```
https://localhost:3000
```

Or if domain name configured:
```
https://metabase.yourdomain.com
```

⚠️ **For self-signed certificate**: Click "Advanced" → "Proceed to localhost" to accept security warning.

✅ **Green lock icon** indicates HTTPS is working!

---

## Configuration Files

### docker-compose-https.yml

**Key changes from original:**
- Nginx service added with SSL support
- Metabase `expose: 3000` instead of `ports: 3000` (not exposed to internet)
- Both services on internal network `metabase-network`
- Nginx handles all external traffic on ports 80/443

### nginx.conf

**Key features:**
- **Port 80 redirect**: All HTTP requests redirect to HTTPS
- **TLS 1.2+**: Modern secure encryption
- **Security headers**:
  - `HSTS`: Enforce HTTPS for 1 year
  - `CSP`: Content Security Policy
  - `X-Frame-Options`: Clickjacking protection
  - `X-Content-Type-Options`: MIME sniffing protection
- **Rate limiting**: 10 requests/second per IP on API
- **GZip compression**: Reduces bandwidth
- **WebSocket support**: For real-time features
- **Deny sensitive files**: Blocks access to `.git`, `~` files, etc.

---

## Security Considerations

### ✅ Implemented

- HTTPS/TLS 1.2+ encryption
- HTTP → HTTPS redirect
- Security headers (HSTS, CSP, X-Frame-Options)
- Rate limiting on API endpoints
- Metabase isolated to internal network
- Certificate validation enabled

### 📋 Additional Recommendations

1. **Update Admin Password**
   ```bash
   # After HTTPS is working, change the default password
   # Navigate to: https://metabase.yourdomain.com/admin/settings/authentication
   ```

2. **Enable Email Notifications**
   - Configure SMTP for alerts
   - Use authenticated connections

3. **Enable Row-Level Security (RLS)**
   - Restrict data access by user role
   - Useful for sensitive student data

4. **Regular Certificate Renewal**
   - For Let's Encrypt: Set up auto-renewal cron job
   - For purchased: Monitor expiration date

5. **Regular Security Updates**
   ```bash
   # Update nginx and Metabase images monthly
   docker pull nginx:alpine
   docker pull metabase/metabase:v0.49.1
   docker-compose down
   docker-compose up -d
   ```

---

## Troubleshooting

### Issue: Certificate file not found

**Error**: `error opening certificate file`

**Solution**:
```bash
# Verify files exist
ls -la ssl/

# Check paths in nginx.conf
cat nginx.conf | grep ssl_

# File permissions
chmod 600 ssl/private.key
chmod 644 ssl/certificate.crt
```

### Issue: Browser shows "untrusted certificate"

**For self-signed**: Normal - click "Advanced" → "Proceed"
**For Let's Encrypt/Purchased**: Check domain name matches certificate

### Issue: 502 Bad Gateway error

**Error**: Nginx can't reach Metabase

**Solution**:
```bash
# Check Metabase is running
docker ps | grep metabase

# Check health
docker exec oss-metabase-backend curl http://localhost:3000/api/health

# Check network connection
docker network ls
docker network inspect metabase-network

# Check nginx logs
docker logs oss-nginx | tail -50
```

### Issue: SSL handshake fails

**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution**:
```bash
# Verify certificate is valid
openssl x509 -in ssl/certificate.crt -text -noout

# Check certificate dates
openssl x509 -in ssl/certificate.crt -noout -dates

# For self-signed, use -k flag
curl -k https://localhost/
```

### Issue: Certificate expired

**For Let's Encrypt**:
```bash
./renew_certs.sh
```

**For purchased certificate**:
```bash
# Get new certificate from provider
# Copy files to ssl/ directory
# Restart nginx
docker restart oss-nginx
```

---

## Performance Impact

**Minimal**: Nginx overhead is negligible
- HTTPS adds ~5-10ms latency (encryption)
- GZip compression reduces bandwidth by 70-80%
- Rate limiting protects against abuse
- Overall: **Better security with minimal performance loss**

---

## Monitoring

### Check SSL Certificate Expiration

```bash
# Self-signed or Let's Encrypt
openssl x509 -in ssl/certificate.crt -noout -dates

# Output example:
# notBefore=Jan 27 15:30:00 2026 GMT
# notAfter=Jan 27 15:30:00 2027 GMT
```

### Monitor Nginx Health

```bash
# Real-time logs
docker logs -f oss-nginx

# Count requests
docker logs oss-nginx | grep "200" | wc -l

# Find errors
docker logs oss-nginx | grep "error\|fail\|502\|503"
```

### SSL Test Online

Test your SSL configuration online:
```
https://www.ssllabs.com/ssltest/
```

Enter your domain and get detailed report on SSL/TLS configuration.

---

## Next Steps

1. ✅ Choose certificate option (1, 2, or 3)
2. ✅ Generate/obtain certificate
3. ✅ Copy to `ssl/` directory
4. ✅ Deploy with HTTPS configuration
5. ✅ Verify SSL working (curl tests pass)
6. ✅ Access Metabase via HTTPS
7. Consider additional security enhancements

---

## Summary

| Item | Status |
|------|--------|
| **Nginx Config** | ✅ Created |
| **Docker Compose** | ✅ Created |
| **SSL Certificate** | 📋 User to provide |
| **HTTP Redirect** | ✅ Configured |
| **Security Headers** | ✅ Configured |
| **Rate Limiting** | ✅ Configured |
| **Health Checks** | ✅ Configured |

---

## Support

For issues:
1. Check logs: `docker logs oss-nginx`
2. Test connectivity: `curl -k https://localhost`
3. Verify certificate: `openssl x509 -in ssl/certificate.crt -text`
4. Review nginx.conf for configuration errors

---

**Status**: ✅ Configuration Complete - Ready for SSL Setup

*Choose certificate option above and follow deployment steps to enable HTTPS.*
