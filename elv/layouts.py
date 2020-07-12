import dash_core_components as dcc
import dash_html_components as html
import dash_table

from elv import figures, dh

layout = html.Div(children=[
    # html.Div(className="row", children=["Electric Load Viewer"]),
    html.Div(className="row", children=[
        html.Div(className="one columns", children=[html.Div()]),
        html.Div(className="ten columns", children=[
            html.Div(className="row", children=[
                html.H3("Übersicht"),
                html.Div([
                    dcc.Dropdown(
                        id='type-dropdown',
                        className="two columns",
                        options=[
                            {'label': 'Balken', 'value': 'bar'},
                            {'label': 'Linie', 'value': 'line'},
                        ],
                        value='bar',
                        clearable=False,
                        searchable=False
                    ),
                    dcc.Dropdown(
                        id='style-dropdown',
                        className="two columns",
                        options=[
                            {'label': 'Füllen', 'value': 'fill'},
                            {'label': 'Linie+Punkte', 'value': 'markers'},
                        ],
                        placeholder="Stil...",
                        value=[],
                        multi=True
                    )
                ])
            ]),
            html.Div(className="row", children=[
                dcc.Graph(id='graph-overview', figure=figures.create_overview_figure())
            ]),
            html.Div(className="row", children=[
                html.Div(className="three columns", children=[
                    html.P(children=[
                        html.Span("Zeitraum: "),
                        html.Span("", id="start-span"),
                        html.Span(" → "),
                        html.Span("", id="end-span")
                    ])
                ]),
                html.Div(className="two columns", children=[
                    html.P(children=[html.Span("Min.: "), html.Span("", id="min-span"), html.Span(" kWh")])
                ]),
                html.Div(className="two columns", children=[
                    html.P(children=[html.Span("Max.: "), html.Span("", id="max-span"), html.Span(" kWh")])
                ]),
                html.Div(className="two columns", children=[
                    html.P(children=[html.Span("Durchschn.: "), html.Span("", id="mean-span"), html.Span(" kWh")])
                ]),
                html.Div(className="two columns", children=[
                    html.P(children=[html.Span("Summe: "), html.Span("", id="sum-span"), html.Span(" kWh")])
                ]),
            ]),
            html.Div(className="row", children=[
                html.H3(style={'margin': 5}, children="Detailansicht"),
                dcc.DatePickerSingle(
                    id='date-picker-single',
                    min_date_allowed=dh.first_date(),
                    max_date_allowed=dh.last_date(),
                    initial_visible_month=dh.last_date(),
                    display_format="DD.MM.YYYY",
                    style={'display': "inline-block"}
                ),
                dcc.Checklist(
                    id='detail-toggle',
                    options=[
                        {'label': 'Viertelstunden', 'value': 'quarter'},
                        {'label': 'Zählerwerte', 'value': 'meter'},
                    ],
                    value=[],
                    labelStyle={'display': 'inline-block'},
                    style={'display': 'inline-block'}
                ),
                dcc.Graph(id='graph-detail'),
            ]),
            html.Div(className="row", children=[
                dash_table.DataTable(
                    id='table',
                    columns=[
                        {
                            'name': "Zeitpunkt",
                            'id': 'date_time'
                        },
                        {
                            'name': "Zählerstand",
                            'id': 'obis_180'
                        },
                        {
                            'name': "Zählervorschub",
                            'id': 'diff'
                        },
                    ],
                    page_size=24
                )
            ]),
        ]),
        html.Div(className="one columns", children=[html.Div()])
    ])
])
