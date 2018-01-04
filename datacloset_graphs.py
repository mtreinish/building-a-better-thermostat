import matplotlib.dates as dates
import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas as pd

def _split_columns(df):
    out_df = pd.DataFrame()
    gb = df.groupby('Series')
    # Split sensors into columns
    for sensor in gb.groups:
        sensor_df = gb.get_group(sensor)
        sensor_df = sensor_df.set_index(pd.to_datetime(sensor_df['Time']))
        if sensor.endswith('set_point'):
            continue
        out_df[sensor] = sensor_df['Value']
    out_df = out_df.dropna(how='all')
    out_df = out_df.interpolate(method='time')
    return out_df


def make_graph(title, cycle, filename):
    plt.close('all')
    fig, ax = plt.subplots(1)
    plt.title(title)
    plt.ylabel('Degrees Celcius')
    xfmt = dates.DateFormatter("%m-%d %H:%M:%S")
    ax.xaxis.set_major_formatter(xfmt)
    ax.autoscale_view()

    for sensor in cycle.keys():
        label = sensor.split(':')[1].split('}')[0]
        plt.plot(cycle.index, cycle[sensor], label=label)
    fig.autofmt_xdate()
    ax.set_axisbelow(False)
    ax.xaxis.grid(True)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator())
    ax.yaxis.grid(False)
    plt.legend()
    plt.savefig(filename, dpi=900)


df = pd.read_csv('datacloset.csv', sep=';', na_values=['null'])
temps = _split_columns(df)

make_graph('Bedroom Temperatures', temps, 'datacloset_graph.png')
