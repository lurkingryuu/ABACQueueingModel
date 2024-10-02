import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from parser_data import stats_parser
import re

BASE_DIR = Path(__file__).resolve().parent.parent


ALL_EXPERIMENTS_HISTORY_DIR = BASE_DIR / "client-server-model" / "experiments"

def getplots(data_ART, data_NAR, data_AIVT, data_AVD, parameter, param_string='Initial Policy Size'):
    # Set the theme
    sns.set_theme(style="ticks")
    
    print(f"Parameter: {parameter}")

    # Define the color palette
    palette = sns.color_palette(["red", "green", "blue", "black"])

    # Define markers for each configuration
    markers = ['s', 'X', 'o', '^']

    data = []
    dic_ART = {
        'Avg. Resolution Time (in msec)': data_ART,
        'Configurations': [
            'C1', 'C1', 'C1', 'C1', 'C2', 'C2', 'C2', 'C2', 'C3', 'C3', 'C3', 'C3', 'C4', 'C4', 'C4', 'C4'
        ],
        param_string: parameter
    }
    dic_NAR = {
        'Avg. number of requests': data_NAR,
        'Configurations': [
            'C1', 'C1', 'C1', 'C1', 'C2', 'C2', 'C2', 'C2', 'C3', 'C3', 'C3', 'C3', 'C4', 'C4', 'C4', 'C4'
        ],
        param_string: parameter
    }
    dic_AIVT = {
        'Avg. inter vacation duration (in sec)': data_AIVT,
        'Configurations': [
            'C1', 'C1', 'C1', 'C1', 'C2', 'C2', 'C2', 'C2', 'C3', 'C3', 'C3', 'C3', 'C4', 'C4', 'C4', 'C4'
        ],
        param_string: parameter
    }
    dic_AVD = {
        'Avg. vacation duration (in sec)': data_AVD,
        'Configurations': [
            'C1', 'C1', 'C1', 'C1', 'C2', 'C2', 'C2', 'C2', 'C3', 'C3', 'C3', 'C3', 'C4', 'C4', 'C4', 'C4'
        ],
        param_string: parameter
    }
    data.append(dic_ART)
    data.append(dic_NAR)
    data.append(dic_AIVT)
    data.append(dic_AVD)
    dots = []
    for i in range(4):
        print(data[i])
        dots.append(pd.DataFrame(data[i]))

    # Create a subplot grid
    fig, axs = plt.subplots(2, 2, figsize=(8.4, 7))
    axs = axs.flatten()

    count = 0
    y_label = ['Avg. Resolution Time (in msec)', 'Avg. number of requests', 'Avg. inter vacation duration (in sec)',
               'Avg. vacation duration (in sec)']
    enum = ['(a)', '(b)', '(c)', '(d)']
    # Plot each subplot
    for i, ax in enumerate(axs):

        sns.lineplot(
            data=dots[count],
            x=param_string, y=y_label[count],
            hue="Configurations",
            palette=palette,
            style="Configurations",  # Specify style for different markers
            markers=markers,  # Specify markers for each configuration
            markersize=7,
            ax=ax
        )
        mark_string = param_string + '\n' + enum[count]
        ax.set_xlabel(mark_string)
        ax.set_ylabel(y_label[count])
        ax.tick_params(axis='both')
        ax.get_legend().remove()
        count += 1

        # Add a grid of dotted lines
        ax.grid(True, linestyle='--', alpha=0.5)

    plt.subplots_adjust(wspace=0.3, hspace=0.33)

    # Create a single, shared legend for the figure with entries on a single line
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, [f"{label}" for label in labels], loc='upper right', bbox_to_anchor=(0.65, 0.48),
               borderaxespad=0, fontsize='xx-small', ncol=4)

    plt.savefig(ALL_EXPERIMENTS_HISTORY_DIR / f'{param_string}.png')
    return


def get_avg_inter_vacation_time(vac_start_time, vac_durations):
    inter_vacation_time = []
    for i in range(1, len(vac_start_time)):
        inter_vacation_time.append(vac_start_time[i] - vac_start_time[i - 1] - vac_durations[i - 1])
    # print(f"No. of vacations: {len(vac_start_time)}")
    # print(f"Inter vacation time: {inter_vacation_time}")
    if len(inter_vacation_time) == 0:
        return 0
    return sum(inter_vacation_time) / len(inter_vacation_time)

# tot_avg_wait_time, tot_avg_res_time, avg_vac_duration, avg_no_of_jobs, vac_start_time, vac_durations = stats_parser(file_path)
# c1_al_update_rate_v1_1
EXPERIMENT_REGEX = r'(c\d)_([a-z_]+)_(v\d)_(\d)'

VARIANT_CONFIGS = {
    "al_update_rate": [20, 15, 7, 2],
    "arrival_rate": [150, 80, 20, 5],
    "attributes": [4, 6, 8, 10],
    "policy_size": [15, 25, 35, 45],
}

STATS_TITLES = ['res_time', 'inter_vac_duration', 'no_of_jobs', 'vac_duration']


store = { key: { avgkey: {} for avgkey in STATS_TITLES } for key in VARIANT_CONFIGS.keys() }
for file in ALL_EXPERIMENTS_HISTORY_DIR.glob('*.txt'):
    experiment = file.stem
    match = re.match(EXPERIMENT_REGEX, experiment)
    if match:
        config = match.group(1)
        variant = match.group(2)
        value = match.group(3)
        experiment_no = int(match.group(4))
        avg_wait_time, avg_res_time, avg_vac_duration, avg_no_of_jobs, vac_start_time, vac_durations = stats_parser(file)
        avg_inter_vacation_time = get_avg_inter_vacation_time(vac_start_time, vac_durations)
        key_name = f'{config}_{value}'
        if key_name not in store[variant]['res_time']:
            for stat in STATS_TITLES:
                store[variant][stat][key_name] = []
        store[variant]['res_time'][key_name].append(avg_res_time)
        store[variant]['inter_vac_duration'][key_name].append(avg_inter_vacation_time)
        store[variant]['no_of_jobs'][key_name].append(avg_no_of_jobs)
        store[variant]['vac_duration'][key_name].append(avg_vac_duration)
        
keys = list(store['al_update_rate']['res_time'].keys())
keys.sort()
print(f"Keys: {keys}")

def plot_param(param: str):
    data_ART = [ sum(store[param]['res_time'][key])/len(store[param]['res_time'][key]) for key in keys ]
    data_NAR = [ sum(store[param]['no_of_jobs'][key])/len(store[param]['no_of_jobs'][key]) for key in keys ]
    data_AIVT = [ sum(store[param]['inter_vac_duration'][key])/len(store[param]['inter_vac_duration'][key]) for key in keys ]
    data_AVD = [ sum(store[param]['vac_duration'][key])/len(store[param]['vac_duration'][key]) for key in keys ]
    getplots(data_ART, data_NAR, data_AIVT, data_AVD, VARIANT_CONFIGS[param]*4, param)

if __name__ == "__main__":
    plot_param('al_update_rate')
    plot_param('arrival_rate')
    plot_param('attributes')
    plot_param('policy_size')
    print("Done")