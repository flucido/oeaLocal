# Automated Pipeline Scheduling

This directory contains automation scripts for scheduled execution of the local-data-stack pipeline.

## Overview

The pipeline can be scheduled to run automatically using:
- **Cron** (traditional Unix scheduler)
- **Systemd timers** (modern Linux scheduler)
- **macOS launchd** (macOS scheduler)

All methods use the wrapper script `scripts/schedule_pipeline.sh` which provides:
- Lock file management (prevents concurrent runs)
- Environment validation
- Logging and error handling
- Timeout protection (2-hour max runtime)
- Post-execution cleanup

---

## Option 1: Cron (Simplest)

### Installation

**1. Edit crontab:**
```bash
crontab -e
```

**2. Add daily execution at 6 AM:**
```cron
# Local Data Stack - Daily Analytics Pipeline
0 6 * * * cd /Users/flucido/projects/local-data-stack && ./scripts/schedule_pipeline.sh >> oss_framework/logs/cron.log 2>&1
```

**3. Verify cron job installed:**
```bash
crontab -l
```

### Cron Schedule Examples

```cron
# Daily at 6 AM
0 6 * * * cd /Users/flucido/projects/local-data-stack && ./scripts/schedule_pipeline.sh

# Every 6 hours
0 */6 * * * cd /Users/flucido/projects/local-data-stack && ./scripts/schedule_pipeline.sh

# Monday-Friday at 7 AM (weekdays only)
0 7 * * 1-5 cd /Users/flucido/projects/local-data-stack && ./scripts/schedule_pipeline.sh

# Every Sunday at 3 AM (weekly)
0 3 * * 0 cd /Users/flucido/projects/local-data-stack && ./scripts/schedule_pipeline.sh
```

### Cron Monitoring

**View cron logs:**
```bash
tail -f oss_framework/logs/cron.log
```

**Check last execution:**
```bash
ls -lt oss_framework/logs/pipeline_scheduled_*.log | head -1
```

**Disable cron job:**
```bash
crontab -e
# Comment out the line with #
```

**Remove cron job:**
```bash
crontab -r  # ⚠️ Removes ALL cron jobs
```

---

## Option 2: Systemd Timer (Linux Only)

### Installation

**1. Create systemd service:**
```bash
sudo nano /etc/systemd/system/local-data-stack.service
```

**Content:**
```ini
[Unit]
Description=Local Data Stack Analytics Pipeline
After=network.target

[Service]
Type=oneshot
User=flucido
Group=flucido
WorkingDirectory=/Users/flucido/projects/local-data-stack
ExecStart=/Users/flucido/projects/local-data-stack/scripts/schedule_pipeline.sh
StandardOutput=append:/Users/flucido/projects/local-data-stack/oss_framework/logs/systemd.log
StandardError=append:/Users/flucido/projects/local-data-stack/oss_framework/logs/systemd.log

# Environment
Environment="PATH=/usr/local/bin:/usr/bin:/bin"

# Timeout protection
TimeoutStartSec=7200

# Resource limits (optional)
MemoryLimit=8G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**2. Create systemd timer:**
```bash
sudo nano /etc/systemd/system/local-data-stack.timer
```

**Content:**
```ini
[Unit]
Description=Local Data Stack Daily Analytics Pipeline
Requires=local-data-stack.service

[Timer]
# Run daily at 6 AM
OnCalendar=daily
# Offset from midnight (6 hours = 6 AM)
OnCalendar=*-*-* 06:00:00
# Persistent (run missed executions on boot)
Persistent=true
# Randomize start within 5 minutes (avoid exact-time spikes)
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
```

**3. Enable and start timer:**
```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable timer (start on boot)
sudo systemctl enable local-data-stack.timer

# Start timer immediately
sudo systemctl start local-data-stack.timer

# Check timer status
sudo systemctl status local-data-stack.timer
```

### Systemd Management

**View timer status:**
```bash
systemctl status local-data-stack.timer
systemctl list-timers local-data-stack.timer
```

**View service logs:**
```bash
journalctl -u local-data-stack.service -f
```

**Trigger manual execution:**
```bash
sudo systemctl start local-data-stack.service
```

**Stop timer:**
```bash
sudo systemctl stop local-data-stack.timer
sudo systemctl disable local-data-stack.timer
```

### Systemd Timer Schedule Examples

```ini
# Every 6 hours
OnCalendar=00/6:00:00

# Monday-Friday at 7 AM (weekdays)
OnCalendar=Mon-Fri *-*-* 07:00:00

# Weekly on Sunday at 3 AM
OnCalendar=Sun *-*-* 03:00:00

# Monthly on 1st day at 2 AM
OnCalendar=*-*-01 02:00:00
```

---

## Option 3: macOS launchd

### Installation

**1. Create launchd plist:**
```bash
nano ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
```

**Content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.localdata.analytics-pipeline</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/flucido/projects/local-data-stack/scripts/schedule_pipeline.sh</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/flucido/projects/local-data-stack</string>
    
    <key>StandardOutPath</key>
    <string>/Users/flucido/projects/local-data-stack/oss_framework/logs/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/flucido/projects/local-data-stack/oss_framework/logs/launchd.log</string>
    
    <!-- Run daily at 6 AM -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <!-- Run on load (optional) -->
    <key>RunAtLoad</key>
    <false/>
    
    <!-- Keep alive (restart on crash) -->
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

**2. Load launchd job:**
```bash
launchctl load ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
```

**3. Verify loaded:**
```bash
launchctl list | grep localdata
```

### macOS launchd Management

**View logs:**
```bash
tail -f oss_framework/logs/launchd.log
```

**Trigger manual execution:**
```bash
launchctl start com.localdata.analytics-pipeline
```

**Unload job:**
```bash
launchctl unload ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
```

**Reload after changes:**
```bash
launchctl unload ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
launchctl load ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
```

---

## Monitoring & Troubleshooting

### Check Execution History

**Last 10 pipeline runs:**
```bash
ls -lt oss_framework/logs/pipeline_scheduled_*.log | head -10
```

**View latest log:**
```bash
tail -100 $(ls -t oss_framework/logs/pipeline_scheduled_*.log | head -1)
```

**Count successful runs:**
```bash
grep "Pipeline completed successfully" oss_framework/logs/pipeline_scheduled_*.log | wc -l
```

**Count failures:**
```bash
grep "Pipeline failed" oss_framework/logs/pipeline_scheduled_*.log | wc -l
```

### Common Issues

**1. Lock file prevents execution:**
```bash
# Check if pipeline is actually running
ps aux | grep run_pipeline.py

# If not running, remove stale lock
rm -f .pipeline.lock
```

**2. Virtual environment not found:**
```bash
# Recreate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**3. Permissions error:**
```bash
# Make script executable
chmod +x scripts/schedule_pipeline.sh

# Fix log directory permissions
chmod 755 oss_framework/logs
```

**4. Timeout after 2 hours:**
```bash
# Check for stuck processes
ps aux | grep duckdb
ps aux | grep dbt

# Increase timeout in schedule_pipeline.sh
# Change: MAX_RUNTIME_MINUTES=120
# To:     MAX_RUNTIME_MINUTES=240
```

---

## Integration with Monitoring

### Prometheus Metrics (Future)

Add to end of `scripts/schedule_pipeline.sh`:

```bash
# Export metrics to Prometheus
cat > /var/lib/prometheus/node_exporter/pipeline.prom << EOF
# HELP pipeline_last_run_timestamp_seconds Last pipeline run timestamp
# TYPE pipeline_last_run_timestamp_seconds gauge
pipeline_last_run_timestamp_seconds $(date +%s)

# HELP pipeline_last_run_success Pipeline success (1) or failure (0)
# TYPE pipeline_last_run_success gauge
pipeline_last_run_success ${exit_code:-0}

# HELP pipeline_duration_seconds Pipeline execution duration
# TYPE pipeline_duration_seconds gauge
pipeline_duration_seconds ${duration}
EOF
```

### Email Notifications (Future)

Add to `cleanup()` function in `scripts/schedule_pipeline.sh`:

```bash
if [[ $exit_code -eq 0 ]]; then
    # Success email
    echo "Pipeline completed successfully at $(date)" | \
    mail -s "✅ Analytics Pipeline Success" admin@yourdistrict.edu
else
    # Failure email
    echo "Pipeline failed with exit code ${exit_code}" | \
    mail -s "❌ Analytics Pipeline Failure" admin@yourdistrict.edu
fi
```

### Slack Notifications (Future)

```bash
# Send to Slack webhook
curl -X POST \
  -H 'Content-type: application/json' \
  --data "{\"text\":\"Pipeline ${status}: ${message}\"}" \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## Best Practices

### Scheduling Recommendations

1. **Daily Execution**: Run at 6 AM before business hours
2. **Off-Peak**: Avoid peak database usage times
3. **Weekends**: Consider Sunday 3 AM for full refresh
4. **Incremental**: Daily incremental + weekly full refresh

### Log Retention

The `schedule_pipeline.sh` script automatically:
- Archives logs older than 30 days
- Compresses logs larger than 10 MB
- Keeps latest 30 days uncompressed

**Manual cleanup:**
```bash
# Delete logs older than 90 days
find oss_framework/logs -name "pipeline_scheduled_*.log*" -mtime +90 -delete

# Keep only last 100 logs
ls -t oss_framework/logs/pipeline_scheduled_*.log | tail -n +101 | xargs rm -f
```

### Resource Management

**Limit CPU usage (Linux only):**
```bash
# Use nice to lower priority
nice -n 10 ./scripts/schedule_pipeline.sh
```

**Limit memory (systemd):**
```ini
# In local-data-stack.service
MemoryLimit=8G
```

**Monitor resource usage:**
```bash
# While pipeline runs
top -p $(pgrep -f run_pipeline.py)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Install cron** | `crontab -e` → Add line → Save |
| **Check cron** | `crontab -l` |
| **View logs** | `tail -f oss_framework/logs/cron.log` |
| **Manual run** | `./scripts/schedule_pipeline.sh` |
| **Test run** | `./scripts/schedule_pipeline.sh --dry-run` |
| **Remove lock** | `rm -f .pipeline.lock` |
| **Check status** | `ls -lt oss_framework/logs/pipeline_scheduled_*.log \| head -1` |

---

## Next Steps

After setting up automation:

1. ✅ **Test manual execution**
   ```bash
   ./scripts/schedule_pipeline.sh --dry-run
   ./scripts/schedule_pipeline.sh
   ```

2. ✅ **Install scheduler** (choose one: cron, systemd, launchd)

3. ✅ **Monitor first scheduled run**
   ```bash
   tail -f oss_framework/logs/pipeline_scheduled_*.log
   ```

4. ⏳ **Set up monitoring** (Prometheus, email, Slack)

5. ⏳ **Configure backups** (DuckDB daily backups)

---

## Support

**Documentation:**
- Production Deployment: `oss_framework/PRODUCTION_DEPLOYMENT.md`
- Operational Runbooks: `oss_framework/OPERATIONAL_RUNBOOKS.md`
- Current State Analysis: `CURRENT_STATE_ANALYSIS.md`

**Troubleshooting:**
- Check logs: `oss_framework/logs/`
- Verify environment: `./scripts/schedule_pipeline.sh --dry-run`
- Review pipeline: `python3 scripts/run_pipeline.py --help`
