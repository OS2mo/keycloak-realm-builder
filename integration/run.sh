#!/bin/sh
# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0

terraform init -backend-config="conn_str=$POSTGRES_CONNECTION_STRING" -backend-config="schema_name=$POSTGRES_SCHEMA_NAME"
terraform apply -auto-approve
