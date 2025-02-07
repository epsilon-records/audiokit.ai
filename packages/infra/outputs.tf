output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "gpu_instance_ip" {
  value = google_compute_instance.gpu_instance.network_interface[0].access_config[0].nat_ip
} 