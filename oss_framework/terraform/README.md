# Terraform Infrastructure-as-Code Documentation

Complete Infrastructure-as-Code (IaC) configuration for deploying the OSS Framework SIS Analytics platform across AWS, Azure, and GCP cloud providers.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Cloud Providers](#cloud-providers)
5. [Quick Start](#quick-start)
6. [AWS Deployment](#aws-deployment)
7. [Azure Deployment](#azure-deployment)
8. [GCP Deployment](#gcp-deployment)
9. [Terraform Configuration](#terraform-configuration)
10. [Outputs](#outputs)
11. [Maintenance](#maintenance)
12. [Troubleshooting](#troubleshooting)
13. [Cost Considerations](#cost-considerations)
14. [Security Best Practices](#security-best-practices)

---

## Overview

This Terraform configuration enables deployment of the OSS Framework SIS Analytics platform across multiple cloud providers with consistent architecture and best practices.

### Key Features

- **Multi-Cloud Support**: AWS EKS, Azure AKS, and GCP GKE
- **Production-Ready**: Security groups, IAM roles, RBAC, and backup policies
- **Auto-Scaling**: Horizontal pod autoscaling and node pool autoscaling
- **High Availability**: Multi-zone deployments with load balancers
- **Persistent Storage**: RDS/Cloud SQL for databases, S3/Cloud Storage for data
- **Monitoring Ready**: Compatible with Prometheus, Grafana, and cloud provider native monitoring
- **Configurable**: Environment-based variable overrides (dev/staging/prod)

### Directory Structure

```
terraform/
├── aws/
│   ├── main.tf                     # AWS provider configuration
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values
│   ├── terraform.tfvars.example    # Example configuration
│   └── eks.tf                      # Alternative EKS configuration
├── azure/
│   ├── main.tf                     # Azure provider configuration
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values
│   └── terraform.tfvars.example    # Example configuration
├── gcp/
│   ├── main.tf                     # GCP provider configuration
│   ├── variables.tf                # Input variables
│   ├── outputs.tf                  # Output values
│   └── terraform.tfvars.example    # Example configuration
└── README.md                       # This file
```

---

## Prerequisites

### Global Requirements

- **Terraform**: v1.0 or later
- **Git**: For version control
- **Environment**: Unix-like system (Linux, macOS) or Windows with WSL2

### AWS Requirements

- AWS Account with appropriate permissions
- AWS CLI v2 configured with credentials
- IAM permissions for: EKS, RDS, S3, EC2, VPC, IAM, CloudFormation
- AWS CLI configuration:
  ```bash
  aws configure
  aws sts get-caller-identity  # Verify credentials
  ```

### Azure Requirements

- Azure Subscription with owner access
- Azure CLI installed and authenticated
- Azure CLI configuration:
  ```bash
  az login
  az account show  # Verify current subscription
  az account set --subscription "SUBSCRIPTION_ID"  # If needed
  ```
- Service Principal for Terraform (recommended for CI/CD):
  ```bash
  az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/{subscriptionId}"
  ```

### GCP Requirements

- GCP Project with billing enabled
- Google Cloud SDK (gcloud CLI) installed
- GCP CLI configuration:
  ```bash
  gcloud auth application-default login
  gcloud config set project PROJECT_ID
  gcloud iam service-accounts create terraform --display-name="Terraform"
  ```
- Service Account with Owner or Editor role
- GCP APIs enabled:
  - Kubernetes Engine API
  - Compute Engine API
  - Cloud SQL API
  - Cloud Storage API

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Pipeline   │  │   Grafana    │  │  Metabase    │      │
│  │  Deployment  │  │  Deployment  │  │  Deployment  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Superset   │  │  PostgreSQL  │  │   pgAdmin    │      │
│  │  Deployment  │  │  StatefulSet │  │  Deployment  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer / Service Mesh                               │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │   RDS   │          │  Azure  │          │ Cloud   │
    │ Database│          │ Database│          │ SQL     │
    └────┬────┘          └────┬────┘          └────┬────┘
         │                    │                    │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │   S3    │          │ Storage  │          │ Cloud   │
    │ Bucket  │          │ Account  │          │ Storage │
    └─────────┘          └─────────┘          └─────────┘
```

### Component Breakdown

**Kubernetes Cluster (K8s)**
- Multi-zone high availability
- Auto-scaling node pools
- Network policies and security groups
- Load balancer for external access
- 2-5 replicas for pipeline deployments
- Persistent volumes for databases

**Relational Database**
- PostgreSQL with 100GB+ storage
- Automated backups (30+ days)
- Multi-AZ replication (production)
- SSL/TLS encryption
- Read replicas available

**Object Storage**
- S3 / Cloud Storage for data files
- Versioning enabled
- Encryption at rest
- Lifecycle policies for old data

---

## Cloud Providers

### AWS (EKS)

**Region**: us-east-1 (configurable)

**Resources**:
- EKS Cluster (Kubernetes 1.28)
- Auto Scaling Group with 2-10 nodes
- RDS PostgreSQL 16 (db.t3.medium)
- S3 bucket for data
- VPC with public/private subnets across 3 AZs
- NAT Gateways for egress
- Security Groups for network isolation
- IAM roles and policies

**Estimated Monthly Cost** (production):
- EKS Control Plane: ~$73
- EC2 (5 t3.large nodes): ~$400-600
- RDS (db.t3.large, 500GB): ~$600-800
- Data Transfer: Variable
- **Total**: ~$1,100-1,500/month

### Azure (AKS)

**Region**: eastus (configurable)

**Resources**:
- AKS Cluster (Kubernetes 1.28+)
- 3-10 nodes (Standard_D2s_v3)
- Database for PostgreSQL (B_Gen5_2)
- Azure Storage Account
- Resource Group
- Virtual Network with subnets
- Network Security Groups
- Managed Identity

**Estimated Monthly Cost** (production):
- AKS Cluster: ~$0 (included)
- VM Instances (5 D4s_v3): ~$700-900
- Database (GP tier): ~$300-400
- Storage: ~$20-50
- **Total**: ~$1,000-1,300/month

### GCP (GKE)

**Region**: us-central1 (configurable)

**Resources**:
- GKE Cluster (Kubernetes 1.28+)
- Node pool with preemptible/standard nodes
- Cloud SQL PostgreSQL 15
- Cloud Storage bucket
- VPC with secondary ranges
- Cloud NAT for egress
- Firewall rules

**Estimated Monthly Cost** (production):
- GKE Cluster: ~$73 (control plane)
- Compute (5 n1-standard-2): ~$200-300 (preemptible)
- Cloud SQL (db-custom tier): ~$200-300
- Storage: ~$20-30
- **Total**: ~$500-700/month (with preemptible nodes)

---

## Quick Start

### 1. Clone Repository

```bash
cd /path/to/openedDataEstate
git clone <repository>
cd oss_framework/terraform
```

### 2. Choose Cloud Provider

```bash
# AWS
cd aws

# OR Azure
cd azure

# OR GCP
cd gcp
```

### 3. Configure Variables

```bash
# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars  # or your preferred editor
```

### 4. Initialize Terraform

```bash
terraform init
```

This will:
- Download required providers
- Set up remote state backend
- Initialize modules

### 5. Review Plan

```bash
terraform plan
```

Carefully review the output to ensure all resources match your expectations.

### 6. Apply Configuration

```bash
terraform apply
```

Review the plan and type `yes` to proceed. This typically takes 10-30 minutes depending on the provider.

### 7. Configure kubectl

After deployment, configure kubectl:

```bash
# AWS
aws eks update-kubeconfig --region us-east-1 --name sis-analytics

# Azure
az aks get-credentials --resource-group sis-analytics-rg --name sis-analytics

# GCP
gcloud container clusters get-credentials sis-analytics-dev --zone us-central1-a
```

### 8. Verify Deployment

```bash
kubectl get nodes
kubectl get pods -n sis-analytics
```

---

## AWS Deployment

### AWS-Specific Configuration

**Provider Version**: ~> 5.0

**State Backend**: S3 with DynamoDB locks (requires pre-configuration)

### Step 1: Pre-Setup (One-Time)

Create the Terraform state S3 bucket and DynamoDB table:

```bash
# Create S3 bucket for state
aws s3api create-bucket \
  --bucket sis-analytics-terraform-state \
  --region us-east-1 \
  --create-bucket-configuration LocationConstraint=us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket sis-analytics-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket sis-analytics-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=2,WriteCapacityUnits=2 \
  --region us-east-1
```

### Step 2: Configure AWS Variables

```bash
cd oss_framework/terraform/aws
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region           = "us-east-1"
environment          = "dev"
cluster_name         = "sis-analytics"
cluster_version      = "1.28"
instance_types       = ["t3.medium", "t3.large"]
desired_size         = 3
min_size             = 2
max_size             = 10
db_allocated_storage = 100
db_instance_class    = "db.t3.medium"
db_password          = "YourSecurePassword123!"
backup_retention_days = 30
public_access_cidrs  = ["YOUR_IP/32"]  # Restrict to your IP
```

### Step 3: Deploy

```bash
terraform init
terraform plan
terraform apply
```

### Step 4: Get Connection Details

```bash
# Get outputs
terraform output eks_cluster_endpoint
terraform output rds_endpoint
terraform output s3_bucket_id

# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name sis-analytics
```

### AWS Key Outputs

- `eks_cluster_endpoint`: Kubernetes API endpoint
- `eks_cluster_id`: Cluster identifier
- `rds_endpoint`: Database connection string
- `rds_address`: Database host
- `s3_bucket_id`: Data storage bucket
- `vpc_id`: Virtual Private Cloud ID
- `configure_kubectl`: kubectl configuration command

---

## Azure Deployment

### Azure-Specific Configuration

**Provider Version**: ~> 3.0

**Authentication**: 
- Interactive: `az login`
- Service Principal: Set environment variables (recommended for CI/CD)

### Step 1: Authenticate with Azure

```bash
# Interactive login
az login

# Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Or use Service Principal (CI/CD)
export ARM_CLIENT_ID="<client_id>"
export ARM_CLIENT_SECRET="<client_secret>"
export ARM_SUBSCRIPTION_ID="<subscription_id>"
export ARM_TENANT_ID="<tenant_id>"
```

### Step 2: Configure Azure Variables

```bash
cd oss_framework/terraform/azure
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
azure_region           = "eastus"
environment            = "dev"
cluster_name           = "sis-analytics"
resource_group_name    = "sis-analytics-rg"
kubernetes_version     = "1.28"
node_count             = 3
vm_size                = "Standard_D2s_v3"
enable_auto_scaling    = true
min_node_count         = 2
max_node_count         = 10
db_password            = "YourSecurePassword123!"
backup_retention_days  = 30
storage_replication_type = "GRS"  # Geo-Redundant for production
```

### Step 3: Deploy

```bash
terraform init
terraform plan
terraform apply
```

### Step 4: Get Connection Details

```bash
# Get outputs
terraform output aks_fqdn
terraform output postgresql_fqdn
terraform output storage_account_name

# Configure kubectl
az aks get-credentials --resource-group sis-analytics-rg --name sis-analytics
```

### Azure Key Outputs

- `aks_cluster_name`: Cluster identifier
- `aks_fqdn`: Kubernetes API endpoint
- `postgresql_fqdn`: Database connection string
- `storage_account_name`: Data storage account
- `configure_kubectl`: kubectl configuration command
- `kube_config_raw`: Full kubeconfig output

---

## GCP Deployment

### GCP-Specific Configuration

**Provider Version**: ~> 5.0

**Authentication**: Default Application Credentials

### Step 1: Authenticate with GCP

```bash
# Interactive authentication
gcloud auth application-default login

# Set default project
gcloud config set project YOUR_PROJECT_ID

# Verify authentication
gcloud auth list
gcloud config list
```

### Step 2: Enable Required APIs

```bash
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com
```

### Step 3: Configure GCP Variables

```bash
cd oss_framework/terraform/gcp
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
gcp_project_id       = "my-project-id"
gcp_region           = "us-central1"
environment          = "dev"
cluster_name         = "sis-analytics"
kubernetes_version   = "1.28"
node_count           = 3
machine_type         = "n1-standard-2"
preemptible          = true  # Use preemptible nodes for cost savings
min_node_count       = 2
max_node_count       = 10
db_password          = "YourSecurePassword123!"
backup_retention_days = 30
```

### Step 4: Deploy

```bash
terraform init
terraform plan
terraform apply
```

### Step 5: Get Connection Details

```bash
# Get outputs
terraform output gke_cluster_name
terraform output cloud_sql_connection_name
terraform output storage_bucket_name

# Configure kubectl
gcloud container clusters get-credentials sis-analytics-dev --zone us-central1-a
```

### GCP Key Outputs

- `gke_cluster_name`: Cluster identifier
- `gke_endpoint`: Kubernetes API endpoint
- `cloud_sql_connection_name`: Database connection for proxy
- `cloud_sql_instance_name`: Database instance identifier
- `storage_bucket_name`: Data storage bucket
- `configure_kubectl`: kubectl configuration command

---

## Terraform Configuration

### Variables

Each cloud provider has configurable variables:

**Common Variables**:
- `environment`: dev, staging, or prod
- `cluster_name`: Kubernetes cluster name
- `kubernetes_version`: K8s version (1.28+)
- `db_password`: Database administrator password (required)

**Compute Variables**:
- Instance/VM types and counts
- Auto-scaling min/max values
- Node pool configurations

**Database Variables**:
- Storage size (GB)
- Instance class/tier
- Backup retention (days)
- Replication settings

**Network Variables**:
- CIDR ranges for VPC/VNet
- Public access restrictions

### Best Practices

1. **Never commit terraform.tfvars to Git**
   ```bash
   echo "terraform.tfvars" >> .gitignore
   echo "*.tfstate*" >> .gitignore
   ```

2. **Use terraform.tfvars.example as template**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Then edit terraform.tfvars
   ```

3. **Always review plans before applying**
   ```bash
   terraform plan > plan.txt
   # Review plan.txt carefully
   terraform apply plan.txt
   ```

4. **Use workspaces for multiple environments**
   ```bash
   terraform workspace new dev
   terraform workspace new staging
   terraform workspace new prod
   terraform workspace select dev
   ```

5. **Store state remotely (not locally)**
   - AWS: S3 backend (configured in main.tf)
   - Azure: Azure Storage backend
   - GCP: GCS backend

---

## Outputs

Terraform outputs provide connection information and resource identifiers:

### AWS Outputs

```bash
terraform output eks_cluster_endpoint
terraform output rds_address
terraform output s3_bucket_id
terraform output cluster_summary
```

### Azure Outputs

```bash
terraform output aks_fqdn
terraform output postgresql_fqdn
terraform output storage_account_name
terraform output cluster_summary
```

### GCP Outputs

```bash
terraform output gke_cluster_name
terraform output cloud_sql_connection_name
terraform output storage_bucket_name
terraform output cluster_summary
```

### Summary Output

All providers provide a `cluster_summary` output with all key information:

```json
{
  "cluster_name": "sis-analytics-dev",
  "cluster_endpoint": "https://...",
  "kubernetes_version": "1.28",
  "region": "us-east-1",
  "environment": "dev",
  "node_count": 3,
  "db_endpoint": "sis-analytics.xxx.rds.amazonaws.com"
}
```

---

## Maintenance

### Scaling

**Increase Node Count**:

```bash
# Edit terraform.tfvars
# Change desired_size, min_size, or max_size

terraform plan
terraform apply
```

**Change Node Type**:

```bash
# Update instance_types or machine_type variable
# This may require node replacement

terraform plan
terraform apply
```

### Updates

**Kubernetes Version Updates**:

```bash
# Update cluster_version in terraform.tfvars
cluster_version = "1.29"

terraform plan  # Review changes
terraform apply
```

**Database Scaling**:

```bash
# Update db_instance_class or database_storage_gb
db_instance_class = "db.t3.large"
db_allocated_storage = 200

terraform plan
terraform apply
```

### Backup & Recovery

**Database Backups**:
- Automated daily backups (retention: 30+ days)
- Point-in-time recovery available
- Restore via provider console or CLI

**Kubernetes Workload Backups**:
- Use Velero for cluster backups
- Regular etcd backups
- State stored in persistent volumes

**State Backups**:
- S3/GCS versioning enabled
- Point-in-time recovery possible
- Test recovery procedures regularly

### Monitoring

**Terraform State Drift**:

```bash
# Detect changes made outside Terraform
terraform refresh
terraform plan  # Shows drift if any

# Reimport resources if needed
terraform import aws_eks_cluster.main sis-analytics
```

---

## Troubleshooting

### Common Issues

**Issue: Authentication Fails**

AWS:
```bash
aws sts get-caller-identity
aws configure
```

Azure:
```bash
az login
az account show
```

GCP:
```bash
gcloud auth application-default login
gcloud config list
```

**Issue: Insufficient Permissions**

Check IAM roles:

AWS:
```bash
aws iam get-user
aws iam list-user-policies --user-name YOUR_USER
```

Azure:
```bash
az role assignment list --assignee YOUR_USER_ID
```

GCP:
```bash
gcloud projects get-iam-policy PROJECT_ID
```

**Issue: Resource Creation Timeout**

```bash
# Increase timeout for specific resources
terraform apply -refresh=false  # Skip refreshing state

# Or increase Terraform logs
TF_LOG=debug terraform apply
```

**Issue: State Lock Timeout**

AWS (DynamoDB):
```bash
# Check lock
aws dynamodb scan --table-name terraform-locks

# Remove lock (if truly stuck)
aws dynamodb delete-item \
  --table-name terraform-locks \
  --key '{"LockID": {"S": "sis-analytics"}}'
```

### Debug Mode

Enable detailed logging:

```bash
export TF_LOG=debug
terraform apply
unset TF_LOG
```

Save logs to file:

```bash
export TF_LOG=debug
export TF_LOG_PATH=./terraform-debug.log
terraform apply
```

---

## Cost Considerations

### Cost Optimization Strategies

1. **Use Spot/Preemptible Instances**
   - AWS: Spot instances (up to 70% savings)
   - Azure: Spot VMs (up to 70% savings)
   - GCP: Preemptible nodes (up to 80% savings)

2. **Right-Sizing**
   - Start small (dev: t3.micro, staging: t3.small)
   - Monitor actual usage
   - Scale up based on metrics

3. **Reserved Instances**
   - AWS: 1-year or 3-year reserved instances
   - Azure: Reserved instances
   - GCP: Committed use discounts

4. **Scheduled Scaling**
   - Scale down during off-hours
   - Use CronJobs in Kubernetes
   - Environment-based sizing

5. **Data Optimization**
   - Lifecycle policies for old data
   - Compression and deduplication
   - Archive unused data

### Cost Monitoring

```bash
# AWS
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost"

# Azure
az cost management query --query-string '{...}'

# GCP
gcloud billing accounts list
bq query --use_legacy_sql=false \
  'SELECT project_id, SUM(cost) FROM `billing_project_id.billing_dataset.gcp_billing_export_v1_XXXXX` GROUP BY project_id'
```

---

## Security Best Practices

### Network Security

1. **Restrict Public Access**
   ```hcl
   # AWS
   public_access_cidrs = ["YOUR_OFFICE_IP/32", "VPN_IP/32"]
   
   # Not: ["0.0.0.0/0"]
   ```

2. **Use Private Subnets**
   - Database in private subnets
   - Only bastion/NAT gateway in public
   - Control egress with NAT

3. **Network Policies**
   - Enable Kubernetes network policies
   - Restrict pod-to-pod communication
   - Deny-all ingress default

### Authentication & Authorization

1. **RBAC (Role-Based Access Control)**
   ```bash
   kubectl create serviceaccount deployer -n sis-analytics
   kubectl create rolebinding deployer --clusterrole=edit \
     --serviceaccount=sis-analytics:deployer
   ```

2. **IAM Roles & Policies**
   - Principle of least privilege
   - Service-specific roles
   - Regular access reviews

3. **OIDC for IRSA** (AWS)
   ```bash
   # Service account tied to IAM role
   # Pod gets temporary credentials
   ```

### Data Protection

1. **Encryption at Rest**
   - Database: SSL/TLS enabled
   - Storage: AES-256 encryption
   - EBS/Persistent volumes: Encrypted

2. **Encryption in Transit**
   - TLS 1.2+ for all connections
   - Certificate management
   - API encryption

3. **Secrets Management**
   - Use HashiCorp Vault or cloud provider secrets manager
   - Never store secrets in .tfvars files
   - Rotate regularly

### Backup & Disaster Recovery

1. **Automated Backups**
   ```hcl
   backup_retention_days = 90  # Production
   backup_retention_days = 30  # Staging
   backup_retention_days = 7   # Development
   ```

2. **Cross-Region Backup**
   - Geographic redundancy
   - RTO/RPO targets
   - Regular restore tests

3. **Disaster Recovery Plan**
   - Document procedures
   - Test regularly
   - Maintain runbooks

### Compliance

1. **Audit Logging**
   - CloudTrail (AWS)
   - Azure Activity Log
   - Cloud Audit Logs (GCP)

2. **Compliance Frameworks**
   - HIPAA, FERPA for education data
   - GDPR for EU data
   - SOC2 for security

3. **Regular Security Reviews**
   - Penetration testing
   - Vulnerability scanning
   - Policy reviews

---

## Support & Additional Resources

### Documentation

- **Terraform Docs**: https://www.terraform.io/docs
- **AWS**: https://docs.aws.amazon.com
- **Azure**: https://docs.microsoft.com/azure
- **GCP**: https://cloud.google.com/docs

### Community

- **Terraform Community**: https://discuss.hashicorp.com
- **Stack Overflow**: Tag: terraform
- **GitHub Issues**: Report bugs and request features

### Getting Help

For issues:
1. Check this documentation
2. Review Terraform logs (`TF_LOG=debug`)
3. Verify credentials and permissions
4. Check cloud provider service health
5. Post to community forums with logs (sanitized)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-26 | Initial release with AWS, Azure, GCP support |

---

## License

This Terraform configuration is part of the Open Education Analytics project and is licensed under the MIT License. See LICENSE-CODE for details.

---

Last Updated: January 26, 2024
