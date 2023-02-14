# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
FROM hashicorp/terraform:1.3.3@sha256:d97b8378e608a994196302e1e4b386b94d229de1bc7c514a3169d66c53b4e13e

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apk add python3 py3-pip
RUN pip install --no-cache-dir click pydantic[email]

WORKDIR /app

COPY keycloak.tf .
COPY .terraform.lock.hcl .
RUN terraform init -backend=false

COPY main.py .
COPY run.sh .
ENTRYPOINT [ "sh", "run.sh" ]
