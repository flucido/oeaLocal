# Security Policy

## Overview

The OSS Framework handles sensitive student data and must be deployed with appropriate security measures. This document outlines security best practices, vulnerability reporting, and compliance guidance for FERPA/GDPR.

---

## Reporting Security Vulnerabilities

### Reporting Process

**Please do not report security vulnerabilities through public GitHub issues.**

To report a security vulnerability:

1. **Email**: Send details to `security@openedDataEstate.org` (if available) or open a private security advisory on GitHub
2. **GitHub Security Advisory**: Use [GitHub's private vulnerability reporting](https://github.com/flucido/openedDataEstate/security/advisories/new)
3. **Response Time**: We aim to respond within 72 hours

### What to Include

Please provide as much detail as possible:

- **Type of vulnerability** (e.g., SQL injection, path traversal, authentication bypass)
- **Affected component** (DuckDB, Metabase, dbt, ingestion scripts, etc.)
- **Steps to reproduce** the issue
- **Potential impact** (data exposure, unauthorized access, etc.)
- **Suggested fix** (if available)
- **Proof-of-concept** (if safe to share)

### Disclosure Policy

- We follow [responsible disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure) practices
- We will acknowledge receipt within 72 hours
- We will provide a fix timeline or workaround
- We will coordinate public disclosure after a fix is available
- We will credit reporters in release notes (unless anonymity requested)

---

## Security Best Practices

### 1. Student Data Protection (FERPA/GDPR)

#### Pseudonymization (Required)

**OSS Framework implements pseudonymization by default:**

- **PII Hashing**: Student names, IDs, emails are SHA-256 hashed
- **Lookup Tables**: Stored separately with restricted access
- **Stage Separation**:
  - **Stage 1 (Raw)**: Contains identifiable data (restricted access)
  - **Stage 2 (Refined/General)**: Pseudonymized data (analytics team access)
  - **Stage 2 (Refined/Sensitive)**: Lookup tables (administrators only)
  - **Stage 3 (Analytics)**: Aggregated, anonymized (broad access)

**Configuration:**

```python
# oss_framework/config/privacy.py
PSEUDONYMIZATION_CONFIG = {
    'hash_algorithm': 'sha256',
    'salt': os.environ.get('PRIVACY_SALT'),  # Set this in production!
    'pii_fields': ['student_name', 'student_id', 'email', 'address']
}
```

#### Data Minimization

- Only collect data required for analytics use cases
- Regularly purge outdated data per retention policy
- Avoid collecting sensitive categories unless essential

#### Access Control

```bash
# File system permissions (Linux example)
sudo chown -R analytics-user:analytics-group data/stage2/refined/general
sudo chmod 750 data/stage2/refined/general

sudo chown -R admin-user:admin-group data/stage2/refined/sensitive
sudo chmod 700 data/stage2/refined/sensitive
```

---

### 2. Infrastructure Security

#### Encryption at Rest

**Required for production deployments:**

- **Linux**: Use LUKS full-disk encryption
  ```bash
  cryptsetup luksFormat /dev/sdX
  cryptsetup open /dev/sdX encrypted-data
  mkfs.ext4 /dev/mapper/encrypted-data
  ```

- **Windows**: Use BitLocker
  ```powershell
  Enable-BitLocker -MountPoint "D:" -EncryptionMethod Aes256
  ```

- **macOS**: Use FileVault (System Preferences → Security & Privacy)

#### Encryption in Transit

**Metabase HTTPS Setup (Required):**

```yaml
# docker-compose.yml
metabase:
  environment:
    MB_JETTY_SSL: "true"
    MB_JETTY_SSL_PORT: "443"
    MB_JETTY_SSL_KEYSTORE: "/path/to/keystore.jks"
    MB_JETTY_SSL_KEYSTORE_PASSWORD: "${KEYSTORE_PASSWORD}"
```

**See**: [HTTPS Setup Guide](oss_framework/deployment/metabase/HTTPS_SETUP_GUIDE.md)

#### Network Security

- **Firewall**: Restrict access to Metabase, Dagster, JupyterLab
  ```bash
  # Example: ufw (Ubuntu)
  sudo ufw allow from 192.168.1.0/24 to any port 3000  # Metabase (internal only)
  sudo ufw allow from 192.168.1.0/24 to any port 3001  # Dagster (internal only)
  sudo ufw deny 3000  # Block external access
  ```

- **VPN**: Use VPN for remote access to services
- **No Public Exposure**: Never expose DuckDB, Dagster, or JupyterLab to the internet

---

### 3. Authentication & Authorization

#### Metabase Access Control

**Role-Based Access Control (RBAC):**

```sql
-- Example: Restrict sensitive data access
CREATE VIEW public_analytics AS
SELECT 
    hashed_student_id,
    grade_level,
    attendance_rate,
    -- NO personal identifiers
FROM refined.students;
```

**Metabase User Roles:**

| Role | Access | Use Case |
|------|--------|----------|
| **Administrator** | All data + admin panel | IT staff |
| **Analyst** | Stage 2 general + Stage 3 | District analytics team |
| **Educator** | Stage 3 aggregated dashboards | Teachers, principals |
| **Board Member** | Stage 3 summary dashboards | Board members |

**See**: [Access Control Guide](oss_framework/deployment/metabase/access-control-guide.md)

#### System Access

- **SSH Keys Only**: Disable password authentication
  ```bash
  # /etc/ssh/sshd_config
  PasswordAuthentication no
  PubkeyAuthentication yes
  ```

- **Sudo Access**: Limit to essential administrators
- **Service Accounts**: Use dedicated accounts for Dagster, Metabase

---

### 4. DuckDB Security

#### File Permissions

```bash
# Restrict DuckDB file access
chmod 600 data/oea.duckdb
chown analytics-user:analytics-group data/oea.duckdb
```

#### Read-Only Access

```python
# For analytics users (read-only)
import duckdb
con = duckdb.connect('data/oea.duckdb', read_only=True)
```

#### Query Injection Prevention

**Always use parameterized queries:**

```python
# BAD: SQL injection risk
student_id = request.args.get('student_id')
con.execute(f"SELECT * FROM students WHERE id = '{student_id}'")

# GOOD: Parameterized
student_id = request.args.get('student_id')
con.execute("SELECT * FROM students WHERE id = ?", [student_id])
```

---

### 5. Dependency Management

#### Regular Updates

```bash
# Update Python dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull
docker-compose up -d
```

#### Security Scanning

```bash
# Scan Python dependencies
pip install safety
safety check --json

# Scan Docker images
docker scan metabase:latest
```

#### Pinned Versions

**Use exact versions in production:**

```txt
# requirements.txt (example)
duckdb==0.9.2
dbt-core==1.7.4
dlt==0.4.2
```

---

### 6. Audit Logging

#### Dagster Logs

**All pipeline runs are logged:**

```bash
# View Dagster logs
docker-compose logs dagster
```

**Retain logs for compliance:**

```yaml
# docker-compose.yml
dagster:
  logging:
    driver: "json-file"
    options:
      max-size: "100m"
      max-file: "10"
```

#### Metabase Query Logs

**Enable query logging:**

```sql
-- Metabase stores query history in internal database
SELECT * FROM query_execution
WHERE executed_at > NOW() - INTERVAL '30 days'
ORDER BY executed_at DESC;
```

#### Access Logs

**Monitor access to sensitive files:**

```bash
# Linux: auditd
sudo auditctl -w /path/to/data/stage2/refined/sensitive -p rwa -k sensitive_access

# View logs
sudo ausearch -k sensitive_access
```

---

### 7. Backup & Disaster Recovery

#### Encrypted Backups

```bash
# Example: Encrypted backup to external drive
tar czf - data/ | openssl enc -aes-256-cbc -salt -out backup.tar.gz.enc

# Restore
openssl enc -d -aes-256-cbc -in backup.tar.gz.enc | tar xzf -
```

#### Backup Retention

- **Daily**: Keep 7 days
- **Weekly**: Keep 4 weeks
- **Monthly**: Keep 12 months
- **Annually**: Keep 7 years (FERPA requirement)

---

### 8. Secure Configuration

#### Environment Variables

**Never commit secrets to Git:**

```bash
# .env (not tracked in Git)
PRIVACY_SALT="your-secret-salt-here"
MB_DB_PASSWORD="metabase-db-password"
DAGSTER_SECRET_KEY="dagster-secret"
```

**Use `.gitignore`:**

```gitignore
.env
*.key
*.pem
*.p12
data/stage2/refined/sensitive/
```

#### Configuration Validation

```bash
# Check for exposed secrets
git secrets --scan

# Check file permissions
find data/ -type f -perm /o+r  # No world-readable files
```

---

## Compliance Checklist

### FERPA Compliance

- [ ] Student data is pseudonymized
- [ ] Access controls are enforced (file permissions + Metabase roles)
- [ ] Audit logging is enabled
- [ ] Data retention policy is defined and enforced
- [ ] Staff are trained on data privacy
- [ ] Written security policy is documented

### GDPR Compliance (if applicable)

- [ ] Legal basis for processing is documented
- [ ] Data minimization is enforced
- [ ] Right to erasure is supported (data deletion procedures)
- [ ] Data breach notification procedures are defined
- [ ] Privacy by design is implemented (pseudonymization)

---

## Incident Response

### In Case of Security Breach

1. **Contain**: Immediately restrict access to affected systems
2. **Assess**: Determine scope of breach (what data, how many records)
3. **Notify**: Inform affected parties per FERPA/GDPR requirements
4. **Remediate**: Apply fixes and security improvements
5. **Document**: Record incident details and response actions

### FERPA Breach Notification

**Required by law:**
- Notify affected students/parents
- Notify U.S. Department of Education (if breach involves >500 records)
- Timeline: "Without unreasonable delay" (typically within 72 hours)

---

## Security Resources

- **FERPA Compliance**: [U.S. Department of Education](https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html)
- **GDPR Compliance**: [GDPR.eu](https://gdpr.eu/)
- **NIST Cybersecurity Framework**: [NIST CSF](https://www.nist.gov/cyberframework)
- **DuckDB Security**: [DuckDB Docs](https://duckdb.org/docs/)
- **Metabase Security**: [Metabase Security Guide](https://www.metabase.com/docs/latest/security-guide/)

---

## Contact

For security concerns, please contact:
- **Email**: security@openedDataEstate.org (if available)
- **GitHub**: [Private Security Advisory](https://github.com/flucido/openedDataEstate/security/advisories/new)

---

**Note**: This document provides guidance but is not legal advice. Consult your district's legal counsel to ensure compliance with applicable laws and regulations.
