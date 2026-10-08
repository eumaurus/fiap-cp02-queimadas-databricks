variable "resource_group_name" {
  type        = string
  description = "Prefixo do Resource Group (um sufixo aleatorio e adicionado)"
  default     = "rg-queimadas-cp02"
}

variable "location" {
  type        = string
  description = "Regiao Azure (eastus2 funcionou no Checkpoint 01; o workflow permite trocar sem editar codigo)"
  default     = "eastus2"
}

variable "mysql_admin_username" {
  type        = string
  description = "Administrador do MySQL Flexible Server"
  default     = "queimadasadmin"
}

variable "mysql_admin_password" {
  type        = string
  description = "Senha do admin do MySQL (vem da secret MYSQL_ADMIN_PASSWORD)"
  sensitive   = true
}

variable "database_name" {
  type        = string
  description = "Nome do banco"
  default     = "queimadas"
}
