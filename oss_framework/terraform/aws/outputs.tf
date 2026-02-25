# ============================================================================
# AWS EKS & RDS Outputs
# ============================================================================
# Comprehensive output values for AWS infrastructure deployment
# These outputs provide essential information for post-deployment configuration

# ============================================================================
# EKS Cluster Outputs
# ============================================================================

output "eks_cluster_id" {
  description = "The name/id of the EKS cluster"
  value       = aws_eks_cluster.main.id
}

output "eks_cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the cluster"
  value       = aws_eks_cluster.main.arn
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.main.endpoint
}

output "eks_cluster_version" {
  description = "The Kubernetes server version for the cluster"
  value       = aws_eks_cluster.main.version
}

output "eks_cluster_certificate_authority" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "eks_cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}

output "eks_node_group_id" {
  description = "EKS node group ID"
  value       = aws_eks_node_group.main.id
}

output "eks_node_group_arn" {
  description = "Amazon Resource Name (ARN) of the EKS Node Group"
  value       = aws_eks_node_group.main.arn
}

output "eks_node_group_role_arn" {
  description = "IAM role ARN of EKS Node Group"
  value       = aws_iam_role.eks_node_group_role.arn
}

output "eks_node_security_group_id" {
  description = "Security group ID of EKS nodes"
  value       = aws_security_group.eks_nodes.id
}

output "eks_oidc_provider_arn" {
  description = "ARN of the OIDC Provider for IRSA (IAM Roles for Service Accounts)"
  value       = aws_iam_openid_connect_provider.eks.arn
}

# ============================================================================
# VPC & Network Outputs
# ============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "vpc_public_subnets" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "vpc_private_subnets" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "vpc_nat_gateway_ips" {
  description = "Elastic IP addresses of NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}

# ============================================================================
# RDS Database Outputs
# ============================================================================

output "rds_db_instance_id" {
  description = "The RDS instance identifier"
  value       = aws_db_instance.sis_postgres.id
}

output "rds_db_instance_arn" {
  description = "The ARN of the RDS instance"
  value       = aws_db_instance.sis_postgres.arn
}

output "rds_endpoint" {
  description = "The RDS instance endpoint (host:port)"
  value       = aws_db_instance.sis_postgres.endpoint
  sensitive   = true
}

output "rds_address" {
  description = "The hostname of the RDS instance"
  value       = aws_db_instance.sis_postgres.address
}

output "rds_port" {
  description = "The RDS instance port"
  value       = aws_db_instance.sis_postgres.port
}

output "rds_username" {
  description = "The master username for the database"
  value       = aws_db_instance.sis_postgres.username
  sensitive   = true
}

output "rds_db_name" {
  description = "The name of the database"
  value       = aws_db_instance.sis_postgres.db_name
}

output "rds_instance_class" {
  description = "The instance class of the RDS instance"
  value       = aws_db_instance.sis_postgres.instance_class
}

output "rds_allocated_storage" {
  description = "The allocated storage in gigabytes"
  value       = aws_db_instance.sis_postgres.allocated_storage
}

output "rds_security_group_id" {
  description = "Security group ID for RDS instance"
  value       = aws_security_group.rds.id
}

output "rds_backup_retention_period" {
  description = "The backup retention period in days"
  value       = aws_db_instance.sis_postgres.backup_retention_period
}

output "rds_backup_window" {
  description = "The daily time window during which backups occur"
  value       = aws_db_instance.sis_postgres.backup_window
}

# ============================================================================
# S3 Bucket Outputs
# ============================================================================

output "s3_bucket_id" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.sis_data.id
}

output "s3_bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.sis_data.arn
}

output "s3_bucket_region" {
  description = "The AWS region of the S3 bucket"
  value       = aws_s3_bucket.sis_data.region
}

output "s3_bucket_versioning_status" {
  description = "The versioning status of the S3 bucket"
  value       = try(aws_s3_bucket_versioning.sis_data.versioning_configuration[0].status, "Disabled")
}

# ============================================================================
# IAM Role & Policy Outputs
# ============================================================================

output "eks_cluster_role_arn" {
  description = "IAM role ARN for EKS cluster"
  value       = aws_iam_role.eks_cluster_role.arn
}

output "eks_cluster_role_name" {
  description = "IAM role name for EKS cluster"
  value       = aws_iam_role.eks_cluster_role.name
}

output "eks_service_role_arn" {
  description = "IAM role ARN for EKS service account"
  value       = aws_iam_role.eks_service_role.arn
}

# ============================================================================
# Kubeconfig Configuration Output
# ============================================================================

output "configure_kubectl" {
  description = "Command to configure kubectl to access the EKS cluster"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.id}"
}

# ============================================================================
# Summary Output
# ============================================================================

output "cluster_summary" {
  description = "Summary of cluster configuration"
  value = {
    cluster_name       = aws_eks_cluster.main.id
    cluster_version    = aws_eks_cluster.main.version
    cluster_endpoint   = aws_eks_cluster.main.endpoint
    region             = var.aws_region
    environment        = var.environment
    node_count         = aws_eks_node_group.main.desired_size
    node_types         = var.instance_types
    rds_endpoint       = aws_db_instance.sis_postgres.endpoint
    rds_port           = aws_db_instance.sis_postgres.port
    s3_bucket          = aws_s3_bucket.sis_data.id
    vpc_id             = aws_vpc.main.id
    vpc_cidr           = aws_vpc.main.cidr_block
  }
}
