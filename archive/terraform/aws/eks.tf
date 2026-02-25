# AWS EKS Cluster Module
# Creates managed Kubernetes cluster with auto-scaling nodes

resource "aws_eks_cluster" "main" {
  name     = "${var.cluster_name}-${var.environment}"
  version  = var.cluster_version
  role_arn = aws_iam_role.cluster.arn

  vpc_config {
    subnet_ids              = aws_subnet.main[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.public_access_cidrs
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policy,
  ]

  tags = {
    Name = "${var.cluster_name}-${var.environment}"
  }
}

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-${var.environment}-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = aws_subnet.main[*].id
  version         = var.cluster_version

  scaling_config {
    desired_size = var.desired_size
    max_size     = var.max_size
    min_size     = var.min_size
  }

  instance_types = var.instance_types

  depends_on = [
    aws_iam_role_policy_attachment.node_policy,
    aws_iam_role_policy_attachment.cni_policy,
  ]

  tags = {
    Name = "${var.cluster_name}-${var.environment}"
  }
}

# RDS PostgreSQL Database
resource "aws_db_instance" "sis_postgres" {
  identifier     = "sis-analytics-${var.environment}"
  engine         = "postgres"
  engine_version = "16.1"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  iops                  = 3000
  performance_insights_enabled = true

  db_name  = "sis_analytics"
  username = "sis_admin"
  password = var.db_password

  parameter_group_name = aws_db_parameter_group.sis.name
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = var.backup_retention_days
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  multi_az               = var.environment == "prod" ? true : false

  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment == "dev" ? true : false

  tags = {
    Name = "sis-analytics-${var.environment}"
  }
}

# S3 Bucket for data
resource "aws_s3_bucket" "sis_data" {
  bucket = "sis-analytics-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "sis-analytics-data-${var.environment}"
  }
}

resource "aws_s3_bucket_versioning" "sis_data" {
  bucket = aws_s3_bucket.sis_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sis_data" {
  bucket = aws_s3_bucket.sis_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# IAM Role for EKS Cluster
resource "aws_iam_role" "cluster" {
  name = "sis-analytics-cluster-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}

# IAM Role for EKS Nodes
resource "aws_iam_role" "node" {
  name = "sis-analytics-node-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.node.name
}

resource "aws_iam_role_policy_attachment" "cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.node.name
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name = "sis-analytics-rds-${var.environment}"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_nodes.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group for EKS Nodes
resource "aws_security_group" "eks_nodes" {
  name = "sis-analytics-eks-nodes-${var.environment}"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "sis-analytics-vpc-${var.environment}"
  }
}

# Subnets
resource "aws_subnet" "main" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "sis-analytics-subnet-${count.index}"
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "sis-analytics-${var.environment}"
  subnet_ids = aws_subnet.main[*].id
}

# DB Parameter Group
resource "aws_db_parameter_group" "sis" {
  name_prefix = "sis-analytics-"
  family      = "postgres16"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }
}

# Data sources
data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

# Outputs
output "eks_cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "eks_cluster_name" {
  value = aws_eks_cluster.main.name
}

output "rds_endpoint" {
  value = aws_db_instance.sis_postgres.endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.sis_data.id
}
