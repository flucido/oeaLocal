# ============================================================================
# GCP Terraform Variables
# ============================================================================
# Variable definitions for GCP GKE infrastructure

variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
  
  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]$", var.gcp_region))
    error_message = "GCP region must be a valid region name."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "sis-analytics"
}

# ============================================================================
# GKE Configuration
# ============================================================================

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "enable_network_policy" {
  description = "Enable network policy"
  type        = bool
  default     = true
}

variable "enable_http_load_balancing" {
  description = "Enable HTTP load balancing"
  type        = bool
  default     = true
}

variable "enable_horizontal_pod_autoscaling" {
  description = "Enable horizontal pod autoscaling"
  type        = bool
  default     = true
}

# ============================================================================
# Node Pool Configuration
# ============================================================================

variable "node_pool_name" {
  description = "Name of the node pool"
  type        = string
  default     = "default-pool"
}

variable "node_count" {
  description = "Initial number of nodes in the node pool"
  type        = number
  default     = 3
  
  validation {
    condition     = var.node_count > 0 && var.node_count <= 100
    error_message = "Node count must be between 1 and 100."
  }
}

variable "machine_type" {
  description = "Machine type for nodes"
  type        = string
  default     = "n1-standard-2"
}

variable "disk_size_gb" {
  description = "Boot disk size in GB"
  type        = number
  default     = 50
}

variable "preemptible" {
  description = "Use preemptible nodes (lower cost, no SLA)"
  type        = bool
  default     = true
}

variable "enable_autoscaling" {
  description = "Enable autoscaling for node pool"
  type        = bool
  default     = true
}

variable "min_node_count" {
  description = "Minimum number of nodes for autoscaling"
  type        = number
  default     = 2
}

variable "max_node_count" {
  description = "Maximum number of nodes for autoscaling"
  type        = number
  default     = 10
}

# ============================================================================
# Network Configuration
# ============================================================================

variable "network_name" {
  description = "VPC network name"
  type        = string
  default     = "sis-analytics-network"
}

variable "subnet_name" {
  description = "Subnet name"
  type        = string
  default     = "sis-analytics-subnet"
}

variable "subnet_cidr" {
  description = "Subnet CIDR range"
  type        = string
  default     = "10.0.0.0/20"
}

variable "pods_secondary_range_name" {
  description = "Secondary range name for pods"
  type        = string
  default     = "pods"
}

variable "pods_secondary_range_cidr" {
  description = "Secondary CIDR range for pods"
  type        = string
  default     = "10.4.0.0/14"
}

variable "services_secondary_range_name" {
  description = "Secondary range name for services"
  type        = string
  default     = "services"
}

variable "services_secondary_range_cidr" {
  description = "Secondary CIDR range for services"
  type        = string
  default     = "10.8.0.0/20"
}

# ============================================================================
# Cloud SQL Configuration
# ============================================================================

variable "database_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "POSTGRES_15"
}

variable "database_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "database_storage_gb" {
  description = "Initial database storage in GB"
  type        = number
  default     = 100
}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default     = "sis_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention in days"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 0 && var.backup_retention_days <= 35
    error_message = "Backup retention must be between 0 and 35 days."
  }
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for database"
  type        = bool
  default     = false
}

# ============================================================================
# Cloud Storage Configuration
# ============================================================================

variable "storage_bucket_location" {
  description = "Storage bucket location"
  type        = string
  default     = "US"
}

variable "storage_bucket_force_destroy" {
  description = "Force destroy storage bucket"
  type        = bool
  default     = false
}

variable "storage_versioning_enabled" {
  description = "Enable versioning for storage bucket"
  type        = bool
  default     = true
}

# ============================================================================
# Tags and Labels
# ============================================================================

variable "common_labels" {
  description = "Common labels applied to all resources"
  type        = map(string)
  default = {
    project   = "oss-framework"
    module    = "sis-analytics"
    managed-by = "terraform"
  }
}

variable "resource_name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "sis"
}
