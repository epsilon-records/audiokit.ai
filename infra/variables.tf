variable "project" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "zone" {
  description = "GCP zone"
  type        = string
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
}

variable "gpu_machine_type" {
  description = "Machine type for GPU instances"
  type        = string
  default     = "n1-standard-4"
}

variable "gpu_type" {
  description = "Type of GPU"
  type        = string
  default     = "nvidia-tesla-t4"
}

variable "gpu_count" {
  description = "Number of GPUs per instance"
  type        = number
  default     = 1
} 