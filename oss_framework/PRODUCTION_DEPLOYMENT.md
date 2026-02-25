# Production Deployment & Infrastructure Guide

## Overview

This document provides step-by-step instructions for deploying the complete analytics platform to production Kubernetes with high availability, disaster recovery, and monitoring.

## Deployment Architecture

### Multi-Cloud Support

```
┌─────────────────────────────────────────────────────────────────┐
│                     Production Deployment                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AWS EKS (Recommended)    Azure AKS        GCP GKE             │
│  ├─ 3 AZs                 ├─ 3 Regions     ├─ 3 Zones          │
│  ├─ Auto-scaling 3-10     ├─ Node pool     ├─ Node pool        │
│  ├─ EBS volumes (100GB)   ├─ Disk (100GB)  ├─ Persistent (100G)│
│  ├─ RDS PostgreSQL        ├─ PostgreSQL    ├─ Cloud SQL        │
│  └─ S3 backups            └─ Blob backups  └─ GCS backups      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Pre-Deployment Checklist

### Infrastructure Prerequisites

- [ ] Kubernetes cluster created (1.24+) with 3+ nodes
- [ ] kubectl configured and authenticated
- [ ] Persistent volume provisioner configured
- [ ] Load balancer configured
- [ ] SSL/TLS certificates generated
- [ ] Secret backend configured (Secrets Manager / Key Vault / KMS)
- [ ] Container registry authenticated (Docker Hub / GHCR / ECR)

### Code & Data Prerequisites

- [ ] dbt project tested locally (all 34 models passing)
- [ ] Docker images built and pushed to registry
- [ ] Terraform infrastructure provisioned
- [ ] Database backup verified
- [ ] dbt profiles.yml configured for production database

### Organizational Prerequisites

- [ ] Change control process approved
- [ ] Incident response team briefed
- [ ] Rollback procedure documented and tested
- [ ] Monitoring and alerting configured
- [ ] Support team trained on operational procedures

## Step 1: Kubernetes Cluster Setup

### 1.1 Create Namespace & Secrets

```bash
#!/bin/bash
# Deploy to production

# 1. Create namespace
kubectl create namespace oea-production
kubectl config set-context --current --namespace=oea-production

# 2. Create secrets for database credentials
kubectl create secret generic db-credentials \
  --from-literal=postgres-user=oea_admin \
  --from-literal=postgres-password=$(openssl rand -base64 32) \
  --from-literal=postgres-host=postgres.oea-production.svc.cluster.local \
  --from-literal=postgres-port=5432 \
  --from-literal=postgres-db=oea

# 3. Create secrets for application keys
kubectl create secret generic app-keys \
  --from-literal=metabase-key=$(openssl rand -base64 32) \
  --from-literal=jwt-secret=$(openssl rand -base64 32) \
  --from-literal=api-key=$(openssl rand -base64 32)

# 4. Create SSL/TLS certificate
kubectl create secret tls tls-cert \
  --cert=path/to/cert.crt \
  --key=path/to/key.key

# 5. Verify secrets created
kubectl get secrets -n oea-production
```

### 1.2 Create Storage Classes

```yaml
# PersistentVolume storage class
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
  namespace: oea-production
provisioner: kubernetes.io/aws-ebs  # or 'disk.csi.azure.com' or 'pd.csi.storage.gke.io'
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  replication-type: regional-pd  # for GCP
allowVolumeExpansion: true
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: backup-storage
  namespace: oea-production
provisioner: kubernetes.io/aws-ebs
parameters:
  type: st1  # throughput optimized
  iops: "500"
```

### 1.3 Deploy PostgreSQL

```yaml
# PostgreSQL StatefulSet - High Availability
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: oea-production
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-password
        - name: POSTGRES_DB
          value: oea
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        - name: postgres-config
          mountPath: /etc/postgresql/postgresql.conf
          subPath: postgresql.conf
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U $POSTGRES_USER
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U $POSTGRES_USER
          initialDelaySeconds: 5
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
---
# PostgreSQL Service
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: oea-production
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

### 1.4 Deploy DuckDB Service

```yaml
# DuckDB Deployment with shared storage
apiVersion: apps/v1
kind: Deployment
metadata:
  name: duckdb
  namespace: oea-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: duckdb
  template:
    metadata:
      labels:
        app: duckdb
    spec:
      containers:
      - name: duckdb
        image: mcr.microsoft.com/python:3.11-slim
        command: ["python", "-m", "duckdb.cli"]
        ports:
        - containerPort: 5433
          name: duckdb
        volumeMounts:
        - name: duckdb-data
          mountPath: /data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      volumes:
      - name: duckdb-data
        persistentVolumeClaim:
          claimName: duckdb-data-pvc
---
# DuckDB PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: duckdb-data-pvc
  namespace: oea-production
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi
---
# DuckDB Service
apiVersion: v1
kind: Service
metadata:
  name: duckdb
  namespace: oea-production
spec:
  selector:
    app: duckdb
  ports:
  - port: 5433
    targetPort: 5433
  type: ClusterIP
```

## Step 2: Deploy dbt & Orchestration

### 2.1 Create dbt ConfigMap

```yaml
# dbt project configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: dbt-config
  namespace: oea-production
data:
  profiles.yml: |
    oea:
      outputs:
        production:
          type: duckdb
          path: '/data/oea.duckdb'
          threads: 8
          timeout_seconds: 300
      target: production
  
  dbt_project.yml: |
    name: 'oea_student_analytics'
    version: '1.0.0'
    config-version: 2
    
    profile: 'oea'
    model-paths: ["models"]
    test-paths: ["tests"]
    data-paths: ["data"]
    
    target-path: "target"
    clean-targets:
      - "target"
      - "dbt_packages"
    
    models:
      oea_student_analytics:
        materialized: view
        staging:
          materialized: view
        mart_analytics:
          materialized: view
```

### 2.2 Deploy dbt CronJob for Daily Refresh

```yaml
# Kubernetes CronJob for dbt orchestration
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dbt-refresh
  namespace: oea-production
spec:
  schedule: "0 2 * * *"  # 2 AM UTC daily
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 3
      template:
        spec:
          serviceAccountName: dbt-runner
          containers:
          - name: dbt
            image: fishtownanalytics/dbt:1.5.0-py3.11
            command:
            - /bin/bash
            - -c
            - |
              cd /dbt
              dbt run --profile oea --target production --threads 8
              dbt test --profile oea --target production
              echo "dbt run completed at $(date)"
            env:
            - name: DBT_PROFILES_DIR
              value: /root/.dbt
            volumeMounts:
            - name: dbt-config
              mountPath: /root/.dbt
            - name: dbt-project
              mountPath: /dbt
            - name: dbt-data
              mountPath: /data
            resources:
              requests:
                memory: "4Gi"
                cpu: "2000m"
              limits:
                memory: "8Gi"
                cpu: "4000m"
          - name: notification
            image: curlimages/curl:latest
            command:
            - /bin/sh
            - -c
            - |
              if [ $? -eq 0 ]; then
                curl -X POST -H 'Content-type: application/json' \
                  --data '{"text":"✅ dbt refresh completed successfully at '$(date)'"}' \
                  $SLACK_WEBHOOK_URL
              else
                curl -X POST -H 'Content-type: application/json' \
                  --data '{"text":"❌ dbt refresh failed at '$(date)'"}' \
                  $SLACK_WEBHOOK_URL
              fi
            env:
            - name: SLACK_WEBHOOK_URL
              valueFrom:
                secretKeyRef:
                  name: slack-config
                  key: webhook-url
          restartPolicy: OnFailure
          volumes:
          - name: dbt-config
            configMap:
              name: dbt-config
          - name: dbt-project
            emptyDir: {}
          - name: dbt-data
            persistentVolumeClaim:
              claimName: duckdb-data-pvc
```

## Step 3: Deploy Metabase

### 3.1 Metabase Deployment

```yaml
# Metabase Deployment - High Availability
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metabase
  namespace: oea-production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: metabase
  template:
    metadata:
      labels:
        app: metabase
    spec:
      serviceAccountName: metabase
      containers:
      - name: metabase
        image: metabase/metabase:latest
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: MB_DB_TYPE
          value: postgres
        - name: MB_DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-host
        - name: MB_DB_PORT
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-port
        - name: MB_DB_DBNAME
          value: metabase
        - name: MB_DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-user
        - name: MB_DB_PASS
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-password
        - name: MB_ENCRYPTION_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-keys
              key: metabase-key
        - name: MB_EMAIL_SMTP_HOST
          value: smtp.sendgrid.net
        - name: MB_EMAIL_SMTP_PORT
          value: "587"
        - name: MB_EMAIL_SMTP_USERNAME
          value: apikey
        - name: MB_EMAIL_SMTP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: smtp-credentials
              key: password
        - name: JAVA_TOOL_OPTIONS
          value: "-Xmx2g -Xms1g"
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "3Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
---
# Metabase Service
apiVersion: v1
kind: Service
metadata:
  name: metabase
  namespace: oea-production
spec:
  selector:
    app: metabase
  ports:
  - port: 3000
    targetPort: 3000
    name: http
  type: LoadBalancer
---
# Metabase HPA (Auto-scaling)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: metabase-hpa
  namespace: oea-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: metabase
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Step 4: Backup & Disaster Recovery

### 4.1 Automated Backup CronJob

```yaml
# Daily backup CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: oea-production
spec:
  schedule: "0 3 * * *"  # 3 AM UTC daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/bash
            - -c
            - |
              #!/bin/bash
              set -e
              BACKUP_DIR="/backups"
              TIMESTAMP=$(date +%Y%m%d_%H%M%S)
              BACKUP_FILE="$BACKUP_DIR/oea_backup_$TIMESTAMP.sql.gz"
              
              echo "Starting backup: $BACKUP_FILE"
              pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB \
                | gzip > $BACKUP_FILE
              
              # Upload to S3/GCS/Blob
              aws s3 cp $BACKUP_FILE s3://oea-backups/
              
              # Retain last 90 days of backups
              find $BACKUP_DIR -name "oea_backup_*.sql.gz" -mtime +90 -delete
              
              echo "Backup completed: $BACKUP_FILE"
            env:
            - name: POSTGRES_HOST
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: postgres-host
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: postgres-user
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: postgres-password
            - name: POSTGRES_DB
              value: oea
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
---
# Backup PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backup-pvc
  namespace: oea-production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: backup-storage
  resources:
    requests:
      storage: 500Gi
```

## Step 5: Monitoring & Alerting

See separate MONITORING.md for Prometheus/Grafana/Loki setup.

## Step 6: Deployment Validation

### 6.1 Smoke Tests

```bash
#!/bin/bash
# Post-deployment validation

echo "=== Deployment Validation ==="

# 1. Check pod status
echo "Checking pod status..."
kubectl get pods -n oea-production
kubectl wait --for=condition=ready pod \
  -l app=postgres,app=duckdb,app=metabase \
  -n oea-production \
  --timeout=300s

# 2. Test database connectivity
echo "Testing database connectivity..."
kubectl run -it --rm debug \
  --image=postgres:15-alpine \
  --restart=Never \
  -- psql -h postgres.oea-production.svc.cluster.local \
    -U $DB_USER \
    -d oea \
    -c "SELECT COUNT(*) FROM information_schema.tables;"

# 3. Test Metabase health
echo "Testing Metabase health..."
METABASE_LB=$(kubectl get svc metabase -n oea-production \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -s http://$METABASE_LB:3000/api/health | jq .

# 4. Verify data pipeline
echo "Verifying data pipeline..."
kubectl exec -it postgres-0 -n oea-production \
  -- psql -U $DB_USER -d oea \
    -c "SELECT COUNT(*) FROM v_chronic_absenteeism_risk;"

# 5. Check monitoring stack
echo "Verifying monitoring..."
kubectl get pods -n monitoring
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

## Rollback Procedure

### Emergency Rollback

```bash
#!/bin/bash
# Immediate rollback to previous deployment

# 1. Identify previous deployment
kubectl rollout history deployment/metabase -n oea-production

# 2. Rollback to previous version
kubectl rollout undo deployment/metabase -n oea-production --to-revision=N

# 3. Verify rollback
kubectl rollout status deployment/metabase -n oea-production

# 4. Restore database from backup
./scripts/restore-database.sh <backup-file>

# 5. Run health checks
./scripts/health-checks.sh
```

## Next Steps

1. Week 5: Complete infrastructure setup and testing
2. Week 6: Deploy monitoring and alerting
3. Week 7: Execute production deployment
4. Week 8: Go-live and production support

---

For more details, see:
- `oss_framework/k8s/README.md` - Kubernetes deployment guide
- `oss_framework/terraform/README.md` - Infrastructure-as-Code documentation
- `MONITORING.md` - Monitoring and alerting setup
