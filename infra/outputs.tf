output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "mysql_server_name" {
  value = azurerm_mysql_flexible_server.mysql.name
}

output "mysql_fqdn" {
  value = azurerm_mysql_flexible_server.mysql.fqdn
}

output "database_name" {
  value = azurerm_mysql_flexible_database.db.name
}

output "mysql_admin_username" {
  value = var.mysql_admin_username
}
