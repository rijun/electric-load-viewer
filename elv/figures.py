import arrow
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from elv import dh
from default_load_profile import DefaultLoadProfile


def empty_graph():
    fig = make_subplots()
    fig.update_layout(
        xaxis={'visible': False},
        yaxis={'visible': False},
        margin=dict(t=25, b=38, l=0, r=0),
        modebar={'orientation': 'v'}
    )
    return fig


def overview_figure(session, meter_id, kind='bar', fill=False, markers=False):
    # Create empty figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df = dh.overview(session, meter_id)

    # Set x-axis title
    fig.update_xaxes(title_text="Datum")

    # Set y-axes titles
    fig.update_yaxes(title_text="kWh / Tag")

    x_values = df.index.date

    plot_mode = 'lines+markers' if markers else 'lines'
    plot_fill = 'tonexty' if fill else 'none'

    # Add traces
    if kind == 'line':
        fig.add_trace(
            go.Scatter(x=x_values, y=df['diff'], name="Lastgang", line={'shape': 'vhv'}, fill=plot_fill,
                       mode=plot_mode, hovertemplate="%{y} kWh / Tag")
        )
    else:
        if df['interpolation'].any():
            colors = df['interpolation'].map({False: '#636EFA', True: '#EF553B'})
        else:
            colors = '#00CC96'

        fig.add_trace(
            go.Bar(x=x_values, y=df['diff'], name="Lastgang", hovertemplate="%{y} kWh / Tag", marker_color=colors)
        )

    fig.layout.title = {
        'text': f"{arrow.get(df.index.min()).format('D. MMMM YYYY', locale='de_DE')} -- "
                f"{arrow.get(df.index.max()).format('D. MMMM YYYY', locale='de_DE')}",
        'x': 0.5,
        'xanchor': 'center'
    }

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
            'tickformat': '.2f'
        }
    )

    return fig


def detail_figure(session: str, meter_id: str, date: str, quarter: bool, meter: bool, default_load_profile: bool):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Set x-axis title
    fig.update_xaxes(title_text="Zeitpunkt")

    # Set y-axes titles
    fig.update_yaxes(title_text=f"kWh / {'60 min' if not quarter else '15 min'}", secondary_y=False)

    # Filter incomplete request
    if date is not None:
        day = dh.day(session, meter_id, date)

        if quarter:
            rule = '15T'
        else:
            rule = '60T'

        day = day.resample(rule).agg({'obis_180': 'first', 'diff': 'sum'})

        x_values = day.index

        # Add traces
        fig.add_trace(
            go.Bar(x=x_values, y=day['diff'], name="Lastgang", hovertemplate="%{y}" + f" kWh / {'60 min' if not quarter else '15 min'}"),
            secondary_y=False,
        )

        if meter:
            fig.add_trace(
                go.Scatter(x=x_values, y=day['obis_180'], name="Zählerstand", line={'color': '#00CC96'},
                           hovertemplate="%{y} kWh"),
                secondary_y=True
            )
            fig.update_yaxes(title_text="kWh", secondary_y=True)

        if default_load_profile:
            dlp = DefaultLoadProfile()
            dlp_data = dlp.calculate_profile(date, dh.yearly_energy_usage(session, meter_id), shift=True)
            dlp_data = dlp_data.mul(1E-3).resample(rule).sum()  # Scale to kWh before resampling

            fig.add_trace(
                go.Bar(x=dlp_data.index, y=dlp_data.values, name="Standardlastprofil", marker={'color': '#AB63FA'},
                       hovertemplate="%{y}" + f" kWh / {'60 min' if not quarter else '15 min'}"),
                secondary_y=False
            )

        fig.layout.title = {
            'text': arrow.get(date).format('dddd, D. MMMM YYYY', locale='de_DE'),
            'x': 0.5,
            'xanchor': 'center'
        }

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
            'tickformat': '.2f'
        },
        yaxis2={
            'showexponent': 'none',
            'exponentformat': 'none',
            'tickformat': '.f'
        }
    )

    return fig


def table_data(session: str, meter_id: str, date: str, quarter: bool) -> list:
    """
    Return the data for the given date as a list of dictionaries. If quarter is true, values are aggregated to 15
    minutes, otherwise the aggregation is hourly.

    :param session:
    :param meter_id:
    :param date: Requested date as a string.
    :param quarter: Aggregate to 15 minute values.
    :return: List of dictionaries with the keys date_time, obis_180 and diff.
    """
    if date is not None:
        day = dh.day(session, meter_id, date).copy(deep=True)

        if quarter:
            rule = '15T'
        else:
            rule = '60T'

        dlp = DefaultLoadProfile()
        dlp_data = dlp.calculate_profile(date, dh.yearly_energy_usage(session, meter_id), shift=True)
        day['dlp'] = dlp_data.mul(1E-3)   # Scale to kWh

        td = day.resample(rule)\
            .agg({'date_time': 'first', 'obis_180': 'first', 'diff': 'sum', 'dlp': 'sum'})\
            .to_dict('records')
        # Clean up data
        for data in td:
            data['date_time'] = data['date_time'].strftime("%H:%M")
            data['diff'] = round(data['diff'], 2)
            data['dlp'] = round(data['dlp'], 2)

        return td
