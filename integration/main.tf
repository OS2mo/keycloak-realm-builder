# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
terraform {
  backend "pg" {}
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = "3.6.0"
    }
  }
}

# REST API Credentials
#---------------------
variable "admin_client_id" {
  type        = string
  description = ""
  default     = "admin-cli"
}
variable "admin_username" {
  type        = string
  description = "Keycloak API admin account"
  default     = "admin"
}
variable "admin_password" {
  type        = string
  description = "Keycloak API admin password"
}
variable "url" {
  type        = string
  description = "Keycloak Root URL"
  default     = "http://keycloak-service:8080"
}

# Client configuration
#---------------------
variable "client_name" {
  type        = string
  description = "Name of the OpenID Client"
}
variable "client_lifespan" {
  type        = number
  description = "Lifespan of access tokens"
  default     = 300
}
variable "client_secret" {
  type        = string
  description = "Preshared client secret"
}
variable "client_roles" {
  type        = set(string)
  description = "Set of roles to attach to the client"
  default     = []
}

provider "keycloak" {
  client_id = var.admin_client_id
  username  = var.admin_username
  password  = var.admin_password
  url       = var.url
}

data "keycloak_realm" "mo" {
  realm = "mo"
}

data "keycloak_role" "roles" {
  for_each = var.client_roles

  realm_id = data.keycloak_realm.mo.id
  name     = each.key
}

resource "keycloak_openid_client" "client" {
  realm_id  = data.keycloak_realm.mo.id
  client_id = var.client_name

  name                     = var.client_name
  access_type              = "CONFIDENTIAL"
  service_accounts_enabled = true
  access_token_lifespan    = var.client_lifespan

  client_secret = var.client_secret
}

resource "keycloak_openid_client_service_account_realm_role" "client_role" {
  for_each = var.client_roles

  realm_id                = data.keycloak_realm.mo.id
  service_account_user_id = keycloak_openid_client.client.service_account_user_id
  role                    = data.keycloak_role.roles[each.key].name
}
