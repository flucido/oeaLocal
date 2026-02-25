# ============================================================================
# Azure Terraform Variables
# ============================================================================
# Variable definitions for Azure AKS infrastructure

variable "azure_region" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
  
  validation {
    condition     = can(regex("^[a-z]+$", var.azure_region))
    error_message = "Azure region must be a valid region name."
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
  description = "AKS cluster name"
  type        = string
  default     = "sis-analytics"
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "sis-analytics-rg"
}

# ============================================================================
# AKS Configuration
# ============================================================================

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_pool_name" {
  description = "Name of the default node pool"
  type        = string
  default     = "default"
}

variable "node_count" {
  description = "Number of nodes in the AKS cluster"
  type        = number
  default     = 3
  
  validation {
    condition     = var.node_count > 0 && var.node_count <= 100
    error_message = "Node count must be between 1 and 100."
  }
}

variable "vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "enable_auto_scaling" {
  description = "Enable autoscaling for AKS cluster"
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

variable "enable_rbac" {
  description = "Enable RBAC on the AKS cluster"
  type        = bool
  default     = true
}

# ============================================================================
# Network Configuration
# ============================================================================

variable "network_plugin" {
  description = "Network plugin to use (azure, kubenet)"
  type        = string
  default     = "azure"
}

variable "service_cidr" {
  description = "CIDR range for Kubernetes services"
  type        = string
  default     = "10.1.0.0/16"
}

variable "dns_service_ip" {
  description = "IP address for DNS service"
  type        = string
  default     = "10.1.0.10"
}

# ============================================================================
# Database Configuration
# ============================================================================

variable "db_administrator_login" {
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

variable "db_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "14"
}

variable "db_sku_name" {
  description = "SKU name for Database for PostgreSQL"
  type        = string
  default     = "B_Gen5_2"
}

variable "db_storage_mb" {
  description = "Database storage in MB"
  type        = number
  default     = 102400  # 100 GB
}

variable "backup_retention_days" {
  description = "Database backup retention in days"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 7 && var.backup_retention_days <= 35
    error_message = "Backup retention must be between 7 and 35 days."
  }
}

variable "enable_geo_redundant_backup" {
  description = "Enable geo-redundant backup"
  type        = bool
  default     = false
}

variable "enable_ssl_enforcement" {
  description = "Enable SSL enforcement for database"
  type        = bool
  default     = true
}

# ============================================================================
# Storage Configuration
# ============================================================================

variable "storage_account_tier" {
  description = "Storage account tier (Standard, Premium)"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Storage replication type (LRS, GRS, RAGRS, ZRS)"
  type        = string
  default     = "GRS"
}

variable "enable_https_traffic_only" {
  description = "Enable HTTPS traffic only for storage account"
  type        = bool
  default     = true
}

# ============================================================================
# Tags and Naming
# ============================================================================

variable "common_tags" {
  description = "Common tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "OSS Framework"
    Module      = "SIS Analytics"
    ManagedBy   = "Terraform"
  }
}

variable "resource_name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "sis"
}
