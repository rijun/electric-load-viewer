import arrow
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from elv import dh
from dlp import DefaultLoadProfile


def yearly_energy_usage(meter_id):
    """
    Calculate the previous yearly energy usage.

    If the number of days in the dataset is > 365 (one year), the sum of all meter values for the last 365 days is
    returned. Otherwise, the currently stored meter values are summed up and interpolated to the a duration of one
    year.

    :param meter_id: The ID of the meter in question
    :return: The yearly energy usage
    """
    df = dh.overview(meter_id)
    if df.index.size < 365:  # Dataset smaller than one year
        energy_used = df.sum(axis=1).div(4).sum()
        energy_used = energy_used / df.index.size * 365  # Scale to one year
    else:
        energy_used = df.iloc[-366:-1].sum(axis=1).div(
            4).sum()  # Calculate sum of last 365 values
    return round(energy_used / 1000, 2)  # Convert Wh to kWh


def empty_graph():
    """Return a empty figure as a placeholder."""
    fig = make_subplots()
    fig.update_layout(
        xaxis={
            'visible': False
        },
        yaxis={'visible': False},
        margin=dict(t=25, b=38, l=0, r=0),
        modebar={'orientation': 'v'},
        plot_bgcolor='#FFFFFF'
    )
    return fig


def overview_figure(meter_id):
    """
    Return a Plotly GraphObj showing the full load profile of a given meter.

    :param meter_id: The meter whose profile is to be plotted
    :return: List of dictionaries with the keys date_time, obis_180 and diff
    """
    # Create empty figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df = dh.overview(meter_id)

    # Set x-axis title
    fig.update_xaxes(title_text="Datum")

    # Set y-axes titles
    fig.update_yaxes(title_text="kWh / Tag")

    x_values = df.index.date

    # Color interpolation bars if necessary
    if df['interpolation'].any():
        colors = df['interpolation'].map({False: '#007BFF', True: '#EF553B'})
    else:
        colors = '#007BFF'

    # Add trace
    fig.add_trace(
        go.Bar(x=x_values, y=df['diff'], name="Lastgang", hovertemplate="%{y} kWh / Tag", marker_color=colors)
    )

    # Set title
    fig.layout.title = {
        'text': f"{arrow.get(df.index.min()).format('D. MMMM YYYY', locale='de_DE')} -- "
                f"{arrow.get(df.index.max()).format('D. MMMM YYYY', locale='de_DE')}",
        'x': 0.5,
        'xanchor': 'center'
    }

    # Additional figure settings
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),
        margin=dict(t=25, b=38, l=0, r=0),
        hovermode='x',
        modebar={'orientation': 'v'},
        yaxis={
            'tickformat': '.2f',
            'tickcolor': '#E1E1E1',
            'gridcolor': '#E1E1E1'
        },
        plot_bgcolor='#FFFFFF'
    )

    return fig


def detail_figure(meter_id, date, quarter, meter, default_load_profile):
    """
    Return a Plotly GraphObj showing the load profile of a given meter for a given day, either as hourly or quarterly
    values. The meter values and the default load profile can be included as well.

    :param meter_id: The meter whose profile is to be plotted
    :param date: The date for which the load profile is requested
    :param quarter: Use quarter hour values, if False hourly values are used
    :param meter: Show meter values
    :param default_load_profile: Calculate and show default load profile
    :return: List of dictionaries with the keys date_time, obis_180 and diff
    """
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Set x-axis title
    fig.update_xaxes(title_text="Zeitpunkt")

    # Set y-axes titles
    fig.update_yaxes(title_text=f"kWh / {'60 min' if not quarter else '15 min'}", secondary_y=False)

    # Filter incomplete request
    if date is not None:
        day = dh.day(meter_id, date)

        if quarter:
            rule = '15T'
        else:
            rule = '60T'

        # Resample to requested interval
        day = day.resample(rule).agg({'obis_180': 'first', 'diff': 'sum', 'interpolation': 'first'})

        x_values = day.index

        # Color interpolation bars if necessary
        if day['interpolation'].any():
            colors = day['interpolation'].map({False: '#007BFF', True: '#EF553B'})
        else:
            colors = '#007BFF'

        # Add profile trace
        fig.add_trace(
            go.Bar(x=x_values, y=day['diff'], name="Lastgang", marker_color=colors,
                   hovertemplate="%{y}" + f" kWh / {'60 min' if not quarter else '15 min'}"),
            secondary_y=False,
        )

        # Add meter value trace
        if meter:
            fig.add_trace(
                go.Scatter(x=x_values, y=day['obis_180'], name="Zählerstand", line={'color': '#00CC96'},
                           hovertemplate="%{y} kWh"),
                secondary_y=True
            )
            fig.update_yaxes(title_text="kWh", secondary_y=True)

        # Add default load profile trace
        if default_load_profile:
            dlp = DefaultLoadProfile()
            dlp_data = dlp.calculate_profile(date, yearly_energy_usage(meter_id), shift=True)
            dlp_data = dlp_data.mul(1E-3).resample(rule).sum()  # Scale to kWh before resampling

            fig.add_trace(
                go.Bar(x=dlp_data.index, y=dlp_data.values, name="Standardlastprofil", marker={'color': '#B3B8F6'},
                       hovertemplate="%{y}" + f" kWh / {'60 min' if not quarter else '15 min'}"),
                secondary_y=False
            )

        fig.layout.title = {
            'text': arrow.get(date).format('dddd, D. MMMM YYYY', locale='de_DE'),
            'x': 0.5,
            'xanchor': 'center'
        }

    # Additional figure settings
    fig.update_layout(
        legend={
            'x': 0.01,
            'y': 0.99,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        margin={'t': 25, 'b': 0, 'l': 0, 'r': 75 if meter else 0},
        hovermode='x',
        modebar={'orientation': 'v'},
        yaxis={
            'tickformat': '.2f',
            'tickcolor': '#E1E1E1',
            'gridcolor': '#E1E1E1'
        },
        yaxis2={
            'showexponent': 'none',
            'exponentformat': 'none',
            'tickformat': '.f',
            'tickcolor': '#E1E1E1',
            'gridcolor': '#E1E1E1'
        },
        plot_bgcolor='#FFFFFF'
    )

    return fig


def table_data(meter_id, date, quarter):
    """
    Return the data for the given date as a list of dictionaries. If quarter is true, values are aggregated to 15
    minutes, otherwise the aggregation is hourly.

    :param meter_id: The meter whose profile is to be displayed
    :param date: Requested date as a string
    :param quarter: Aggregate to 15 minute values
    :return: DataFrame with date_time, obis_180 and diff
    """
    if date is not None:
        day = dh.day(meter_id, date).copy(deep=True)

        if quarter:
            rule = '15T'
        else:
            rule = '60T'

        dlp = DefaultLoadProfile()
        dlp_data = dlp.calculate_profile(date, yearly_energy_usage(meter_id), shift=True)
        day['dlp'] = dlp_data.mul(1E-3)   # Scale to kWh

        td = day.resample(rule)\
            .agg({'date_time': 'first', 'obis_180': 'first', 'diff': 'sum', 'dlp': 'sum'})\
            .to_dict('records')
        # Clean up data
        for data in td:
            data['date_time'] = data['date_time'].strftime("%H:%M")
            data['obis_180'] = round(data['obis_180'], 2)
            data['diff'] = round(data['diff'], 2)
            data['dlp'] = round(data['dlp'], 2)

        return td
