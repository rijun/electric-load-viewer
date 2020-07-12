import re
from datetime import datetime
from typing import Optional, Tuple

from dash.dependencies import Input, Output

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
    elif "xaxis.range" in slider_data:      # Zoom via range slider
        start_date = slider_data['xaxis.range'][0]
        end_date = slider_data['xaxis.range'][1]
    elif "xaxis.range[1]" in slider_data:   # Zoom via selection in plot
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


@app.callback(Output('graph-overview', 'figure'),
              [Input('type-dropdown', 'value'),
               Input('style-dropdown', 'value')])
def change_overview_figure(plot_type, style):
    fill = True if 'fill' in style else False
    markers = True if 'markers' in style else False
    return figures.create_overview_figure(kind=plot_type, fill=fill, markers=markers)


@app.callback(Output('start-span', 'children'),
              [Input('graph-overview', 'relayoutData')])
def update_start(relayout_data):
    """Update start date display."""
    start_date, _ = date_from_range_slider(relayout_data)
    start_date = dh.first_date() if start_date is None else start_date
    return start_date.strftime("%d.%m.%Y")


@app.callback(Output('end-span', 'children'),
              [Input('graph-overview', 'relayoutData')])
def update_start(relayout_data):
    """Update end date display."""
    _, end_date = date_from_range_slider(relayout_data)
    end_date = dh.last_date() if end_date is None else end_date
    return end_date.strftime("%d.%m.%Y")


@app.callback(Output('min-span', 'children'),
              [Input('graph-overview', 'relayoutData')])
def update_min(relayout_data):
    """Update minimum value display."""
    start_date, end_date = date_from_range_slider(relayout_data)
    return dh.min(start_date, end_date)


@app.callback(Output('max-span', 'children'),
              [Input('graph-overview', 'relayoutData')])
def update_max(relayout_data):
    """Update maximum value display."""
    start_date, end_date = date_from_range_slider(relayout_data)
    return dh.max(start_date, end_date)


@app.callback(Output('mean-span', 'children'),
              [Input('graph-overview', 'relayoutData')])
def update_mean(relayout_data):
    """Update mean value display."""
    start_date, end_date = date_from_range_slider(relayout_data)
    return dh.mean(start_date, end_date)


@app.callback(Output('sum-span', 'children'),
              [Input('graph-overview', 'relayoutData')])
def update_sum(relayout_data):
    """Update max value display."""
    start_date, end_date = date_from_range_slider(relayout_data)
    return dh.sum(start_date, end_date)


@app.callback(Output('date-picker-single', 'date'),
              [Input('graph-overview', 'clickData')])
def display_click_data(click_data):
    """Change the date-picker-single date to the date selected on the overview graph."""
    if not click_data:
        return dh.last_date()
    return click_data['points'][0]['x']


@app.callback(Output('graph-detail', 'figure'),
              [Input('date-picker-single', 'date'),
               Input('detail-toggle', 'value')])
def update_day(date, selector):
    """Update the detail graph."""
    m = True if 'meter' in selector else False
    q = True if 'quarter' in selector else False
    return figures.create_detail_figure(date, quarter=q, meter=m)


@app.callback(Output('table', 'data'),
              [Input('date-picker-single', 'date'),
               Input('detail-toggle', 'value')])
def update_table(date, selector):
    """Update the detail table."""
    q = True if 'quarter' in selector else False
    return figures.create_table_data(date, quarter=q)
