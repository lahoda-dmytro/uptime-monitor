variable "location" {
  type        = string
  default     = "East US"
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
  default     = "~/.ssh/id_ed25519.pub"
}
