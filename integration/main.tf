# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
terraform {
  required_providers {
    keycloak = {
      source  = "keycloak/keycloak"
      version = "5.7.0"
    }
  }

  backend "pg" {}
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
  sensitive   = true
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
  description = "Preshared client secret. If not set, one will be generated and output as client_secret."
  sensitive   = true
  default     = null
}
variable "client_roles" {
  type        = set(string)
  description = "Set of roles to attach to the client"
  default     = []
}
variable "client_standard_flow_enabled" {
  type        = bool
  description = "Whether Standard Flow is enabled"
  default     = false
}
variable "client_valid_redirect_urls" {
  type        = list(string)
  description = "Must be set if Standard Flow is enabled"
  default     = []
}
variable "client_web_origins" {
  type        = list(string)
  description = "List of allowed CORS origins"
  default     = []
}
variable "client_uuid" {
  type        = string
  description = ""
  default     = null
}



resource "random_password" "client_secret" {
  length  = 32
  special = false
}


provider "keycloak" {
  client_id = var.admin_client_id
  username  = var.admin_username
  password  = var.admin_password
  url       = var.url
  base_path = "/auth"
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

  standard_flow_enabled = var.client_standard_flow_enabled
  valid_redirect_uris   = var.client_valid_redirect_urls
  web_origins           = var.client_web_origins

  client_secret = coalesce(var.client_secret, random_password.client_secret.result)
}

resource "keycloak_openid_client_service_account_realm_role" "client_role" {
  for_each = var.client_roles

  realm_id                = data.keycloak_realm.mo.id
  service_account_user_id = keycloak_openid_client.client.service_account_user_id
  role                    = data.keycloak_role.roles[each.key].name
}

output "client_secret" {
  value     = keycloak_openid_client.client.client_secret
  sensitive = true
}

resource "keycloak_openid_hardcoded_claim_protocol_mapper" "client_uuid_claim" {
  count = var.client_uuid != null ? 1 : 0

  realm_id  = data.keycloak_realm.mo.id
  client_id = keycloak_openid_client.client.id
  name      = "hardcoded-uuid"

  claim_name  = "uuid"
  claim_value = var.client_uuid
}
