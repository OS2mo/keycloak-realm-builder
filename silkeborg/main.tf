# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
terraform {
  backend "pg" {
    schema_name="terraform_remote_state_sd_changed_at"
  }
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = "3.6.0"
    }
  }
}

variable "keycloak_admin_client_id" {
  type        = string
  description = ""
  default     = "admin-cli"
}

variable "keycloak_admin_username" {
  type        = string
  description = ""
  default     = "admin"
}

variable "keycloak_admin_password" {
  type        = string
  description = ""
}

variable "keycloak_url" {
  type        = string
  description = ""
  default     = "http://localhost:8081"
}

variable "keycloak_client_name" {
  type        = string
  description = ""
}

variable "keycloak_client_lifespan" {
  type        = number
  description = ""
  default     = 300
}

variable "keycloak_client_secret" {
  type        = string
  description = ""
}

provider "keycloak" {
  client_id = var.keycloak_admin_client_id
  username  = var.keycloak_admin_username
  password  = var.keycloak_admin_password
  url       = var.keycloak_url
}

data "keycloak_realm" "mo" {
  realm        = "mo"
}

data "keycloak_role" "admin" {
  realm_id    = data.keycloak_realm.mo.id
  name        = "admin"
}

resource "keycloak_openid_client" "client" {
  realm_id  = data.keycloak_realm.mo.id
  client_id = var.keycloak_client_name

  name                     = var.keycloak_client_name
  access_type              = "CONFIDENTIAL"
  service_accounts_enabled = true
  access_token_lifespan    = var.keycloak_client_lifespan

  client_secret = var.keycloak_client_secret
}

resource "keycloak_openid_client_service_account_realm_role" "realm_role" {
  realm_id                = data.keycloak_realm.mo.id
  service_account_user_id = keycloak_openid_client.client.service_account_user_id
  role                    = data.keycloak_role.admin.name
}
