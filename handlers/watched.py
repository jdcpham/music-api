# Module Imports
import operator
import simplejson as json
import datetime
import os
import decimal

# Custom Imports
import utils.response as res
import utils.aws as aws
import utils.db as dynamodb

# Other Imports
import tmdbsimple as tmdb
tmdb.API_KEY = '1933485589773c055a2064f3d1c0a208'

db = dynamodb.DynamoDBClient()

def get(event, context):

    movies = db.execute_scan('Movies')

    # Sort Entries
    movies.sort(key=operator.itemgetter('Timestamp'), reverse=True)

    for movie in movies:
        tmdb_movie = tmdb.Movies(movie['Identifier'])
        tmdb_movie_info = tmdb_movie.info()
        movie.update(tmdb_movie_info)
        movie['timestamp'] = movie['Timestamp']
        movie['rating'] = movie['Rating']
        movie.pop('Identifier')
        movie.pop('Rating')
        movie.pop('Timestamp')

    # movies = movies[:100]

    json_file = json.dumps(movies, cls=JSONEncoder)
    aws.s3.put_object(Body=json_file, Bucket="assets.johnpham.co.uk", Key="movies/recently-watched-{}.json".format(os.environ["STAGE"]), ACL="public-read")

    return res.build(200, json.loads(json_file))

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def post(event, _):

    body = json.loads(event.get('body', {}))

    id = body.get('id', 1210973)
    rating = body.get('rating')
    timestamp = body.get('timestamp', datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))

    if (rating > 10):
        return res.build(400, {
            'message': 'Rating must be 0-10',
        })

    try:
        record = {
            'id': id,
            'rating': rating,
            'timestamp': timestamp,
        }
        db.add_item('Movies', {
            'Identifier': id,
            'Rating': rating,
            'Timestamp': timestamp,
        })
        return res.build(200, record)

    except Exception as e:
        return res.build(500, {
            'message': 'Could not add movie.',
            'exception': str(e),
        })
