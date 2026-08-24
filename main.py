# SPDX-FileCopyrightText: Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
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


class KeycloakUser(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    email: EmailStr
    uuid: Optional[str] = None
    roles: List[str] = []
    enabled: bool = True


class Settings(BaseSettings):
    class Config:
        @classmethod
        def prepare_field(cls, field) -> None:  # type: ignore
            super().prepare_field(field)  # type: ignore
            # Add optional TF_VAR prefix
            env_names = field.field_info.extra["env_names"]
            prefix_env_names = set(map(lambda x: "tf_var_" + x, env_names))
            field.field_info.extra["env_names"] = set.union(env_names, prefix_env_names)

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

    # Allowed CORS origins
    keycloak_mo_client_web_origin: List[Union[AnyHttpUrl, Literal["*"]]] = [
        parse_obj_as(AnyHttpUrl, "http://localhost:5001")
    ]

    # MO token lifespan
    keycloak_mo_token_lifespan: PositiveInt = 300

    # Toggle orgviewer client.
    keycloak_orgviewer_client_enabled: bool = False
    # Token lifespan is 0 for now. We can remove this, once the RBAC reader
    # role works _and_ orgviewer implement keycloak in the frontend.
    keycloak_orgviewer_token_lifespan: PositiveInt = 60 * 60 * 24 * 365
    keycloak_orgviewer_client_secret: Optional[str]

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

    # Custom realm signing key (RSA). When set, this keypair replaces the
    # auto-generated one, e.g. in the SAML SP descriptor at
    # /auth/realms/mo/broker/saml/endpoint/descriptor
    keycloak_realm_rsa_private_key: Optional[str]
    keycloak_realm_rsa_certificate: Optional[str]

    # Specifies whether SSL is required for Keycloak requests. Can be one of
    # "all", "external" or "none". The options are further described here:
    # https://www.keycloak.org/docs/latest/server_installation/#_setting_up_ssl
    keycloak_ssl_required_mo: str = "all"

    @root_validator
    def optionally_required(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check that derived keys are set if master switch is set."""
        optionally_required_fields = {
            "keycloak_idp_enable": (
                "keycloak_idp_signing_certificate",
                "keycloak_idp_entity_id",
                "keycloak_idp_logout_service_url",
                "keycloak_idp_signon_service_url",
            ),
            "keycloak_orgviewer_client_enabled": ("keycloak_orgviewer_client_secret",),
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
