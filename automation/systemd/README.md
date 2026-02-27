# systemd Installation and Management Guide

This directory contains systemd service and timer files for production deployment
of the Local Data Stack analytics pipeline.

## Quick Start

```bash
# 1. Copy service files to systemd directory
sudo cp local-data-stack.service /etc/systemd/system/
sudo cp local-data-stack.timer /etc/systemd/system/

# 2. Reload systemd daemon
sudo systemctl daemon-reload

# 3. Enable and start timer
sudo systemctl enable local-data-stack.timer
sudo systemctl start local-data-stack.timer

# 4. Verify timer is active
systemctl list-timers --all | grep local-data-stack
```

## Files

- **local-data-stack.service** - Service unit that runs the pipeline
- **local-data-stack.timer** - Timer unit that schedules daily execution at 6 AM

## Configuration

### User and Group

The service runs as `datapipeline` user by default. Create this user:

```bash
# Create dedicated user (no login shell)
sudo useradd -r -s /bin/false datapipeline

# Grant ownership of project directory
sudo chown -R datapipeline:datapipeline /Users/flucido/projects/local-data-stack
```

### Working Directory

Update `WorkingDirectory` in `local-data-stack.service` if your project path differs:

```ini
WorkingDirectory=/path/to/your/local-data-stack
```

### Resource Limits

Current limits (adjust based on your system):

- **Memory**: 4GB max, 3GB soft limit
- **CPU**: 200% (2 full cores)
- **I/O**: 50 MB/s read/write

Edit `local-data-stack.service` to change:

```ini
MemoryMax=8G        # Increase for larger datasets
CPUQuota=400%       # Use 4 cores
```

## Management Commands

### Timer Operations

```bash
# Start timer (begin scheduling)
sudo systemctl start local-data-stack.timer

# Stop timer (stop scheduling, but don't cancel running job)
sudo systemctl stop local-data-stack.timer

# Enable timer (start on boot)
sudo systemctl enable local-data-stack.timer

# Disable timer (don't start on boot)
sudo systemctl disable local-data-stack.timer

# Check timer status
systemctl status local-data-stack.timer

# List all timers and next execution time
systemctl list-timers
```

### Service Operations (Manual Execution)

```bash
# Run pipeline manually (outside of timer schedule)
sudo systemctl start local-data-stack.service

# Check service status
systemctl status local-data-stack.service

# View service logs
journalctl -u local-data-stack.service

# Follow logs in real-time
journalctl -u local-data-stack.service -f

# View logs from last execution
journalctl -u local-data-stack.service -n 100
```

### Log Analysis

```bash
# Show logs from today only
journalctl -u local-data-stack.service --since today

# Show logs from last 2 hours
journalctl -u local-data-stack.service --since "2 hours ago"

# Show logs between dates
journalctl -u local-data-stack.service --since "2026-02-20" --until "2026-02-27"

# Export logs to file
journalctl -u local-data-stack.service > pipeline_logs.txt

# Show logs with priority ERROR and above
journalctl -u local-data-stack.service -p err
```

## Scheduling Options

### Change Execution Time

Edit `local-data-stack.timer` and modify `OnCalendar`:

```ini
# Every day at 2 AM
OnCalendar=*-*-* 02:00:00

# Every Monday at 6 AM
OnCalendar=Mon *-*-* 06:00:00

# Every 6 hours
OnCalendar=0/6:00:00

# Weekdays only at 6 AM
OnCalendar=Mon-Fri *-*-* 06:00:00
```

After changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart local-data-stack.timer
```

### Multiple Schedules

Run at multiple times by adding multiple `OnCalendar` lines:

```ini
[Timer]
OnCalendar=*-*-* 06:00:00  # 6 AM
OnCalendar=*-*-* 18:00:00  # 6 PM
```

## Troubleshooting

### Timer Not Running

```bash
# Check if timer is active
systemctl is-active local-data-stack.timer

# Check if timer is enabled
systemctl is-enabled local-data-stack.timer

# View timer logs
journalctl -u local-data-stack.timer
```

### Service Failing

```bash
# View detailed service status
systemctl status local-data-stack.service -l

# Check last 50 lines of logs
journalctl -u local-data-stack.service -n 50

# Test service manually
sudo systemctl start local-data-stack.service
journalctl -u local-data-stack.service -f
```

### Permission Errors

Ensure `datapipeline` user has access:

```bash
# Check ownership
ls -la /Users/flucido/projects/local-data-stack

# Fix ownership if needed
sudo chown -R datapipeline:datapipeline /Users/flucido/projects/local-data-stack

# Verify .env file exists and is readable
sudo -u datapipeline cat /Users/flucido/projects/local-data-stack/.env
```

### Memory/Resource Limits

If pipeline is killed due to memory:

```bash
# Check OOM (Out of Memory) kills
journalctl -u local-data-stack.service | grep -i "memory"

# Increase MemoryMax in service file
sudo nano /etc/systemd/system/local-data-stack.service
# Change: MemoryMax=8G

sudo systemctl daemon-reload
```

## Monitoring

### Check Next Execution

```bash
# Show when timer will next trigger
systemctl list-timers local-data-stack.timer
```

Output:
```
NEXT                          LEFT       LAST                          PASSED   UNIT                        ACTIVATES
Wed 2026-02-27 06:00:00 PST   9h left    Tue 2026-02-26 06:00:23 PST   14h ago  local-data-stack.timer      local-data-stack.service
```

### Execution History

```bash
# View all past executions
journalctl -u local-data-stack.service --since "1 month ago" | grep "Started\|Stopped"
```

### Performance Metrics

```bash
# View service resource usage
systemctl status local-data-stack.service

# Detailed resource usage
systemd-cgtop -m local-data-stack.service
```

## Integration with Monitoring

### Prometheus Node Exporter

Export systemd metrics for Prometheus:

```bash
# Install node_exporter with systemd collector
# metrics available at http://localhost:9100/metrics

# Query metrics:
# systemd_unit_state{name="local-data-stack.service"}
# systemd_timer_last_trigger_seconds{name="local-data-stack.timer"}
```

### Email Notifications

Install `mailx` and configure OnFailure notification:

```ini
# Add to [Service] section
OnFailure=status-email-user@%n.service

# Create email notification service
sudo nano /etc/systemd/system/status-email-user@.service
```

### Slack Notifications

Add to service `ExecStopPost`:

```ini
ExecStopPost=/usr/local/bin/notify-slack.sh "Pipeline completed with status: $EXIT_STATUS"
```

## Best Practices

1. **Test before enabling**: Run manually with `systemctl start` before enabling timer
2. **Monitor logs**: Set up log rotation and retention policies
3. **Resource limits**: Always set MemoryMax and CPUQuota to prevent runaway processes
4. **Persistent timer**: Use `Persistent=true` to catch up missed runs
5. **Randomization**: Use `RandomizedDelaySec` to avoid exact-time spikes
6. **Security**: Run as dedicated user with minimal permissions

## Uninstallation

```bash
# Stop and disable timer
sudo systemctl stop local-data-stack.timer
sudo systemctl disable local-data-stack.timer

# Remove files
sudo rm /etc/systemd/system/local-data-stack.service
sudo rm /etc/systemd/system/local-data-stack.timer

# Reload daemon
sudo systemctl daemon-reload

# Remove user (optional)
sudo userdel datapipeline
```

## See Also

- [systemd.timer documentation](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [systemd.service documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- Main project documentation: `/Users/flucido/projects/local-data-stack/automation/cron/README.md`
