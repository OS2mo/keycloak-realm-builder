#!/bin/sh
# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0

terraform init -backend-config="conn_str=$POSTGRES_CONNECTION_STRING"
terraform apply -auto-approve
