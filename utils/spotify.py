import json
import uuid
import spotipy

import utils.aws as aws
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheHandler

SPOTIFY_SCOPES = [
    'user-library-read',
    'playlist-read-collaborative',
    'playlist-read-private',
    'user-read-playback-state',
    'user-read-currently-playing',
    'user-modify-playback-state',
    'playlist-modify-private',
    'playlist-modify-public',
    'user-top-read',
    'user-read-recently-played',
    'user-read-playback-position'
]

class CustomCacheHandler(CacheHandler):
    def __init__(self, encoder_cls=None):
        self.encoder_cls = encoder_cls

    def get_cached_token(self):
        try:
            return json.loads(
                get_spotipy_credentials()['SPOTIPY_TEMPORARY_CREDENTIALS']
            )
        except Exception:
            return None
    
    def save_token_to_cache(self, token_info):
        try:
            current_spotipy_credentials = get_spotipy_credentials()
            secret_string = json.dumps({
                'SPOTIPY_CLIENT_ID': current_spotipy_credentials['SPOTIPY_CLIENT_ID'],
                'SPOTIPY_CLIENT_SECRET': current_spotipy_credentials['SPOTIPY_CLIENT_SECRET'],
                'SPOTIPY_REDIRECT_URI': current_spotipy_credentials['SPOTIPY_REDIRECT_URI'],
                'SPOTIPY_TEMPORARY_CREDENTIALS': json.dumps(token_info)
            })
        
            aws.secretsmanager.update_secret(
                SecretId='Spotipy',
                ClientRequestToken=str(uuid.uuid4()),
                SecretString=secret_string
            )

            print("Successfully saved token to AWS secrets manager.")
        except Exception:
            print("Error saving token")


def get_spotipy_credentials():
    try:
        return json.loads(aws.secretsmanager.get_secret_value(SecretId='Spotipy').get('SecretString'))
    except:
        print("An error occurred retrieving Spotipy credentials from AWS Secrets Manager.")
        return {}

def retrieve_spotify_client():

    try:
    
        spotipy_credentials = get_spotipy_credentials()

        spotipy_authentication_manager = spotipy.oauth2.SpotifyOAuth(
            scope=" ".join(SPOTIFY_SCOPES),
            client_id=spotipy_credentials['SPOTIPY_CLIENT_ID'],
            client_secret=spotipy_credentials['SPOTIPY_CLIENT_SECRET'],
            redirect_uri=spotipy_credentials['SPOTIPY_REDIRECT_URI'],
            cache_handler=CustomCacheHandler()
        )

        return spotipy.Spotify(
            auth_manager=spotipy_authentication_manager,
            requests_timeout=3,
            retries=2
        )
    except Exception:
        print("There was an error retrieving the spotify client SPOTIPY.")
        return None
