# Auth code from https://github.com/plamere/SmarterPlaylists/blob/master/server/spotify_auth.py

import os
import time
import json
import requests
import redis
from spotipy import oauth2

SPOTIFY_REDIRECT_URI = 'http://localhost:8080/'
scope = 'playlist-modify-public user-top-read'


class SpotifyAuth(object):

    def __init__(self, r=None):
        if r:
            self.r = r
        else:
            self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.EXPIRES_THRESHOLD = 120
        self.client_id = os.environ['SPOTIFY_CLIENT_ID']
        self.client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
        self.client_redirect_uri = SPOTIFY_REDIRECT_URI
        self.oauth = oauth2.SpotifyOAuth(self.client_id, self.client_secret, self.client_redirect_uri, scope=scope)

        if not self.client_id or not self.client_secret or not self.client_redirect_uri:
            raise Exception('Missing SPOTIPY credentials in the environment')

    def get_fresh_token(self, code):
        now = time.time()
        token = self._get_token(code)
        if token:
            print('Found token in cache')
            if (token['expires_at'] - now) < self.EXPIRES_THRESHOLD:
                token = self._refresh_token(token)
                if token:
                    self._add_token(code, token)
        else:
            print('No token in cache, fetching new token')
            token = self._add_auth_code(code)

        return token

    def get_authorize_url(self):
        return self.oauth.get_authorize_url()

    def _add_auth_code(self, auth_code):
        token = self._get_new_token(auth_code)
        if token:
            token = self._add_token(auth_code, token)
        return token

    def _add_token(self, code, token):
        now = time.time()
        token['expires_at'] = int(now) + token['expires_in']
        user_info = self._me(token)
        if user_info and 'id' in user_info:
            token['user_id'] = user_info['id']
            token['user_name'] = user_info['display_name']
            # could key by user info
            user = token['user_id']
            self._put('token:' + code, token)
        else:
            return None
        return token

    def _get_new_token(self, auth_code):
        return self.oauth.get_access_token(auth_code)

    def _get_token(self, code):
        key = 'token:' + code
        js = self._get(key)
        return js

    def _refresh_token(self, token):
        token_info = self.oauth.refresh_access_token(token['refresh_token'])
        if 'refresh_token' not in token_info:
            token_info['refresh_token'] = token['refresh_token']
        return token_info

    def _me(self, token):
        me_info = self._spget('me', token['access_token'])
        return me_info

    def _spget(self, method, auth, params=None):
        prefix = 'https://api.spotify.com/v1/'
        args = dict(params=params)
        url = prefix + method
        headers = {'Authorization': f'Bearer {auth}',
                   'Content-Type': 'application/json'}

        r = requests.get(url, headers=headers, **args)

        if len(r.text) > 0:
            results = r.json()
            return results
        else:
            return None

    def _get(self, key):
        js = self.r.get(key)
        if js:
            return json.loads(js)
        else:
            return None

    def _put(self, key, val):
        js = json.dumps(val)
        self.r.set(key, js)

    def delete_auth(self, code):
        key = 'token:' + code
        self.r.delete(key)
