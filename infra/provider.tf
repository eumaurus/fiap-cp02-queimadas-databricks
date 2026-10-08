terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Sem backend remoto de proposito: o estado fica local no runner do GitHub Actions.
  # Isso evita depender de um Storage Account de tfstate criado a mao.
  # Consequencia: cada execucao do workflow cria um ambiente NOVO (veja main.tf).
}

provider "azurerm" {
  features {}

  # O workflow exporta ARM_SUBSCRIPTION_ID a partir do 'az login'.
  # "none" evita o Terraform tentar registrar resource providers (o Contributor
  # do service principal as vezes nao tem permissao para isso). O workflow
  # registra o Microsoft.DBforMySQL por conta propria.
  resource_provider_registrations = "none"
}
