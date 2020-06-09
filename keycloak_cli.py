import click
import requests
import yaml 
import json

from datetime import datetime
import os
path = os.path

TOKEN_DIR = '~/.kc'
TOKEN_FILE = 'tokens.yml'
CONFIG_FILE = 'config.yml'
NO_TOKEN = 'none'
_token_dir = path.expanduser(TOKEN_DIR)
_token_path = path.expanduser(path.join(TOKEN_DIR, TOKEN_FILE))
_config_path = path.expanduser(path.join(TOKEN_DIR, CONFIG_FILE))


@click.group()
def cli():
    pass

@click.command('authenticate', short_help='Authenticates user.')
@click.option('--rsa_tokencode', prompt='Enter your RSA tokencode', 
                help='RSA tokencode', hide_input=True)
def authenticate(rsa_tokencode): 
    authenticated = request_tokens(rsa_tokencode)
    if authenticated == NO_TOKEN:
        click.echo("Authentication invalid.")

@click.command('token', short_help='Refresh authentication.')
def token():
    authenticated = refresh()
    if authenticated == NO_TOKEN:
        click.echo("Tokens are expired. Please reauthenticate.")
    else:
        click.echo(refresh())

def refresh():
    try:
        if path.exists(_token_dir):
            if path.exists(_token_path):
                with open(_token_path, 'r') as fp:
                    tokens = yaml.safe_load(fp)
                    refresh_token = tokens['refresh_token']
                    # check expiration time
                    if refresh_token:
                        refresh_expires_in = tokens['refresh_expires_in']
                        generated_at = tokens['generated_at']
                        now = int(datetime.now().strftime("%s"))
                        if(generated_at + refresh_expires_in > now):
                            return request_tokens(refresh_token=refresh_token)
    except Exception as e:
       return NO_TOKEN
    return NO_TOKEN

# check if valid time on refresh and refresh tokens
def request_tokens(rsa_tokencode=None, refresh_token=None):
    try:
        if path.exists(_token_dir):
            if path.exists(_config_path):
                with open(_config_path, 'r') as fp:
                    config = yaml.safe_load(fp)
                    # found in .kc/config
                    keycloak_instance  = config['keycloak_instance']
                    keycloak_realm     = config['keycloak_realm']
                    keycloak_client_id = config['keycloak_client_id']
                    keycloak_username  = config['keycloak_username']
                    keycloak_password  = config['keycloak_password'] 
                    rsa_username       = config['rsa_username']

                    keycloak_url = f'{keycloak_instance}/auth/realms/{keycloak_realm}/protocol/openid-connect/token'
                    if refresh_token:
                        data = {
                            'grant_type': 'refresh_token',
                            'client_id': keycloak_client_id,
                            'refresh_token': refresh_token
                        }
                    else:
                        data = {
                        'grant_type': 'password',
                            'client_id': keycloak_client_id,
                            'scope': 'openid',
                            'username': keycloak_username,
                            'password': keycloak_password,
                            'rsa_username': rsa_username,
                            'rsa_otp': rsa_tokencode,
                        }
                    r = requests.post(keycloak_url, data=data)
                    if r.status_code == requests.codes.ok:
                        response = json.loads(r.text)
                        return write_tokens(response)
    except Exception:
        return NO_TOKEN
    return NO_TOKEN

def write_tokens(response):
    with open(_token_path, 'w') as t_fp:
        tokens = {
            'access_token': response['access_token'],
            'refresh_token': response['refresh_token'],
            'expires_in': response['expires_in'],
            'refresh_expires_in': response['refresh_expires_in'],
            'generated_at': int(datetime.now().strftime("%s"))
        }
        yaml.dump(tokens, t_fp)
        return response['access_token']

## config 
@click.command('configure', short_help='Creates config file for auth.')
@click.option('--keycloak_instance', prompt='Enter your Keycloak instance', help='Keycloak instance')
@click.option('--keycloak_realm', prompt='Enter your Keycloak realm', help='Keycloak realm')
@click.option('--keycloak_client_id', prompt='Enter your Keycloak client id', help='Keycloak client id')
@click.option('--keycloak_username', prompt='Enter your Keycloak username', help='Keycloak username')
@click.option('--keycloak_password', prompt='Enter your Keycloak password',
                help='Keycloak username', hide_input=True)
@click.option('--rsa_username', prompt='Enter RSA username', help='RSA username')
def create_config(keycloak_instance, keycloak_realm,  keycloak_client_id,
                  keycloak_username, keycloak_password, rsa_username):
    if(not path.exists(_token_dir)):
        os.mkdir(_token_dir)

    with open(_config_path, 'w') as fp:
        config = {
            'keycloak_instance': keycloak_instance,
            'keycloak_realm': keycloak_realm,
            'keycloak_client_id': keycloak_client_id,
            'keycloak_username': keycloak_username,
            'keycloak_password': keycloak_password,
            'rsa_username': rsa_username,
        }
        yaml.dump(config, fp)


cli.add_command(authenticate)
cli.add_command(create_config)
cli.add_command(token)