import dash_core_components as dcc
import dash_html_components as html
import dash_table

from elv import figures, dh

main_layout = html.Div(children=[
    # html.Div(className="row", children=["Electric Load Viewer"]),
    html.Div(className="container", style={'padding-top': '2rem'}, children=[
        html.H3("Digitale Lastgangsanzeige"),
        html.Hr(),
        html.Form(className="header-bar", children=[
            html.Div(className="row", children=[
                dcc.Dropdown(
                    id='meter-selector',
                    className="four columns",
                    options=[
                        {'label': '1ESY000222449', 'value': '1ESY000222449'}
                    ],
                    value='NYC'
                ),
                html.Div("Max Mustermann, 44149 Dortmund", className="four columns user-display"),
                html.Button('Auswählen', id='submit-val', className="four columns button-primary"),
            ]),
        ]),
        html.Hr(),
        html.H4("Übersicht", className="section-header"),
        dcc.Graph(
            id='graph-overview',
            figure=figures.create_overview_figure(),
            config={'displaylogo': False}
        ),
        html.Table(className="u-full-width", children=[
            html.Thead([
                html.Th("Minimum"),
                html.Th("Maximum"),
                html.Th("Durchschnitt"),
                html.Th("Summe")
            ]),
            html.Tbody([
                html.Td([html.Span(id='min-span'), " kW"]),
                html.Td([html.Span(id='max-span'), " kW"]),
                html.Td([html.Span(id='mean-span'), " kW"]),
                html.Td([html.Span(id='sum-span'), " kW"]),
            ])
        ]),
        html.Div(className="row button-container", children=[
            dcc.Dropdown(
                id='type-dropdown',
                className="four columns",
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
                className="four columns",
                options=[
                    {'label': 'Füllen', 'value': 'fill'},
                    {'label': 'Linie+Punkte', 'value': 'markers'},
                ],
                placeholder="Stil...",
                value=[],
                multi=True
            )
        ]),
        html.Hr(),
        html.H4("Tagesansicht", className="section-header"),
        html.Div(style={'margin': '1rem 0', 'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}, children=[
            html.Div(children=[
                dcc.DatePickerSingle(
                    id='date-picker-single',
                    className="div-vert-align",
                    min_date_allowed=dh.first_date(),
                    max_date_allowed=dh.last_date(),
                    initial_visible_month=dh.last_date(),
                    display_format="DD.MM.YYYY",
                    style={'height': '36px'}
                )
            ]),
            html.Div(children=[
                dcc.Checklist(
                    id='detail-toggle',
                    options=[
                        {'label': 'Viertelstunden', 'value': 'quarter'},
                        {'label': 'Zählerwerte', 'value': 'meter'},
                        {'label': 'Standardlastprofil', 'value': 'dlp'},
                    ],
                    value=[]
                )
            ])
        ]),
        dcc.Graph(id='graph-detail', config={'displaylogo': False}),
        html.Br(),
        html.Div(className="row", children=[
            dash_table.DataTable(
                id='table',
                columns=[
                    {
                        'name': "Zeitpunkt",
                        'id': 'date_time'
                    },
                    {
                        'name': "Zählerstand [kWh]",
                        'id': 'obis_180'
                    },
                    {
                        'name': "Zählervorschub [kWh / h]",
                        'id': 'diff'
                    },
                ],
                page_size=24,
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'date_time'},
                        'textAlign': 'left'
                    }
                ],
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
                    'font-family': '"Raleway", "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif'
                }
            )
        ])
    ])
])
