import uuid

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from elv import callbacks
from elv.app import app
from elv.layouts import main_layout

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """Display page, necessary when using multi-module apps."""
    session_id = str(uuid.uuid4())  # Currently unused, left for future reference
    if pathname == '/':
        return html.Div(children=[
            html.Div(session_id, id='session-id', style={'display': 'none'}),
            main_layout
        ])
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
