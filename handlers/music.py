# Module Imports
import json
import datetime
import os

# Custom Imports
import utils.response as res
import utils.spotify as spotify
import utils.aws as aws

def process_artist(artist):
    return {
        'url': artist['external_urls']['spotify'],
        'name': artist['name']
    }


def process_item(item):
    album = {}
    artists = []
    track = {}

    if 'track' not in item:
        album = item['album']
        artists = item['artists']
        track = item
    else:
        album = item['track']['album']
        artists = item['track']['artists']
        track = item['track']
    return {
        'playedAt': item.get('played_at'),
        'album': {
            'name': album['name'],
            'image': album['images'][0]['url'],
            'type': album['album_type'],
            'url': album['external_urls']['spotify']
        },
        'artists': list(map(process_artist, artists)),
        'track': {
            'name': track.get('name'),
            'previewUrl': track['preview_url'],
            'duration': track['duration_ms'],
            'url': track['external_urls']['spotify'],
            'explicit': track['explicit'],
            'id': track['id']
        }
    }


def recently_played_tracks(event, context):
    try:
        spotify_client = spotify.retrieve_spotify_client()
        recently_played = spotify_client.current_user_recently_played(limit=15)

        response = {
            'timestamp': datetime.datetime.utcnow().isoformat() + "Z",
            'items': list(map(process_item, recently_played.get('items', [])))
        }

    except Exception as e:

        return res.build(500, {
            'error': True,
            'message': str(e),
        })
    
    json_file = json.dumps(response)
    aws.s3.put_object(Body=json_file, Bucket="assets.johnpham.co.uk", Key="music/recently-played-{}.json".format(os.environ["STAGE"]), ACL="public-read")

    return res.build(200, response)

def search_track(event, context):
    query_params = event['queryStringParameters']
    query = query_params.get('query')

    try:
        spotify_client = spotify.retrieve_spotify_client()
        search_results = spotify_client.search(query, 15)
        response = list(map(process_item, search_results['tracks']['items']))

    except Exception as e:

        return res.build(500, {
            'error': True,
            'message': str(e),
        })

    return res.build(200, response)

def suggest_track(event, context):
    body = event.get('body', {})
    if (body is not dict): body = json.loads(body)

    track_id = body.get('trackId')
    forename = body.get('forename')
    surname = body.get('surname')
    email = body.get('email')