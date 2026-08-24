# Keycloak Realm Builder

The Terraform-based realm builder used for OS2mo and friends.

## Development

The development stack can be started with:

```
docker-compose up -d --build
```

This starts an instance of Keycloak, and runs the realm builder against it.

On changes, the realm builder can subsequently be run with:

```
docker-compose up --build keycloak-gen
```

This will show the output from applying the changes with Terraform, and exit.

## Documentation

This section will explain the different components involved in our Keycloak configuration

The headers have corresponding comments in `keycloak.tf`

### Realms

We create realms for each major application area, so as to keep the auth for OS2mo and LoRa completely separate.

### Roles

Various roles for the OS2mo realm, providing fine-grained access control for the various API operations.

Currently only `owner` and `admin` have been implemented.

### Clients

Various clients for interacting with Keycloak under the different realms.

Each application should have its own client.

### Users

Users for the OS2mo realm. These are only used if the IdP broker is disabled.

### IdP broker

An SAML IdP broker for connecting with ADFS.

### IdP RBAC role mappers

Maps attributes from the SAML assertion, whenever a user successfully logs in using the IdP broker. The attributes here correspond to the claims that have been configured for ADFS during RBAC setup.

### Login flow

This is a simplified version of the default login flow in Keycloak. The login flow is invoked whenever a user successfully logs in through the IdP broker in Keycloak.

The login flow automatically creates users in Keycloaks user database if not present. The flow ignores missing attributes (name, email), as we have no need for those, and as those details aren't present on the SAML assertions we receive.

### Browser flow

A simplified version of the default browser flow. The browser flow is used whenever a user interacts with Keycloak.

The browser flow first checks for the presence of a cookie, and alternatively redirects the users to the IdP broker.
