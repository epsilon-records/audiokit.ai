provider "google" {
  project = "your-gcp-project-id"
  region  = "us-central1"
}

resource "google_container_cluster" "primary" {
  name     = "audiokit-ai-cluster"
  location = "us-central1-c"

  initial_node_count = 3

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    accelerators {
      accelerator_count = 1
      accelerator_type  = "nvidia-tesla-t4"
    }
  }
}

resource "google_compute_address" "default" {
  name = "audiokit-ai-address"
}

output "cluster_name" {
  value = google_container_cluster.primary.name
} 