# ============================================================================
# Azure AKS & Database Outputs
# ============================================================================
# Comprehensive output values for Azure infrastructure deployment

# ============================================================================
# AKS Cluster Outputs
# ============================================================================

output "aks_cluster_id" {
  description = "AKS cluster ID"
  value       = azurerm_kubernetes_cluster.main.id
}

output "aks_cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.main.name
}

output "aks_host" {
  description = "AKS cluster host endpoint"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].host
  sensitive   = true
}

output "aks_client_certificate" {
  description = "Base64 encoded client certificate used by kubectl"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].client_certificate
  sensitive   = true
}

output "aks_client_key" {
  description = "Base64 encoded client key used by kubectl"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].client_key
  sensitive   = true
}

output "aks_cluster_ca_certificate" {
  description = "Base64 encoded cluster CA certificate"
  value       = azurerm_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate
  sensitive   = true
}

output "aks_fqdn" {
  description = "AKS cluster FQDN"
  value       = azurerm_kubernetes_cluster.main.fqdn
}

output "aks_node_resource_group" {
  description = "The name of the node resource group created by AKS"
  value       = azurerm_kubernetes_cluster.main.node_resource_group
}

# ============================================================================
# Resource Group Outputs
# ============================================================================

output "resource_group_id" {
  description = "Resource group ID"
  value       = azurerm_resource_group.main.id
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource group location"
  value       = azurerm_resource_group.main.location
}

# ============================================================================
# PostgreSQL Database Outputs
# ============================================================================

output "postgresql_server_id" {
  description = "PostgreSQL server ID"
  value       = azurerm_postgresql_server.main.id
}

output "postgresql_server_name" {
  description = "PostgreSQL server name"
  value       = azurerm_postgresql_server.main.name
}

output "postgresql_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_server.main.fqdn
}

output "postgresql_username" {
  description = "PostgreSQL administrator username"
  value       = azurerm_postgresql_server.main.administrator_login
  sensitive   = true
}

output "postgresql_version" {
  description = "PostgreSQL version"
  value       = azurerm_postgresql_server.main.version
}

output "postgresql_sku_name" {
  description = "PostgreSQL SKU name"
  value       = azurerm_postgresql_server.main.sku_name
}

output "postgresql_storage_mb" {
  description = "PostgreSQL storage in MB"
  value       = azurerm_postgresql_server.main.storage_mb
}

output "postgresql_backup_retention_days" {
  description = "PostgreSQL backup retention in days"
  value       = azurerm_postgresql_server.main.backup_retention_days
}

output "postgresql_ssl_enforcement_enabled" {
  description = "PostgreSQL SSL enforcement status"
  value       = azurerm_postgresql_server.main.ssl_enforcement_enabled
}

# ============================================================================
# Storage Account Outputs
# ============================================================================

output "storage_account_id" {
  description = "Storage account ID"
  value       = azurerm_storage_account.main.id
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}

output "storage_account_primary_blob_endpoint" {
  description = "Storage account primary blob endpoint"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

output "storage_account_primary_connection_string" {
  description = "Storage account primary connection string"
  value       = azurerm_storage_account.main.primary_connection_string
  sensitive   = true
}

output "storage_account_tier" {
  description = "Storage account tier"
  value       = azurerm_storage_account.main.account_tier
}

output "storage_account_replication_type" {
  description = "Storage account replication type"
  value       = azurerm_storage_account.main.account_replication_type
}

# ============================================================================
# Kubeconfig Configuration Output
# ============================================================================

output "configure_kubectl" {
  description = "Command to configure kubectl to access the AKS cluster"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_kubernetes_cluster.main.name}"
}

output "kube_config_raw" {
  description = "Raw kubeconfig output"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

# ============================================================================
# Connection Strings and URLs
# ============================================================================

output "postgresql_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${azurerm_postgresql_server.main.administrator_login}:password@${azurerm_postgresql_server.main.fqdn}:5432/sis_analytics"
  sensitive   = true
}

output "blob_storage_url" {
  description = "Blob storage account URL"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

# ============================================================================
# Summary Output
# ============================================================================

output "cluster_summary" {
  description = "Summary of cluster configuration"
  value = {
    cluster_name       = azurerm_kubernetes_cluster.main.name
    cluster_fqdn       = azurerm_kubernetes_cluster.main.fqdn
    resource_group     = azurerm_resource_group.main.name
    region             = azurerm_resource_group.main.location
    environment        = var.environment
    node_count         = azurerm_kubernetes_cluster.main.default_node_pool[0].node_count
    vm_size            = azurerm_kubernetes_cluster.main.default_node_pool[0].vm_size
    postgresql_server  = azurerm_postgresql_server.main.fqdn
    storage_account    = azurerm_storage_account.main.name
  }
}
