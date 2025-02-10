# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
FROM hashicorp/terraform:1.1.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY main.tf .
COPY .terraform.lock.hcl .
COPY init-sh .
COPY run.sh .
RUN ["sh", "init.sh"]
ENTRYPOINT [ "sh", "run.sh" ]
