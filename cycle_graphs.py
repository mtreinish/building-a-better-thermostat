import matplotlib.dates as dates
import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas as pd
import peakutils


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
        plt.plot(cycle.index, cycle[sensor], label=sensor)
    fig.autofmt_xdate()
    ax.set_axisbelow(False)
    ax.xaxis.grid(True)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator())
    ax.yaxis.grid(False)
    plt.legend()
    plt.savefig(filename, dpi=300)


def double(in_list):
    itr = iter(in_list)
    while True:
        yield tuple([itr.next() for i in range(2)])


def _get_peak_to_peak(times, indexes, mins):
    values = {}
    for first, second in double(zip(indexes, mins)):
        first_max = times[first[0]]
        second_max = times[second[0]]
        first_min = times[first[1]]
        on_time = first_min - first_max
        off_time = second_max - first_min
        values['on_time'] = on_time
        values['off_time'] = off_time
        # Only the first cycle is accurate
        break
    return values


def _get_local_min(first, sec, values):
    local_list = values[first:sec]
    min_value = local_list.min()
    local_index = list(local_list).index(min_value)
    index = local_index + first
    assert values[index] == min_value
    return index

# This method is super buggy and will only ever work for the first cycle
# this is because it will be off by one on each iteration of the loop.
# But, it's good enough if you assume the first cycle is enough.
def get_peak_to_peaks(cycle):
    peak_to_peaks = {}
    for sensor in cycle.keys():
        values = cycle[sensor].dropna()
        if not values.any():
            continue
        indexes = peakutils.indexes(values)
        if indexes.any():
            mins = []
            for first, second in double(indexes):
                mins.append(_get_local_min(first, second,
                            values))
            peak_to_peaks[sensor] = _get_peak_to_peak(cycle[sensor].index,
                                                      indexes, mins)
    return peak_to_peaks

short_df = pd.read_csv('short_cycle.csv', sep=';', na_values=['null'])
short_cycle = _split_columns(short_df)
short_cycle['Set Point'] = 25.0
print("Before hysterisis fix:")
#cycle_times = get_peak_to_peaks(short_cycle)
#for sensor in cycle_times:
#    print("%s was on for %2f min. and off for %2f min." % (
#        sensor,
#        cycle_times[sensor]['on_time'].seconds / 60.0,
#        cycle_times[sensor]['off_time'].seconds / 60.0))

long_df = pd.read_csv('long_cycle.csv', sep=';', na_values=['null'])
long_cycle = _split_columns(long_df)
long_cycle['Set Point'] = 25.0
#print("After hysterisis fix:")
#cycle_times = get_peak_to_peaks(long_cycle)
#for sensor in cycle_times:
#    print("%s was on for %2f min. and off for %2f min." % (
#        sensor,
#        cycle_times[sensor]['on_time'].seconds / 60.0,
#        cycle_times[sensor]['off_time'].seconds / 60.0))

make_graph('Fast Cycle Times', short_cycle, 'short_cycle.png')
make_graph('Better Cycle Times', long_cycle, 'long_cycle.png')
