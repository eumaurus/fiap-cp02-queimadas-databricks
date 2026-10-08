resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

# O sufixo tambem entra no nome do Resource Group. Assim, se uma execucao falhar
# no meio (estado local se perde), a proxima execucao nao bate em "resource group
# already exists". Resource Groups orfaos podem ser apagados no portal.
resource "azurerm_resource_group" "rg" {
  name     = "${var.resource_group_name}-${random_string.suffix.result}"
  location = var.location
}

resource "azurerm_mysql_flexible_server" "mysql" {
  name                = "mysql-queimadas-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  administrator_login    = var.mysql_admin_username
  administrator_password = var.mysql_admin_password

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  sku_name = "B_Standard_B1ms"
  version  = "8.0.21"

  # 'zone' removido de proposito: fixar a zona 3 e uma causa comum de erro de
  # capacidade. Sem ela, a Azure escolhe uma zona disponivel.

  storage {
    size_gb = 20
  }
}

resource "azurerm_mysql_flexible_database" "db" {
  name                = var.database_name
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mysql_flexible_server.mysql.name
  charset             = "utf8mb4"
  collation           = "utf8mb4_unicode_ci"
}

resource "azurerm_mysql_flexible_server_firewall_rule" "allow_azure_services" {
  name                = "AllowAzureServices"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mysql_flexible_server.mysql.name

  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Libera qualquer IP: necessario porque o Databricks Serverless e o Cloud Shell
# saem com IPs variaveis. NAO use isso em producao.
resource "azurerm_mysql_flexible_server_firewall_rule" "allow_all" {
  name                = "AllowAllIP"
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_mysql_flexible_server.mysql.name

  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}
