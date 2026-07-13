variable "location" {
  type        = string
  description = "Azure region where resources will be deployed"
}

variable "resource_group_name" {
  type        = string
  default     = "uptime-monitor-rg"
}

variable "vm_size" {
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  type        = string
  description = "Path to the RSA public key file for SSH access"
}
