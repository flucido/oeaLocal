# macOS launchd Installation and Management Guide

This directory contains a launchd plist file for production deployment of the
Local Data Stack analytics pipeline on macOS.

## Quick Start

```bash
# 1. Copy plist to LaunchAgents directory
cp com.localdata.analytics-pipeline.plist ~/Library/LaunchAgents/

# 2. Load the service
launchctl load ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist

# 3. Verify it's loaded
launchctl list | grep com.localdata.analytics-pipeline
```

## Files

- **com.localdata.analytics-pipeline.plist** - launchd configuration file

## Configuration

### Schedule

Current schedule: **Daily at 6:00 AM**

To change the schedule, edit the `StartCalendarInterval` section:

```xml
<!-- Daily at 2 AM -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>2</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Multiple Schedules

Run at multiple times using an array:

```xml
<key>StartCalendarInterval</key>
<array>
    <!-- 6 AM -->
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <!-- 6 PM -->
    <dict>
        <key>Hour</key>
        <integer>18</integer>
        <integer>0</integer>
    </dict>
</array>
```

### Weekday-Only Schedule

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>
    <integer>1</integer>  <!-- Monday -->
    <key>Hour</key>
    <integer>6</integer>
</dict>
```

Weekday values:
- 0 = Sunday
- 1 = Monday
- 2 = Tuesday
- 3 = Wednesday
- 4 = Thursday
- 5 = Friday
- 6 = Saturday

### Resource Limits

Current limits (4GB memory, 2 hours CPU time):

```xml
<key>SoftResourceLimits</key>
<dict>
    <key>MemoryLimit</key>
    <integer>4294967296</integer>  <!-- 4GB in bytes -->
    <key>CPUTime</key>
    <integer>7200</integer>  <!-- 2 hours in seconds -->
</dict>
```

## Management Commands

### Loading and Unloading

```bash
# Load service (enable scheduling)
launchctl load ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist

# Unload service (disable scheduling)
launchctl unload ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist

# Reload after config changes
launchctl unload ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
launchctl load ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
```

### Status and Debugging

```bash
# Check if service is loaded
launchctl list | grep com.localdata.analytics-pipeline

# View service details
launchctl list com.localdata.analytics-pipeline

# View logs
tail -f ~/Library/Logs/local-data-stack/launchd.log
tail -f ~/Library/Logs/local-data-stack/launchd_error.log

# Alternative: Use Console app
open -a Console  # Filter for "localdata"
```

### Manual Execution

```bash
# Trigger job manually (outside of schedule)
launchctl start com.localdata.analytics-pipeline

# Stop running job
launchctl stop com.localdata.analytics-pipeline
```

## Log Locations

Logs are written to:
- **Standard output**: `~/Library/Logs/local-data-stack/launchd.log`
- **Standard error**: `~/Library/Logs/local-data-stack/launchd_error.log`

Create log directory if it doesn't exist:

```bash
mkdir -p ~/Library/Logs/local-data-stack
```

## Troubleshooting

### Service Not Running

```bash
# Check if loaded
launchctl list | grep com.localdata

# Check for errors in system log
log show --predicate 'processImagePath contains "launchd"' --last 1h | grep localdata

# Validate plist syntax
plutil -lint ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist
```

### Permission Errors

Ensure the shell script is executable:

```bash
chmod +x /Users/flucido/projects/local-data-stack/scripts/schedule_pipeline.sh
```

### Path Issues

launchd has a limited PATH. If commands aren't found, specify full paths:

```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>/Users/flucido/projects/local-data-stack/scripts/schedule_pipeline.sh</string>
</array>
```

### Environment Variables

Add environment variables:

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>CUSTOM_VAR</key>
    <string>value</string>
    <key>LOG_LEVEL</key>
    <string>DEBUG</string>
</dict>
```

## Advanced Configuration

### Run on Boot

```xml
<key>RunAtLoad</key>
<true/>
```

### Keep Alive (Always Running)

```xml
<key>KeepAlive</key>
<true/>
```

### Run on File Changes

Watch a directory and trigger on changes:

```xml
<key>WatchPaths</key>
<array>
    <string>/Users/flucido/projects/local-data-stack/data</string>
</array>
```

### Interval-Based (Not Calendar)

Run every N seconds (e.g., every hour = 3600 seconds):

```xml
<key>StartInterval</key>
<integer>3600</integer>
```

## Notification on Failure

Add a notification script:

```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>/Users/flucido/projects/local-data-stack/scripts/schedule_pipeline.sh || osascript -e 'display notification "Pipeline failed" with title "Local Data Stack"'</string>
</array>
```

## System-Wide Deployment

For system-wide services (requires sudo):

```bash
# Copy to LaunchDaemons instead of LaunchAgents
sudo cp com.localdata.analytics-pipeline.plist /Library/LaunchDaemons/

# Load as root
sudo launchctl load /Library/LaunchDaemons/com.localdata.analytics-pipeline.plist
```

**Differences**:
- **LaunchAgents** (`~/Library/LaunchAgents/`): Run as current user, only when user logged in
- **LaunchDaemons** (`/Library/LaunchDaemons/`): Run as root, always active (even when no user logged in)

## Monitoring

### Check Next Execution

launchd doesn't provide "next run time" like cron. Use this approach:

```bash
# View last execution time in logs
tail -n 50 ~/Library/Logs/local-data-stack/launchd.log | grep -i "started\|completed"
```

### Execution History

```bash
# View recent log entries
tail -n 100 ~/Library/Logs/local-data-stack/launchd.log

# Search for errors
grep -i "error\|failed" ~/Library/Logs/local-data-stack/launchd_error.log
```

## Uninstallation

```bash
# Unload service
launchctl unload ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist

# Remove plist file
rm ~/Library/LaunchAgents/com.localdata.analytics-pipeline.plist

# Remove logs (optional)
rm -rf ~/Library/Logs/local-data-stack
```

## Best Practices

1. **Test manually first**: Run `schedule_pipeline.sh` manually before scheduling
2. **Check logs**: Monitor logs after first scheduled run
3. **Use absolute paths**: Always specify full paths in plist
4. **Validate plist**: Use `plutil -lint` before loading
5. **Resource limits**: Always set memory and CPU limits
6. **Error handling**: Ensure script has proper error handling

## See Also

- [launchd documentation](https://www.launchd.info/)
- [Apple launchd.plist manual](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- Main project documentation: `/Users/flucido/projects/local-data-stack/automation/cron/README.md`
