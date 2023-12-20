import json

def build(code, body):
    return {
        'statusCode': code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body)
    }


def html(code, html):
    return {
        'statusCode': code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Content-Type': 'text/html'
        },
        'body': html
    }

def redirect(url):
    return {
        'statusCode': 302,
        'headers': {
            'Location': url
        }
    }

def error(err, body):
    return {
        'statusCode': 500,
         'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body)
    }