import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

from elv import dh

main_layout = dbc.Container(className=["pt-3"], children=[
    dbc.Row(
        dbc.Col(
            html.H3("Digitale Lastgangsanzeige")
        )
    ),
    html.Div(children=[
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='meter-selector',
                    options=[{'label': x, 'value': x} for x in dh.meters_in_database()],
                    value='',
                    placeholder='Zähler auswählen...',
                    clearable=False
                ),
                md=4,
                className="mb-2 mb-md-0"
            ),
            dbc.Col(
                html.Span(id='user-info'),
                md=4,
                className="mb-2 mb-md-0 align-center"
            ),
            dbc.Col(
                dbc.Button('Auswählen', id='select-meter', color='primary', block=True),
                md=4
            )
        ]),
        html.Hr()
    ], className="sticky-top bg-white pt-3"),
    html.Div(style={'display': 'none'}, id='content', children=[
        dbc.Card(
            dbc.CardBody(children=[
                dbc.Row(
                    dbc.Col(
                        html.H4("Übersicht", className="section-header"),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Loading(type="graph", children=[
                            dcc.Graph(id='graph-overview', config={'displaylogo': False, 'locale': 'de-DE'}),
                        ]),
                    ),
                    className="mb-2"
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Table(children=[
                            html.Thead([
                                html.Th("Minimum"),
                                html.Th("Maximum"),
                                html.Th("Durchschnitt"),
                                html.Th("Summe")
                            ]),
                            html.Tbody([
                                html.Td([html.Span(id='min-span-overview'), " kW"]),
                                html.Td([html.Span(id='max-span-overview'), " kW"]),
                                html.Td([html.Span(id='mean-span-overview'), " kW"]),
                                html.Td([html.Span(id='sum-span-overview'), " kW"]),
                            ])
                        ], responsive='md', className="mb-0")
                    )
                )
            ], className="mb-0"),
            className="mb-3"
        ),
        dbc.Card(
            dbc.CardBody(children=[
                dbc.Row(
                    dbc.Col(
                        html.H4("Tagesansicht", className="section-header"),
                    )
                ),
                dbc.Row(children=[
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id='date-picker-single',
                            display_format="DD.MM.YYYY",
                            month_format="MM.YYYY",
                            placeholder='Datum'
                        ),
                        xs=6, md=4
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id='detail-toggle',
                            options=[
                                {'label': 'Viertelstunden', 'value': 'quarter'},
                                {'label': 'Zählerwerte', 'value': 'meter'},
                                {'label': 'Standardlastprofil', 'value': 'dlp'},
                            ],
                            value=[],
                            placeholder="Optionen...",
                            multi=True
                        ),
                        xs=6, md=4
                    )
                ], justify='between', className="mb-3"),
                dbc.Row(children=[
                    dbc.Col(
                        dcc.Loading(type="graph", children=[
                            dcc.Graph(id='graph-detail', config={'displaylogo': False, 'locale': 'de-DE'}),
                        ])
                    )
                ], className="mb-2"),
                dbc.Row(children=[
                    dbc.Col(
                        dbc.Table(children=[
                            html.Thead([
                                html.Th("Minimum"),
                                html.Th("Maximum"),
                                html.Th("Durchschnitt"),
                                html.Th("Summe")
                            ]),
                            html.Tbody([
                                html.Td([html.Span(id='min-span-detail'), " kW"]),
                                html.Td([html.Span(id='max-span-detail'), " kW"]),
                                html.Td([html.Span(id='mean-span-detail'), " kW"]),
                                html.Td([html.Span(id='sum-span-detail'), " kW"]),
                            ])
                        ], responsive='md')
                    )
                ], className="mb-1"),
                dbc.Row(children=[
                    dbc.Col(
                        dash_table.DataTable(
                            id='table',
                            columns=[
                                {
                                    'name': "Zeitpunkt",
                                    'id': 'date_time'
                                }, {
                                    'name': "Zählerstand [kWh]",
                                    'id': 'obis_180'
                                }, {
                                    'name': "Zählervorschub [kWh / h]",
                                    'id': 'diff'
                                }, {
                                    'name': "Standardlastprofil [kWh / h]",
                                    'id': 'dlp'
                                }
                            ],
                            page_size=24,
                            sort_action='native',
                            cell_selectable=False,
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            },
                            style_cell={
                                'font-family': '"Raleway", "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'maxWidth': 0
                            }
                        ),
                        className="mx-3"
                    )
                ])
            ])
        )
    ])
])
