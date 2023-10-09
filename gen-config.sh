#!/usr/bin/env bash
# SPDX-FileCopyrightText: Magenta ApS
# SPDX-License-Identifier: MPL-2.0

KEYCLOAK_FILE=$1

TOKEN_REPLY=$(curl -s -d "client_id=admin-cli" -d "username=admin" -d "password=admin" -d "grant_type=password" "http://localhost:5000/auth/realms/master/protocol/openid-connect/token")
TOKEN=$(echo "${TOKEN_REPLY}" | jq .access_token -r)
JSON_REPLY=$(curl -s -H "Authorization: Bearer $TOKEN" -FproviderId=saml -Ffile=@"${KEYCLOAK_FILE}"  "http://localhost:5000/auth/admin/realms/mo/identity-provider/import-config")
echo "${JSON_REPLY}" | jq . --sort-keys
