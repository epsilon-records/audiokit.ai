provider "google" {
  project = var.project
  region  = var.region
}

# Create a GKE cluster
resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region
  initial_node_count = 3

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    # For GPU-enabled nodes, further configuration is required.
  }
}

# Provision a GPU instance (for model serving/inference)
resource "google_compute_instance" "gpu_instance" {
  name         = "gpu-instance"
  machine_type = var.gpu_machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
    }
  }

  scheduling {
    on_host_maintenance = "TERMINATE"
    preemptible         = false
  }

  guest_accelerator {
    type  = var.gpu_type
    count = var.gpu_count
  }

  network_interface {
    network = "default"
    access_config {}
  }
} 