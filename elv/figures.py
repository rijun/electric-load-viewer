import arrow
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from elv import dh
from default_load_profile import DefaultLoadProfile


def create_overview_figure(kind='bar', fill=False, markers=False):
    # Create empty figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df = dh.overview()

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
                       mode=plot_mode)
        )
    else:
        fig.add_trace(
            go.Bar(x=x_values, y=df['diff'], name="Lastgang")
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
        modebar={'orientation': 'v'}
    )

    return fig


def create_detail_figure(date: str, quarter: bool, meter: bool, default_load_profile: bool):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Set x-axis title
    fig.update_xaxes(title_text="Zeitpunkt")

    # Set y-axes titles
    fig.update_yaxes(title_text="kWh / Tag", secondary_y=False)

    # Filter incomplete request
    if date is not None:
        day = dh.day(date)

        if quarter:
            rule = '15T'
        else:
            rule = '60T'

        day = day.resample(rule).agg({'obis_180': 'first', 'diff': 'sum'})

        x_values = day.index

        # Add traces
        fig.add_trace(
            go.Bar(x=x_values, y=day['diff'], name="Lastgang"),
            secondary_y=False,
        )

        if meter:
            fig.add_trace(
                go.Scatter(x=x_values, y=day['obis_180'], name="Zählerstand"),
                secondary_y=True,
            )
            fig.update_yaxes(title_text="kW", secondary_y=True)

        if default_load_profile:
            dlp = DefaultLoadProfile()
            dlp_data = dlp.calculate_profile(date, dh.yearly_energy_usage(), shift=True)
            dlp_data = dlp_data.mul(1E-3).resample(rule).sum()  # Scale to kWh before resampling

            fig.add_trace(
                go.Bar(x=dlp_data.index.time, y=dlp_data.values, name="Standardlastprofil"),
                secondary_y=False,
            )

        fig.layout.title = {
            'text': arrow.get(date).format('dddd, D. MMMM YYYY', locale='de_DE'),
            'x': 0.5,
            'xanchor': 'center'
        }

    fig.layout.legend = {
        'x': 0.01,
        'y': 0.99,
        'xanchor': 'left',
        'yanchor': 'top'
    }
    fig.layout.margin = {'t': 25, 'b': 0, 'l': 0, 'r': 75 if meter else 0}
    fig.layout.hovermode = 'x'
    fig.layout.modebar.orientation = 'v'

    return fig


def create_table_data(date: str, quarter: bool) -> list:
    """
    Return the data for the given date as a list of dictionaries. If quarter is true, values are aggregated to 15
    minutes, otherwise the aggregation is hourly.

    :param date: Requested date as a string.
    :param quarter: Aggregate to 15 minute values.
    :return: List of dictionaries with the keys date_time, obis_180 and diff.
    """
    if date is not None:
        day = dh.day(date)

        if quarter:
            rule = '15T'
        else:
            rule = '60T'

        table_data = day.resample(rule)\
            .agg({'date_time': 'first', 'obis_180': 'first', 'diff': 'sum'})\
            .to_dict('records')
        # Clean up data
        for data in table_data:
            data['date_time'] = data['date_time'].strftime("%H:%M")
            data['diff'] = round(data['diff'], 2)

        return table_data
