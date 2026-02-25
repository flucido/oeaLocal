terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

variable "gcp_project_id" {
  type = string
}

variable "gcp_region" {
  type    = string
  default = "us-central1"
}

variable "environment" {
  type = string
}

variable "cluster_name" {
  type    = string
  default = "sis-analytics"
}

# GKE Cluster
resource "google_container_cluster" "main" {
  name     = "${var.cluster_name}-${var.environment}"
  location = var.gcp_region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
}

resource "google_container_node_pool" "main" {
  name       = "${var.cluster_name}-${var.environment}-pool"
  cluster    = google_container_cluster.main.name
  location   = var.gcp_region
  node_count = 3

  node_config {
    preemptible  = var.environment == "prod" ? false : true
    machine_type = "n1-standard-2"
    disk_size_gb = 50

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  autoscaling {
    min_node_count = 2
    max_node_count = 10
  }
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "main" {
  name             = "sis-analytics-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  deletion_protection = var.environment == "prod" ? true : false

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      backup_retention_days          = 30
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }
  }
}

resource "google_sql_database" "main" {
  name     = "sis_analytics"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = "sis_admin"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Cloud Storage Bucket
resource "google_storage_bucket" "main" {
  name          = "sis-analytics-${var.environment}-${var.gcp_project_id}"
  location      = var.gcp_region
  force_destroy = var.environment == "dev" ? true : false

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "sis-analytics-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  name          = "sis-analytics-${var.environment}-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"
  }
}

# Outputs
output "gke_cluster_name" {
  value = google_container_cluster.main.name
}

output "gke_endpoint" {
  value = google_container_cluster.main.endpoint
}

output "cloud_sql_instance" {
  value = google_sql_database_instance.main.connection_name
}

output "storage_bucket_name" {
  value = google_storage_bucket.main.name
}
