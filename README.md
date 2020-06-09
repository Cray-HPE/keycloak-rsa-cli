# keycloak-rsa-cli
Keycloak RSA CLI integration 

# 1. Configure the CLI
command: keycloak_cli configure
This will ask for:
  - keycloak_instance (e.g. mykc.com:800)
  - keycloak_realm (e.g. my-test-realm)
  - keycloak_client_id (i.e. client id where direct grant is set to the custom spi )
  - keycloak_username 
  - keycloak_password
  - rsa_username (i.e. username for the RSA instance)

# 2. Authenticate
Run keycloak_cli authenticate and enter the RSA password,
this will authenticate the user and store a set of tokens in ~/.kc/tokens.yml. 

# 3. Get Token
command: keycloak_cli token
If a refresh token is still valid when the above command is run then a new access token will be returned. If the refresh token is expired the CLI will alert the user and not provide a valid token



