# OSS Framework Setup Guide

## Prerequisites

### System Requirements

**Minimum**:
- **OS**: Ubuntu 20.04+, Debian 11+, or Windows 10/11 with WSL2
- **RAM**: 16GB
- **CPU**: 4 cores
- **Storage**: 250GB available
- **Network**: Internet connection for initial setup

**Recommended**:
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 32GB+
- **CPU**: 8+ cores
- **Storage**: 500GB+ SSD
- **Network**: 100 Mbps+ for data ingestion

### Software Dependencies

1. **Docker** (v20.10+)
2. **Docker Compose** (v2.0+)
3. **Python** (3.10+)
4. **Git** (v2.30+)
5. **Optional**: tmux or screen for long-running processes

## Installation Steps

### Step 1: Install Docker

#### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

#### Windows (WSL2)
```powershell
# Install WSL2
wsl --install

# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# Enable WSL2 integration in Docker Desktop settings
```

### Step 2: Install Python and Dependencies

```bash
# Install Python 3.10+
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# Verify installation
python3 --version  # Should be 3.10 or higher
```

### Step 3: Clone Repository

```bash
# Clone the repository
git clone https://github.com/flucido/openedDataEstate.git

# Navigate to OSS Framework directory
cd openedDataEstate/oss_framework

# Verify structure
ls -la
# Expected output:
# config/
# data/
# dbt/
# docker-compose.yml
# notebooks/
# requirements.txt
# scripts/
```

### Step 4: Configure Environment

```bash
# Create .env file for sensitive configuration
cat > .env << EOF
# DuckDB Configuration
DUCKDB_PATH=/data/oea.duckdb
DUCKDB_MEMORY_LIMIT=16GB
DUCKDB_THREADS=8

# Pseudonymization Salt (CHANGE THIS!)
PSEUDONYM_SALT=$(openssl rand -hex 32)

# Data Lake Paths
STAGE1_PATH=/data/stage1
STAGE2_PATH=/data/stage2
STAGE3_PATH=/data/stage3

# Metabase Configuration
MB_DB_FILE=/data/oea.duckdb
MB_ENCRYPTION_SECRET_KEY=$(openssl rand -hex 32)

# Dagster Configuration
DAGSTER_HOME=/opt/dagster/dagster_home

# Optional: External Data Sources
SIS_API_URL=https://sis.example.com/api
SIS_API_KEY=your_api_key_here
LMS_API_URL=https://lms.example.com/api
LMS_API_KEY=your_api_key_here
EOF

# Secure the .env file
chmod 600 .env

# Load environment variables
source .env
```

### Step 5: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installations
duckdb --version
dbt --version
```

### Step 6: Start Docker Services

```bash
# Start all services in background
docker compose up -d

# Check service status
docker compose ps

# Expected output:
# NAME                IMAGE                       STATUS              PORTS
# oea_duckdb          duckdb:latest              Up                  
# oea_jupyter         jupyter/scipy-notebook      Up                  0.0.0.0:8888->8888/tcp
# oea_metabase        metabase/metabase          Up                  0.0.0.0:3000->3000/tcp
# oea_dagster         dagster/dagster            Up                  0.0.0.0:3001->3000/tcp

# View logs
docker compose logs -f

# Stop services when needed
docker compose down
```

### Step 7: Configure dbt

```bash
# Navigate to dbt directory
cd dbt

# Create profiles.yml for DuckDB connection
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << EOF
oea_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/oea.duckdb
      schema: main
      threads: 8
      extensions:
        - delta
        - parquet
    prod:
      type: duckdb
      path: ../data/oea.duckdb
      schema: main
      threads: 8
      read_only: false
      extensions:
        - delta
        - parquet
EOF

# Test dbt connection
dbt debug

# Expected output:
# All checks passed!

# Return to main directory
cd ..
```

### Step 8: Verify Installation

```bash
# Create verification script
cat > verify_setup.sh << 'EOF'
#!/bin/bash

echo "=== OSS Framework Setup Verification ==="
echo ""

# Check Docker
echo "1. Checking Docker..."
docker --version && echo "✓ Docker installed" || echo "✗ Docker not found"

# Check Docker Compose
echo "2. Checking Docker Compose..."
docker compose version && echo "✓ Docker Compose installed" || echo "✗ Docker Compose not found"

# Check Python
echo "3. Checking Python..."
python3 --version && echo "✓ Python installed" || echo "✗ Python not found"

# Check DuckDB
echo "4. Checking DuckDB..."
python3 -c "import duckdb; print(f'✓ DuckDB {duckdb.__version__} installed')" 2>/dev/null || echo "✗ DuckDB not found"

# Check dbt
echo "5. Checking dbt..."
dbt --version && echo "✓ dbt installed" || echo "✗ dbt not found"

# Check Docker services
echo "6. Checking Docker services..."
docker compose ps | grep -q "Up" && echo "✓ Docker services running" || echo "✗ Docker services not running"

# Check data directories
echo "7. Checking data lake structure..."
[ -d "data/stage1" ] && [ -d "data/stage2" ] && [ -d "data/stage3" ] && echo "✓ Data lake directories exist" || echo "✗ Data lake directories missing"

# Check web services
echo "8. Checking web services..."
curl -s http://localhost:3000 > /dev/null && echo "✓ Metabase accessible" || echo "✗ Metabase not accessible"
curl -s http://localhost:3001 > /dev/null && echo "✓ Dagster accessible" || echo "✗ Dagster not accessible"
curl -s http://localhost:8888 > /dev/null && echo "✓ JupyterLab accessible" || echo "✗ JupyterLab not accessible"

echo ""
echo "=== Verification Complete ==="
EOF

chmod +x verify_setup.sh
./verify_setup.sh
```

## Initial Configuration

### Configure Metabase

1. **Access Metabase**: Open http://localhost:3000 in your browser

2. **Initial Setup**:
   - Language: English
   - Create admin account:
     - Email: admin@yourdistinct.edu
     - Password: (secure password)

3. **Add DuckDB Database**:
   - Click "Add a database"
   - Database type: DuckDB
   - Display name: OEA Data Lake
   - Database file: `/data/oea.duckdb`
   - Click "Save"

4. **Test Connection**:
   - Go to "Browse Data"
   - Select "OEA Data Lake"
   - You should see available tables

### Configure Dagster

1. **Access Dagster**: Open http://localhost:3001 in your browser

2. **Verify Setup**:
   - You should see the Dagster UI
   - Navigate to "Assets" to see defined data assets
   - Check "Runs" for pipeline execution history

### Configure JupyterLab

1. **Access JupyterLab**: Open http://localhost:8888

2. **Get Token**:
```bash
# Get Jupyter token from logs
docker compose logs jupyter | grep "token="
# Example output: http://127.0.0.1:8888/?token=abc123...
```

3. **Test DuckDB Connection**:
   - Create new notebook
   - Run test query:
```python
import duckdb

con = duckdb.connect('/data/oea.duckdb')
print("DuckDB Version:", con.execute("SELECT version()").fetchone()[0])
con.close()
```

## Load Sample Data

### Download Sample Datasets

```bash
# Create sample data directory
mkdir -p data/samples

# Download sample SIS data (modify URL to your actual source)
curl -o data/samples/sample_students.csv \
  https://example.com/sample_students.csv

# Or create synthetic data
python3 << EOF
import pandas as pd
import numpy as np

# Generate 1000 sample students
np.random.seed(42)
students = pd.DataFrame({
    'student_id': range(1, 1001),
    'first_name': [f'Student{i}' for i in range(1, 1001)],
    'last_name': [f'Last{i}' for i in range(1, 1001)],
    'grade_level': np.random.choice([9, 10, 11, 12], 1000),
    'school_name': np.random.choice(['High School A', 'High School B'], 1000),
    'enrollment_status': 'Active',
    'enrollment_date': '2025-09-01'
})

students.to_csv('data/samples/sample_students.csv', index=False)
print("✓ Generated sample_students.csv with 1000 students")
EOF
```

### Ingest Sample Data

```bash
# Run sample ingestion script
python3 scripts/ingest_sample.py

# Expected output:
# [INFO] Starting ingestion: sample_students.csv
# [INFO] Read 1000 rows
# [INFO] Writing to Stage 1: data/stage1/transactional/samples/students/2026-01-26/
# [INFO] ✓ Ingestion complete
```

### Transform Sample Data

```bash
# Run dbt models
cd dbt
dbt run

# Expected output:
# Running with dbt=1.6.0
# Found 3 models, 0 tests, 0 snapshots
# 
# 21:30:00 | 1 of 3 START sql table model main.stg_students .......................... [RUN]
# 21:30:01 | 1 of 3 OK created sql table model main.stg_students ..................... [SUCCESS in 0.5s]
# 21:30:01 | 2 of 3 START sql table model main.dim_students .......................... [RUN]
# 21:30:02 | 2 of 3 OK created sql table model main.dim_students ..................... [SUCCESS in 0.7s]
# 21:30:02 | 3 of 3 START sql table model main.fact_enrollment ....................... [RUN]
# 21:30:03 | 3 of 3 OK created sql table model main.fact_enrollment .................. [SUCCESS in 0.4s]
# 
# Completed successfully

# Run dbt tests
dbt test

# Return to main directory
cd ..
```

### Verify Data in Metabase

1. Go to http://localhost:3000
2. Click "Browse Data"
3. Select "OEA Data Lake"
4. You should see tables:
   - `stg_students`
   - `dim_students`
   - `fact_enrollment`
5. Click any table to preview data

## First Dashboard

### Create Sample Query in Metabase

1. Click "New" → "Question"
2. Choose "Native Query"
3. Enter SQL:
```sql
SELECT 
    grade_level,
    COUNT(*) as student_count,
    school_name
FROM dim_students
GROUP BY grade_level, school_name
ORDER BY grade_level, school_name
```
4. Click "Visualize"
5. Change visualization to "Bar Chart"
6. Save as "Student Enrollment by Grade"

### Create Dashboard

1. Click "New" → "Dashboard"
2. Name: "Student Overview"
3. Add questions:
   - Student Enrollment by Grade
   - (Add more as you create them)
4. Arrange and resize as desired
5. Save dashboard

## Troubleshooting

### Docker Services Won't Start

**Issue**: `docker compose up` fails

**Solutions**:
```bash
# Check Docker daemon
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check port conflicts
sudo netstat -tulpn | grep -E '(3000|3001|8888)'

# View detailed logs
docker compose logs
```

### DuckDB Connection Failed

**Issue**: Cannot connect to DuckDB from Python/dbt

**Solutions**:
```bash
# Check file permissions
ls -la data/oea.duckdb

# Ensure DuckDB file is not locked
lsof data/oea.duckdb

# Recreate database
rm data/oea.duckdb
duckdb data/oea.duckdb << EOF
CREATE TABLE test (id INT);
DROP TABLE test;
.quit
EOF
```

### Metabase Can't See Tables

**Issue**: Database connected but no tables visible

**Solutions**:
```bash
# Sync database schema in Metabase
# Settings → Admin → Databases → OEA Data Lake → Sync database schema now

# Verify tables exist in DuckDB
duckdb data/oea.duckdb << EOF
SHOW TABLES;
.quit
EOF
```

### dbt Models Fail

**Issue**: `dbt run` produces errors

**Solutions**:
```bash
# Check dbt configuration
dbt debug

# View detailed error logs
dbt run --debug

# Validate SQL syntax
cd dbt/models
# Open problematic .sql file and test in DuckDB directly
```

### Insufficient Memory

**Issue**: "Out of memory" errors during queries

**Solutions**:
```bash
# Increase DuckDB memory limit
# Edit: dbt/profiles.yml
# Add under connection config:
#   memory_limit: '16GB'

# Or set in .env:
echo "DUCKDB_MEMORY_LIMIT=16GB" >> .env

# Restart services
docker compose down && docker compose up -d
```

### Slow Query Performance

**Issue**: Queries taking too long

**Solutions**:
```python
# Enable DuckDB profiling
import duckdb
con = duckdb.connect('data/oea.duckdb')

con.execute("SET enable_profiling='query_tree'")
con.execute("SET profiling_mode='detailed'")

# Run your slow query
result = con.execute("SELECT ...").fetchdf()

# View profile
profile = con.execute("SELECT * FROM duckdb_query_profile()").fetchdf()
print(profile)
```

## Production Deployment

### Hardening Checklist

- [ ] Change all default passwords
- [ ] Regenerate `PSEUDONYM_SALT` (in .env)
- [ ] Set up disk encryption (LUKS/BitLocker)
- [ ] Configure firewall rules (block external access)
- [ ] Enable Docker log rotation
- [ ] Set up automated backups
- [ ] Configure monitoring and alerting
- [ ] Document recovery procedures
- [ ] Test backup restore process
- [ ] Review and restrict file permissions

### Backup Configuration

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/oss_framework"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup data lake
echo "Backing up data lake..."
rsync -av --progress data/ "$BACKUP_DIR/$DATE/data/"

# Backup DuckDB database
echo "Backing up DuckDB..."
cp data/oea.duckdb "$BACKUP_DIR/$DATE/oea.duckdb"

# Backup configurations
echo "Backing up configs..."
tar -czf "$BACKUP_DIR/$DATE/configs.tar.gz" config/ dbt/ .env

# Remove backups older than 30 days
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +

echo "Backup complete: $BACKUP_DIR/$DATE"
EOF

chmod +x backup.sh

# Schedule daily backups with cron
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/oss_framework/backup.sh") | crontab -
```

### Monitoring Setup

```bash
# Install monitoring tools
pip install prometheus-client psutil

# Create monitoring script
cat > monitor.py << 'EOF'
from prometheus_client import start_http_server, Gauge
import psutil
import time

# Define metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage')
disk_usage = Gauge('disk_usage_percent', 'Disk usage percentage')

def collect_metrics():
    cpu_usage.set(psutil.cpu_percent(interval=1))
    memory_usage.set(psutil.virtual_memory().percent)
    disk_usage.set(psutil.disk_usage('/').percent)

if __name__ == '__main__':
    start_http_server(8000)
    while True:
        collect_metrics()
        time.sleep(30)
EOF

# Run monitor (or add to systemd)
python monitor.py &
```

## Next Steps

1. **Learn dbt**: [dbt Guide](dbt_guide.md)
2. **Build Pipelines**: [Ingestion Guide](ingestion_guide.md)
3. **Explore Data**: [DuckDB Guide](duckdb_guide.md)
4. **Create Dashboards**: [Metabase Documentation](https://www.metabase.com/docs/)
5. **Deploy to Production**: [Deployment Guide](../developer/deployment_guide.md)

## Support

- **Documentation**: [Main Docs](../README.md)
- **Issues**: [GitHub Issues](https://github.com/flucido/openedDataEstate/issues)
- **Community**: [GitHub Discussions](https://github.com/flucido/openedDataEstate/discussions)
