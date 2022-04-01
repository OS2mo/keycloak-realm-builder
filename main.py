# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
from enum import Enum
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import click
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import EmailStr
from pydantic import parse_obj_as
from pydantic import PositiveInt
from pydantic import root_validator


class Roles(str, Enum):
    admin = "admin"
    owner = "owner"


class KeycloakUser(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    email: EmailStr
    roles: List[Roles] = []
    enabled: bool = True


class Settings(BaseSettings):
    # Keycloak admin credentials
    keycloak_admin_client_id: str = "admin-cli"
    keycloak_admin_username: str = "terraform"
    keycloak_admin_password: str
    keycloak_url: str = "http://localhost:8081"

    # Display name shown on the main Keycloak user login page
    keycloak_realm_display_name: str = "OS2mo"

    # Frontend page(s) that Keycloak is allowed to redirect users back to after they
    # have authenticated successfully in Keycloak
    keycloak_mo_client_redirect_uri: List[Union[AnyHttpUrl, Literal["*"]]] = [
        parse_obj_as(AnyHttpUrl, "http://localhost:5001/*")
    ]

    keycloak_egir_client_redirect_uri: List[Union[AnyHttpUrl, Literal["*"]]] = [
        parse_obj_as(AnyHttpUrl, "http://localhost:5001/*")
    ]

    # Allowed CORS origins
    keycloak_mo_client_web_origin: List[Union[AnyHttpUrl, Literal["*"]]] = [
        parse_obj_as(AnyHttpUrl, "http://localhost:5001")
    ]

    # MO token lifespan
    keycloak_mo_token_lifespan: PositiveInt = 300

    keycloak_egir_client_web_origin: List[Union[AnyHttpUrl, Literal["*"]]] = [
        parse_obj_as(AnyHttpUrl, "http://localhost:5001")
    ]

    # Toggles DIPEX client enablement. If non-user clients should be allowed to
    # contact Keycloak, the DIPEX client can be used. The client uses a
    # client secret auth mechanism to get OIDC tokens instead of the usual
    # username/password mechanism (see further details in the Sphinx MO docs on
    # the development branch)
    keycloak_dipex_client_enabled: bool = False

    # Fix 45298: We need longer access token lifespan for DIPEX
    # This should be set to the default of 5 minutes when we fix our clients
    # Default: 43200 seconds, i.e. 12 hours
    keycloak_dipex_token_lifespan: PositiveInt = 43200

    # DIPEX client secret that can be used to obtain an OIDC token
    # For an example, see:
    # * https://git.magenta.dk/rammearkitektur/os2mo/-/blob/development/backend/ \
    #       tests/manual/keycloak-client-secret.py
    keycloak_dipex_client_secret: Optional[str]

    # Toggle orgviewer client.
    keycloak_orgviewer_client_enabled: bool = False
    # Token lifespan is 0 for now. We can remove this, once the RBAC reader
    # role works _and_ orgviewer implement keycloak in the frontend.
    keycloak_orgviewer_token_lifespan: PositiveInt = 0
    keycloak_orgviewer_client_secret: Optional[str]

    # Toggles EGIR client enablement
    keycloak_egir_client_enabled: bool = False

    # The EGIR client secret
    keycloak_egir_client_secret: Optional[str]

    # The MO realm will have the users below auto-provisioned
    # which can be handy for testing purposes
    keycloak_realm_users: Optional[List[KeycloakUser]] = []

    # IDP Configuration
    keycloak_idp_enable: bool = False
    keycloak_idp_encryption_key: Optional[str]
    keycloak_idp_signing_certificate: Optional[str]
    keycloak_idp_signed_requests: bool = False
    # https://github.com/mrparkers/terraform-provider-keycloak/blob/master/provider/resource_keycloak_saml_identity_provider.go#L10
    keycloak_idp_name_id_policy_format: str = "Unspecified"
    keycloak_idp_entity_id: Optional[AnyHttpUrl]
    keycloak_idp_logout_service_url: Optional[AnyHttpUrl]
    keycloak_idp_signon_service_url: Optional[AnyHttpUrl]
    keycloak_idp_clock_skew: int = 10

    # Specifies whether SSL is required for Keycloak requests. Can be one of
    # "all", "external" or "none". The options are further described here:
    # https://www.keycloak.org/docs/latest/server_installation/#_setting_up_ssl
    keycloak_ssl_required_mo: str = "all"
    keycloak_ssl_required_lora: str = "all"

    # LoRa
    keycloak_lora_realm_enabled: bool = False
    keycloak_lora_client_secret: Optional[str]
    keycloak_lora_dipex_client_enabled: bool = False
    keycloak_lora_dipex_client_secret: Optional[str]
    keycloak_lora_token_lifespan: PositiveInt = 300
    keycloak_lora_dipex_token_lifespan: PositiveInt = 300

    @root_validator
    def optionally_required(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check that derived keys are set if master switch is set."""
        optionally_required_fields = {
            "keycloak_idp_enable": (
                "keycloak_idp_encryption_key",
                "keycloak_idp_signing_certificate",
                "keycloak_idp_entity_id",
                "keycloak_idp_logout_service_url",
                "keycloak_idp_signon_service_url",
            ),
            "keycloak_dipex_client_enabled": ("keycloak_dipex_client_secret",),
            "keycloak_orgviewer_client_enabled": ("keycloak_orgviewer_client_secret",),
            "keycloak_egir_client_enabled": ("keycloak_egir_client_secret",),
            "keycloak_lora_realm_enabled": ("keycloak_lora_client_secret",),
            "keycloak_lora_dipex_client_enabled": (
                "keycloak_lora_dipex_client_secret",
            ),
        }
        for main_key, required_keys in optionally_required_fields.items():
            if not values[main_key]:
                continue
            for required_key in required_keys:
                if required_key not in values:
                    raise ValueError(f"{required_key} not set")
                if values[required_key] is None:
                    raise ValueError(f"{required_key} is None")
        return values


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    return Settings()


def generate_file() -> None:
    settings = get_settings()
    settings_serialized = settings.json(indent=4)
    print(settings_serialized)


@click.command()
def main() -> None:
    generate_file()


if __name__ == "__main__":
    main()
