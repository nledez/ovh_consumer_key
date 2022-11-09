#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import platform
import sys
import ovh
import configparser

# Define default value
DEFAULT_ENDPOINT = 'ovh-eu'
HELP_CREDENTIAL_NEVER_SHOW = True

# Define default access_rules
access_rules_full = [
    {'method': 'GET', 'path': '/*'},
    {'method': 'POST', 'path': '/*'},
    {'method': 'PUT', 'path': '/*'},
    {'method': 'DELETE', 'path': '/*'}
]


def show_help_for_application_credentials():
    '''
    Show help to generate application key & secret
    '''
    global HELP_CREDENTIAL_NEVER_SHOW

    if HELP_CREDENTIAL_NEVER_SHOW:
        print('Go to https://eu.api.ovh.com/createApp/')
        print('Fill form get values and fill ovh.conf with:')
        print('application_key = ')
        print('application_secret = ')
        HELP_CREDENTIAL_NEVER_SHOW = False


def generate_config_file():
    '''
    Generate a ovh.conf if not exist
    '''
    global HELP_CREDENTIAL_NEVER_SHOW
    need_exit = False

    config = configparser.ConfigParser()
    config.read('ovh.conf')
    if 'default' not in config.sections():
        config['default'] = {}
    if 'endpoint' not in config['default'].keys():
        config['default']['endpoint'] = DEFAULT_ENDPOINT
    endpoint = config['default']['endpoint']
    if endpoint not in config.sections():
        config[endpoint] = {}
        if HELP_CREDENTIAL_NEVER_SHOW:
            show_help_for_application_credentials()
            need_exit = True
    if 'application_key' not in config[endpoint]:
        if HELP_CREDENTIAL_NEVER_SHOW:
            show_help_for_application_credentials()
            need_exit = True
    if 'application_secret' not in config[endpoint]:
        if HELP_CREDENTIAL_NEVER_SHOW:
            show_help_for_application_credentials()
            need_exit = True

    with open('ovh.conf', 'w') as configfile:
        config.write(configfile)

    if need_exit:
        print('Now I quit')
        sys.exit(1)


def generate_token(access_rules):
    '''
    Generate token with access_rules
    '''
    validation = client.request_consumerkey(access_rules)

    # Show the URL the create consumerkey
    print('Please visit {} to authenticate'.format(validation['validationUrl']))
    # If you are on darwin open it in browser
    if platform.system() == 'Darwin':
        os.system('open {}'.format(validation['validationUrl']))
    input('and press Enter to continue...')

    # Print nice welcome message to check if it's works
    print('Welcome {}'.format(client.get('/me')['firstname']))

    # Print consumerkey for safety
    # print('Btw, your "consumerKey" is "{}"'.format(validation['consumerKey']))
    print('Your "consumerKey" is saved in ovh.conf')

    # Add consumer_key to ovh.conf
    config = configparser.ConfigParser()
    config.read('ovh.conf')
    endpoint = config['default']['endpoint']
    config[endpoint]['consumer_key'] = validation['consumerKey']

    with open('ovh.conf', 'w') as configfile:
        config.write(configfile)


def write_ovh_sh():
    config = configparser.ConfigParser()
    config.read('ovh.conf')
    endpoint = config['default']['endpoint']

    f = open('ovh.sh', 'w')
    f.write('export OVH_ENDPOINT={}\n'.format(endpoint))
    f.write('export OVH_APPLICATION_KEY={}\n'.format(config[endpoint]['application_key']))
    f.write('export OVH_APPLICATION_SECRET={}\n'.format(config[endpoint]['application_secret']))
    f.write('export OVH_CONSUMER_KEY={}\n'.format(config[endpoint]['consumer_key']))
    f.close()

# create a client using configuration or generate ovh.conf
try:
    client = ovh.Client()
except ovh.exceptions.InvalidRegion:
    print('Need to generate default ovh.conf')
    generate_config_file()

# Try consumer_key or generate new one
try:
    me = client.get('/me')
    print('Welcome {} nothing to do'.format(me['firstname']))
except ovh.exceptions.InvalidKey:
    print('Need a valid consumer_key')
    generate_token(access_rules_full)
except ovh.exceptions.InvalidCredential:
    print('Need a valid consumer_key')
    generate_token(access_rules_full)

write_ovh_sh()
