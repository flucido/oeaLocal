terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "azure_region" {
  type    = string
  default = "eastus"
}

variable "environment" {
  type = string
}

variable "cluster_name" {
  type    = string
  default = "sis-analytics"
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name       = "sis-analytics-${var.environment}"
  location   = var.azure_region
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.cluster_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "sis-analytics-${var.environment}"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
  }
}

# Database for PostgreSQL
resource "azurerm_postgresql_server" "main" {
  name                = "sis-analytics-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  administrator_login          = "sis_admin"
  administrator_login_password = var.db_password

  sku_name   = "B_Gen5_2"
  storage_mb = 102400

  backup_retention_days        = 30
  geo_redundant_backup_enabled = var.environment == "prod" ? true : false
  auto_grow_enabled            = true
  ssl_enforcement_enabled      = true
  version                      = "14"
}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "sisanalytics${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

# Outputs
output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "aks_host" {
  value = azurerm_kubernetes_cluster.main.kube_config[0].host
}

output "postgres_fqdn" {
  value = azurerm_postgresql_server.main.fqdn
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}
