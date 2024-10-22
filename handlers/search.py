# Module Imports

# Custom Imports
import utils.response as res
import utils.db as dynamodb

# Other Imports
import tmdbsimple as tmdb
tmdb.API_KEY = '1933485589773c055a2064f3d1c0a208'

db = dynamodb.DynamoDBClient()

def get(event, _):
    query_params = event.get('queryStringParameters', {})
    query = query_params.get('query')
    page = query_params.get('page', 1)

    if (query is None):
        return res.build(400, {
            'message': 'Query must be provided.',
        })
    
    try:
        search = tmdb.Search()
        movies = search.movie(
            query=query,
            include_adult=False,
            page=page,
        )
    except Exception as e:
        return res.build(500, {
            'message': 'An error occurred whilst performing the search.',
            'exception': str(e),
        })

    return res.build(200, movies)