import dash
from flask_caching import Cache

simple_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_THRESHOLD': 50
}

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
cache = Cache(app.server, config=simple_config)
app.config['suppress_callback_exceptions'] = True
server = app.server
