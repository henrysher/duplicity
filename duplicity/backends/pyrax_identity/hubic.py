#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Gu1
# Licensed under the MIT license

import os
import pyrax
import pyrax.exceptions as exc
import requests
import re
import urlparse
import ConfigParser
import time
from pyrax.base_identity import BaseIdentity, Service
from requests.compat import quote, quote_plus


OAUTH_ENDPOINT = "https://api.hubic.com/oauth/"
API_ENDPOINT = "https://api.hubic.com/1.0/"
TOKENS_FILE = os.path.expanduser("~/.hubic_tokens")


class BearerTokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, req):
        req.headers['Authorization'] = 'Bearer ' + self.token
        return req


class HubicIdentity(BaseIdentity):

    def _get_auth_endpoint(self):
        return ""

    def set_credentials(self, email, password, client_id,
                        client_secret, redirect_uri,
                        authenticate=False):
        """Sets the username and password directly."""
        self._email = email
        self._password = password
        self._client_id = client_id
        self.tenant_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        if authenticate:
            self.authenticate()

    def _read_credential_file(self, cfg):
        """
        Parses the credential file with Rackspace-specific labels.
        """
        self._email = cfg.get("hubic", "email")
        self._password = cfg.get("hubic", "password")
        self._client_id = cfg.get("hubic", "client_id")
        self.tenant_id = self._client_id
        self._client_secret = cfg.get("hubic", "client_secret")
        self._redirect_uri = cfg.get("hubic", "redirect_uri")

    def _parse_error(self, resp):
        if 'location' not in resp.headers:
            return None
        query = urlparse.urlsplit(resp.headers['location']).query
        qs = dict(urlparse.parse_qsl(query))
        return {'error': qs['error'], 'error_description': qs['error_description']}

    def _get_access_token(self, code):
        r = requests.post(
            OAUTH_ENDPOINT + 'token/',
            data={
                'code': code,
                'redirect_uri': self._redirect_uri,
                'grant_type': 'authorization_code',
            },
            auth=(self._client_id, self._client_secret)
        )
        if r.status_code != 200:
            try:
                err = r.json()
                err['code'] = r.status_code
            except:
                err = {}

            raise exc.AuthenticationFailed("Unable to get oauth access token, "
                                           "wrong client_id or client_secret ? (%s)" %
                                           str(err))

        oauth_token = r.json()

        config = ConfigParser.ConfigParser()
        config.read(TOKENS_FILE)

        if not config.has_section("hubic"):
            config.add_section("hubic")

        if oauth_token['access_token'] is not None:
            config.set("hubic", "access_token", oauth_token['access_token'])
            with open(TOKENS_FILE, 'wb') as configfile:
                config.write(configfile)
        else:
            raise exc.AuthenticationFailed(
                "Unable to get oauth access token, wrong client_id or client_secret ? (%s)" %
                str(err))

        if oauth_token['refresh_token'] is not None:
            config.set("hubic", "refresh_token", oauth_token['refresh_token'])
            with open(TOKENS_FILE, 'wb') as configfile:
                config.write(configfile)
        else:
            raise exc.AuthenticationFailed("Unable to get the refresh token.")

        # removing username and password from .hubic_tokens
        if config.has_option("hubic", "email"):
            config.remove_option("hubic", "email")
            with open(TOKENS_FILE, 'wb') as configfile:
                config.write(configfile)
            print "username has been removed from the .hubic_tokens file sent to the CE."
        if config.has_option("hubic", "password"):
            config.remove_option("hubic", "password")
            with open(TOKENS_FILE, 'wb') as configfile:
                config.write(configfile)
            print "password has been removed from the .hubic_tokens file sent to the CE."

        return oauth_token

    def _refresh_access_token(self):

        config = ConfigParser.ConfigParser()
        config.read(TOKENS_FILE)
        refresh_token = config.get("hubic", "refresh_token")

        if refresh_token is None:
            raise exc.AuthenticationFailed("refresh_token is null. Not acquiered before ?")

        success = False
        max_retries = 20
        retries = 0
        sleep_time = 30
        max_sleep_time = 3600

        while retries < max_retries and not success:
            r = requests.post(
                OAUTH_ENDPOINT + 'token/',
                data={
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token',
                },
                auth=(self._client_id, self._client_secret)
            )
            if r.status_code != 200:
                if r.status_code == 509:
                    print "status_code 509: attempt #", retries, " failed"
                    retries += 1
                    time.sleep(sleep_time)
                    sleep_time = sleep_time * 2
                    if sleep_time > max_sleep_time:
                        sleep_time = max_sleep_time
                else:
                    try:
                        err = r.json()
                        err['code'] = r.status_code
                    except:
                        err = {}

                    raise exc.AuthenticationFailed(
                        "Unable to get oauth access token, wrong client_id or client_secret ? (%s)" %
                        str(err))
            else:
                success = True

        if not success:
            raise exc.AuthenticationFailed(
                "All the attempts failed to get the refresh token: "
                "status_code = 509: Bandwidth Limit Exceeded")

        oauth_token = r.json()

        if oauth_token['access_token'] is not None:
            return oauth_token
        else:
            raise exc.AuthenticationFailed("Unable to get oauth access token from json")

    def authenticate(self):
        config = ConfigParser.ConfigParser()
        config.read(TOKENS_FILE)

        if config.has_option("hubic", "refresh_token"):
            oauth_token = self._refresh_access_token()
        else:
            r = requests.get(
                OAUTH_ENDPOINT + 'auth/?client_id={0}&redirect_uri={1}'
                '&scope=credentials.r,account.r&response_type=code&state={2}'.format(
                    quote(self._client_id),
                    quote_plus(self._redirect_uri),
                    pyrax.utils.random_ascii()  # csrf ? wut ?..
                ),
                allow_redirects=False
            )
            if r.status_code != 200:
                raise exc.AuthenticationFailed("Incorrect/unauthorized "
                                               "client_id (%s)" % str(self._parse_error(r)))

            try:
                from lxml import html as lxml_html
            except ImportError:
                lxml_html = None

            if lxml_html:
                oauth = lxml_html.document_fromstring(r.content).xpath('//input[@name="oauth"]')
                oauth = oauth[0].value if oauth else None
            else:
                oauth = re.search(
                    r'<input\s+[^>]*name=[\'"]?oauth[\'"]?\s+[^>]*value=[\'"]?(\d+)[\'"]?>',
                    r.content)
                oauth = oauth.group(1) if oauth else None

            if not oauth:
                raise exc.AuthenticationFailed("Unable to get oauth_id from authorization page")

            if self._email is None or self._password is None:
                raise exc.AuthenticationFailed("Cannot retrieve email and/or password. "
                                               "Please run expresslane-hubic-setup.sh")

            r = requests.post(
                OAUTH_ENDPOINT + 'auth/',
                data={
                    'action': 'accepted',
                    'oauth': oauth,
                    'login': self._email,
                    'user_pwd': self._password,
                    'account': 'r',
                    'credentials': 'r',

                },
                allow_redirects=False
            )

            try:
                query = urlparse.urlsplit(r.headers['location']).query
                code = dict(urlparse.parse_qsl(query))['code']
            except:
                raise exc.AuthenticationFailed("Unable to authorize client_id, "
                                               "invalid login/password ?")

            oauth_token = self._get_access_token(code)

        if oauth_token['token_type'].lower() != 'bearer':
            raise exc.AuthenticationFailed("Unsupported access token type")

        r = requests.get(
            API_ENDPOINT + 'account/credentials',
            auth=BearerTokenAuth(oauth_token['access_token']),
        )

        swift_token = r.json()
        self.authenticated = True
        self.token = swift_token['token']
        self.expires = swift_token['expires']
        self.services['object_store'] = Service(self, {
            'name': 'HubiC',
            'type': 'cloudfiles',
            'endpoints': [
                {'public_url': swift_token['endpoint']}
            ]
        })
        self.username = self.password = None
