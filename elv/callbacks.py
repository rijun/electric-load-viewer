import re
from datetime import datetime
from typing import Optional, Tuple

from dash.dependencies import Input, Output, State

from elv import figures, dh
from elv.app import app


def date_from_range_slider(slider_data: dict) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse the range slider dict and return the start and end dates.

    :param slider_data: A datetime string in the correct format
    :return: datetime object if parsing was successful, otherwise None
    """
    if slider_data is None:
        return None, None
    elif "xaxis.range" in slider_data:  # Zoom via range slider
        start_date = slider_data['xaxis.range'][0]
        end_date = slider_data['xaxis.range'][1]
    elif "xaxis.range[1]" in slider_data:  # Zoom via selection in plot
        start_date = slider_data['xaxis.range[0]']
        end_date = slider_data['xaxis.range[1]']
    else:
        return None, None
    return date_from_str(start_date), date_from_str(end_date)


def date_from_str(date_str: str) -> Optional[datetime]:
    """
    Parse date_str and return a datetime object.

    The valid string formats are:
        "%Y-%m-%d %H:%M:%S.%f"
        "%Y-%m-%d %H:%M:%S"
        "%Y-%m-%d %H:%M"

    :param date_str: A datetime string in the correct format
    :return: datetime object if parsing was successful, otherwise None
    """
    # Get date format
    if re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+", date_str):
        date_fmt = "%Y-%m-%d %H:%M:%S.%f"
    elif re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", date_str):
        date_fmt = "%Y-%m-%d %H:%M:%S"
    elif re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", date_str):
        date_fmt = "%Y-%m-%d %H:%M"
    elif re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        date_fmt = "%Y-%m-%d"
    else:
        return None

    return datetime.strptime(date_str, date_fmt)


@app.callback(Output('user-info', 'children'),
              [Input('meter-selector', 'value')])
def update_user_info(meter_id):
    if meter_id == '':
        return "Bitte einen Zählpunkt auswählen..."
    m = dh.meter_info(meter_id)
    return f"{m[1]} {m[0]}, {m[2]} {m[3]}"


@app.callback(Output('content', 'style'),
              [Input('select-meter', 'n_clicks')],
              [State('meter-selector', 'value')])
def change_overview_visibility(n_clicks, meter):
    if n_clicks is None or meter == '':
        return {'display': 'none'}
    else:
        return {'display': 'block'}


@app.callback(Output('graph-overview', 'figure'),
              [Input('select-meter', 'n_clicks')],
              [State('meter-selector', 'value')])
def change_overview_figure(n_clicks, meter):
    if n_clicks is None or meter == '':
        return figures.empty_graph()
    return figures.overview_figure(meter)


@app.callback([Output('date-picker-single', 'initial_visible_month'),
               Output('date-picker-single', 'min_date_allowed'),
               Output('date-picker-single', 'max_date_allowed')],
              [Input('select-meter', 'n_clicks')],
              [State('meter-selector', 'value')])
def update_date_picker_limits(n_clicks, meter):
    if n_clicks is None or meter == '':
        return None, None, None
    return dh.last_date(meter), dh.first_date(meter), dh.last_date(meter)


@app.callback([Output('min-span-overview', 'children'),
               Output('max-span-overview', 'children'),
               Output('mean-span-overview', 'children'),
               Output('sum-span-overview', 'children')],
              [Input('graph-overview', 'relayoutData'),
               Input('select-meter', 'n_clicks')],
              [State('meter-selector', 'value')])
def update_stats_overview(relayout_data, n_clicks, meter):
    """Update minimum value display."""
    if n_clicks is None or meter == '':
        return '-', '-', '-', '-'
    start_date, end_date = date_from_range_slider(relayout_data)
    df = dh.overview(meter, start_date, end_date)
    return round(float(df['diff'].min()), 2), \
           round(float(df['diff'].max()), 2), \
           round(float(df['diff'].mean()), 2), \
           round(float(df['diff'].sum()), 2)


@app.callback(Output('date-picker-single', 'date'),
              [Input('graph-overview', 'clickData')],
              [State('meter-selector', 'value')])
def display_click_data(click_data, meter):
    """Change the date-picker-single date to the date selected on the overview graph."""
    if meter == '':
        return None
    elif not click_data:
        return dh.last_date(meter)
    else:
        return click_data['points'][0]['x']


@app.callback(Output('graph-detail', 'figure'),
              [Input('date-picker-single', 'date'),
               Input('detail-toggle', 'value')],
              [State('meter-selector', 'value')])
def update_detail_graph(date, selector, meter):
    """Update the detail graph."""
    if meter == '':
        return figures.empty_graph()
    m = True if 'meter' in selector else False
    q = True if 'quarter' in selector else False
    d = True if 'dlp' in selector else False
    return figures.detail_figure(meter, date, quarter=q, meter=m, default_load_profile=d)


@app.callback([Output('min-span-detail', 'children'),
               Output('max-span-detail', 'children'),
               Output('mean-span-detail', 'children'),
               Output('sum-span-detail', 'children')],
              [Input('date-picker-single', 'date'),
               Input('detail-toggle', 'value')],
              [State('meter-selector', 'value')])
def update_detail_stats(date, selector, meter):
    """Update the detail statistics."""
    if meter == '':
        return '-', '-', '-', '-'
    df = dh.day(meter, date)
    if 'quarter' in selector:
        rule = '15T'
    else:
        rule = '60T'
    df = df.resample(rule).agg({'obis_180': 'first', 'diff': 'sum', 'interpolation': 'first'})
    return round(float(df['diff'].min()), 2), \
           round(float(df['diff'].max()), 2), \
           round(float(df['diff'].mean()), 2), \
           round(float(df['diff'].sum()), 2)


@app.callback(Output('table', 'data'),
              [Input('date-picker-single', 'date'),
               Input('detail-toggle', 'value')],
              [State('meter-selector', 'value')])
def update_table_data(date, selector, meter):
    """Update the detail table."""
    if meter == '':
        return
    q = True if 'quarter' in selector else False
    return figures.table_data(meter, date, quarter=q)


@app.callback(Output('table', 'columns'),
              [Input('detail-toggle', 'value')])
def update_table_heading(selector):
    """Update the detail table."""
    return [
        {
            'name': "Zeitpunkt",
            'id': 'date_time'
        }, {
            'name': "Zählerstand [kWh]",
            'id': 'obis_180'
        }, {
            'name': f"Zählervorschub {'[kWh / 15 min]' if 'quarter' in selector else '[kWh / h]'}",
            'id': 'diff'
        }, {
            'name': f"Standardlastprofil {'[kWh / 15 min]' if 'quarter' in selector else '[kWh / h]'}",
            'id': 'dlp'
        }
    ]
