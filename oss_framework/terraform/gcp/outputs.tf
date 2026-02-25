# ============================================================================
# GCP GKE & Cloud SQL Outputs
# ============================================================================
# Comprehensive output values for GCP infrastructure deployment

# ============================================================================
# GKE Cluster Outputs
# ============================================================================

output "gke_cluster_id" {
  description = "GKE cluster ID"
  value       = google_container_cluster.main.id
}

output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.main.name
}

output "gke_cluster_location" {
  description = "GKE cluster location"
  value       = google_container_cluster.main.location
}

output "gke_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.main.endpoint
  sensitive   = true
}

output "gke_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.main.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "gke_kubernetes_version" {
  description = "GKE cluster Kubernetes version"
  value       = google_container_cluster.main.min_master_version
}

output "gke_node_pool_id" {
  description = "GKE node pool ID"
  value       = google_container_node_pool.main.id
}

output "gke_node_pool_name" {
  description = "GKE node pool name"
  value       = google_container_node_pool.main.name
}

output "gke_node_pool_instance_group_urls" {
  description = "Instance group URLs of the node pool"
  value       = google_container_node_pool.main.instance_group_urls
}

# ============================================================================
# Network Outputs
# ============================================================================

output "vpc_network_id" {
  description = "VPC network ID"
  value       = google_compute_network.main.id
}

output "vpc_network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "vpc_network_self_link" {
  description = "VPC network self link"
  value       = google_compute_network.main.self_link
}

output "subnet_id" {
  description = "Subnet ID"
  value       = google_compute_subnetwork.main.id
}

output "subnet_name" {
  description = "Subnet name"
  value       = google_compute_subnetwork.main.name
}

output "subnet_ip_cidr_range" {
  description = "Subnet CIDR range"
  value       = google_compute_subnetwork.main.ip_cidr_range
}

# ============================================================================
# Cloud SQL Outputs
# ============================================================================

output "cloud_sql_instance_id" {
  description = "Cloud SQL instance ID"
  value       = google_sql_database_instance.main.id
}

output "cloud_sql_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL connection name (for proxy)"
  value       = google_sql_database_instance.main.connection_name
}

output "cloud_sql_private_ip_address" {
  description = "Cloud SQL private IP address"
  value       = try(google_sql_database_instance.main.private_ip_address, "")
}

output "cloud_sql_public_ip_address" {
  description = "Cloud SQL public IP address"
  value       = try(google_sql_database_instance.main.public_ip_address, "")
  sensitive   = true
}

output "cloud_sql_database_version" {
  description = "Cloud SQL database version"
  value       = google_sql_database_instance.main.database_version
}

output "cloud_sql_database_name" {
  description = "Cloud SQL database name"
  value       = google_sql_database.main.name
}

output "cloud_sql_user" {
  description = "Cloud SQL database user"
  value       = google_sql_user.main.name
  sensitive   = true
}

output "cloud_sql_tier" {
  description = "Cloud SQL instance tier"
  value       = google_sql_database_instance.main.settings[0].tier
}

# ============================================================================
# Cloud Storage Outputs
# ============================================================================

output "storage_bucket_id" {
  description = "Cloud Storage bucket ID"
  value       = google_storage_bucket.main.id
}

output "storage_bucket_name" {
  description = "Cloud Storage bucket name"
  value       = google_storage_bucket.main.name
}

output "storage_bucket_url" {
  description = "Cloud Storage bucket URL"
  value       = "gs://${google_storage_bucket.main.name}"
}

output "storage_bucket_self_link" {
  description = "Cloud Storage bucket self link"
  value       = google_storage_bucket.main.self_link
}

output "storage_bucket_location" {
  description = "Cloud Storage bucket location"
  value       = google_storage_bucket.main.location
}

# ============================================================================
# Kubeconfig Configuration Output
# ============================================================================

output "configure_kubectl" {
  description = "Command to configure kubectl to access the GKE cluster"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.main.name} --zone=${google_container_cluster.main.location} --project=${var.gcp_project_id}"
}

output "gke_auth_configuration" {
  description = "Auth configuration for kubectl"
  value = {
    cluster_name = google_container_cluster.main.name
    cluster_ca   = google_container_cluster.main.master_auth[0].cluster_ca_certificate
    endpoint     = google_container_cluster.main.endpoint
    zone         = google_container_cluster.main.location
  }
  sensitive = true
}

# ============================================================================
# Connection Information
# ============================================================================

output "cloud_sql_connection_string" {
  description = "Cloud SQL connection string"
  value       = "postgresql://${google_sql_user.main.name}:password@/${google_sql_database.main.name}?host=/cloudsql/${google_sql_database_instance.main.connection_name}"
  sensitive   = true
}

output "storage_bucket_gs_uri" {
  description = "Cloud Storage bucket GS URI"
  value       = "gs://${google_storage_bucket.main.name}"
}

# ============================================================================
# Project Information
# ============================================================================

output "gcp_project_id" {
  description = "GCP project ID"
  value       = var.gcp_project_id
}

output "gcp_region" {
  description = "GCP region"
  value       = var.gcp_region
}

# ============================================================================
# Summary Output
# ============================================================================

output "cluster_summary" {
  description = "Summary of cluster configuration"
  value = {
    cluster_name           = google_container_cluster.main.name
    cluster_endpoint       = google_container_cluster.main.endpoint
    kubernetes_version     = google_container_cluster.main.min_master_version
    region                 = var.gcp_region
    environment            = var.environment
    node_pool_name         = google_container_node_pool.main.name
    machine_type           = var.machine_type
    initial_node_count     = var.node_count
    preemptible            = var.preemptible
    cloud_sql_instance     = google_sql_database_instance.main.connection_name
    cloud_sql_version      = google_sql_database_instance.main.database_version
    storage_bucket         = google_storage_bucket.main.name
    vpc_network            = google_compute_network.main.name
    subnet_cidr            = google_compute_subnetwork.main.ip_cidr_range
  }
}
