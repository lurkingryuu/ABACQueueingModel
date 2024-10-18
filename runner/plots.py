import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from parser_data import stats_parser
import re

BASE_DIR = Path(__file__).resolve().parent.parent


ALL_EXPERIMENTS_HISTORY_DIR = BASE_DIR / "client-server-model" / "experiments"
PLOTS_DIR = ALL_EXPERIMENTS_HISTORY_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def getplots(data_RT, data_NAR, data_IVT, data_VD, parameter, param_string='Initial Policy Size'):
    # Calculate the average for each metric
    data_ART = [sum(data_RT[i]) / len(data_RT[i]) if len(data_RT[i]) > 0 else 0 for i in range(len(data_RT))]
    data_ANAR = [sum(data_NAR[i]) / len(data_NAR[i]) if len(data_NAR[i]) > 0 else 0 for i in range(len(data_NAR))]
    data_AIVT = [sum(data_IVT[i]) / len(data_IVT[i]) if len(data_IVT[i]) > 0 else 0 for i in range(len(data_IVT))]
    data_AVD = [sum(data_VD[i]) / len(data_VD[i]) if len(data_VD[i]) > 0 else 0 for i in range(len(data_VD))]

    # Set the theme for seaborn
    sns.set_theme(style="ticks")
    
    print(f"Parameter: {parameter}")

    # Define the color palette
    palette = sns.color_palette(["red", "green", "blue", "black"])

    # Define markers for each configuration
    markers = ['s', 'X', 'o', '^']

    # Prepare data for plotting
    data = []
    configurations = ['C1', 'C1', 'C1', 'C1',
                      'C2', 'C2', 'C2', 'C2',
                      'C3', 'C3', 'C3', 'C3',
                      'C4', 'C4', 'C4', 'C4']
    configurations = [conf.replace('C', 'QM-PE_') for conf in configurations]
    
    parameter_repeated = parameter * 4  # Repeat parameter values for 4 configurations
    dic_ART = {
        'Avg. Resolution Time (in msec)': data_ART,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    dic_ANAR = {
        'Avg. number of requests': data_ANAR,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    dic_AIVT = {
        'Avg. inter vacation duration (in sec)': data_AIVT,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    dic_AVD = {
        'Avg. vacation duration (in sec)': data_AVD,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    data.extend([dic_ART, dic_ANAR, dic_AIVT, dic_AVD])

    dots = []
    for i in range(4):
        dots.append(pd.DataFrame(data[i]))
    
    # Prepare box data
    all_data = [data_RT, data_NAR, data_IVT, data_VD]
    box_data_list = []

    for i in range(4):
        # Flatten the data for box plots (combine configurations and parameter values)
        flat_data = []
        for j in range(len(configurations)):
            for value in all_data[i][j]:
                flat_data.append({
                    'Configurations': configurations[j],
                    param_string: parameter[j % len(parameter)],
                    'Metric': [f'Avg. Resolution Time (in msec)', 'Avg. number of requests', 'Avg. inter vacation duration (in sec)', 'Avg. vacation duration (in sec)'][i],
                    'Value': value
                })
        box_data_list.append(pd.DataFrame(flat_data))

    # Create a subplot grid for line plots, box plots, and bar plots (4 metrics x 3 plots each)
    fig, axs = plt.subplots(4, 3, figsize=(24, 20))  # Adjusted to 3 columns, increased figsize for better readability
    axs = axs.flatten()

    y_labels = [
        'Avg. Resolution Time (in msec)',
        'Avg. number of requests',
        'Avg. inter vacation duration (in sec)',
        'Avg. vacation duration (in sec)'
    ]
    titles = ['(a)', '(b)', '(c)', '(d)']

    for i in range(4):
        # Line Plot
        sns.lineplot(
            data=dots[i],
            x=param_string,
            y=y_labels[i],
            hue="Configurations",
            palette=palette,
            style="Configurations",
            markers=markers,
            markersize=7,
            ax=axs[3 * i]  # Left-hand plot in the row (column 1)
        )
        axs[3 * i].set_xlabel(f"{param_string}\n{titles[i]}")
        axs[3 * i].set_ylabel(y_labels[i])
        axs[3 * i].tick_params(axis='both')
        axs[3 * i].grid(True, linestyle='--', alpha=0.5)
        if i == 0:
            axs[3 * i].legend(title='Configurations', fontsize='small', title_fontsize='small')
        else:
            axs[3 * i].get_legend().remove()

        # Box Plot
        sns.boxplot(
            data=box_data_list[i],
            x=f"Configurations",
            y='Value',
            hue=param_string,
            palette=palette,
            ax=axs[3 * i + 1]  # Middle plot in the row (column 2)
        )
        axs[3 * i + 1].set_xlabel("Configurations and Parameter")
        axs[3 * i + 1].set_ylabel(y_labels[i])
        axs[3 * i + 1].tick_params(axis='both')
        axs[3 * i + 1].grid(True, linestyle='--', alpha=0.5)

        # Bar Plot
        bar_data = pd.DataFrame({
            param_string: parameter_repeated,
            'Configurations': configurations,
            y_labels[i]: [sum(all_data[i][j]) / len(all_data[i][j]) if len(all_data[i][j]) > 0 else 0 for j in range(len(all_data[i]))]  # Avg. values
        })

        sns.barplot(
            data=bar_data,
            x=param_string,
            y=y_labels[i],
            hue='Configurations',
            palette=palette,
            ax=axs[3 * i + 2]  # Right-hand plot in the row (column 3)
        )
        axs[3 * i + 2].set_xlabel(f"{param_string}\n{titles[i]}")
        axs[3 * i + 2].set_ylabel(y_labels[i])
        axs[3 * i + 2].grid(True, linestyle='--', alpha=0.5)

        # Dynamically set y-limits for the bar plot to make variation observable
        y_min = min(bar_data[y_labels[i]]) - 0.05 * min(bar_data[y_labels[i]])
        y_max = max(bar_data[y_labels[i]]) + 0.05 * max(bar_data[y_labels[i]])
        axs[3 * i + 2].set_ylim(y_min, y_max)

    # Adjust layout for better spacing
    plt.tight_layout(rect=[0, 0, 0.95, 0.96])

    # Create a single, shared legend for the figure
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', fontsize='medium')

    # Add a main title for the entire figure
    fig.suptitle(f'Plots for {param_string}: {parameter}', fontsize=16)

    # Save the figure
    plt.savefig(PLOTS_DIR / f'{param_string}.png')
    plt.close(fig)  # Close the figure to free memory


def plot_line_plots(data_RT, data_NAR, data_IVT, data_VD, parameter, param_string='Initial Policy Size'):
    data_ART = [sum(data_RT[i]) / len(data_RT[i]) if len(data_RT[i]) > 0 else 0 for i in range(len(data_RT))]
    data_ANAR = [sum(data_NAR[i]) / len(data_NAR[i]) if len(data_NAR[i]) > 0 else 0 for i in range(len(data_NAR))]
    data_AIVT = [sum(data_IVT[i]) / len(data_IVT[i]) if len(data_IVT[i]) > 0 else 0 for i in range(len(data_IVT))]
    data_AVD = [sum(data_VD[i]) / len(data_VD[i]) if len(data_VD[i]) > 0 else 0 for i in range(len(data_VD))]

    sns.set_theme(style="ticks")
    palette = sns.color_palette(["red", "green", "blue", "black"])
    markers = ['s', 'X', 'o', '^']

    dots = []
    configurations = ['C1', 'C1', 'C1', 'C1',
                      'C2', 'C2', 'C2', 'C2',
                      'C3', 'C3', 'C3', 'C3',
                      'C4', 'C4', 'C4', 'C4']
    configurations = [conf.replace('C', 'QM-PE_') for conf in configurations]
    
    parameter_repeated = parameter * 4
    dic_ART = {
        'Avg. Resolution Time (in msec)': data_ART,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    dic_ANAR = {
        'Avg. number of requests': data_ANAR,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    dic_AIVT = {
        'Avg. inter vacation duration (in sec)': data_AIVT,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    dic_AVD = {
        'Avg. vacation duration (in sec)': data_AVD,
        'Configurations': configurations,
        param_string: parameter_repeated
    }
    data = [dic_ART, dic_ANAR, dic_AIVT, dic_AVD]
    
    for i in range(4):
        dots.append(pd.DataFrame(data[i]))

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))  # Adjust for 2x2 layout
    axs = axs.flatten()

    y_labels = [
        'Avg. Resolution Time (in msec)',
        'Avg. number of requests',
        'Avg. inter vacation duration (in sec)',
        'Avg. vacation duration (in sec)'
    ]
    titles = ['(a)', '(b)', '(c)', '(d)']

    for i in range(4):
        sns.lineplot(
            data=dots[i],
            x=param_string,
            y=y_labels[i],
            hue="Configurations",
            palette=palette,
            style="Configurations",
            markers=markers,
            markersize=7,
            ax=axs[i]
        )
        axs[i].set_xlabel(f"{param_string}\n{titles[i]}")
        axs[i].set_ylabel(y_labels[i])
        axs[i].tick_params(axis='both')
        axs[i].set_xticks(parameter)
        axs[i].grid(True, linestyle='--', alpha=0.5)

        if i == 0:
            axs[i].legend(title='Configurations', fontsize='small', title_fontsize='small')
        else:
            axs[i].get_legend().remove()

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'line_plots_{param_string}.png')
    plt.close(fig)

def plot_box_plots(data_RT, data_NAR, data_IVT, data_VD, parameter, param_string='Initial Policy Size'):
    sns.set_theme(style="ticks")
    palette = sns.color_palette(["red", "green", "blue", "black"])
    
    all_data = [data_RT, data_NAR, data_IVT, data_VD]
    configurations = ['C1', 'C1', 'C1', 'C1',
                      'C2', 'C2', 'C2', 'C2',
                      'C3', 'C3', 'C3', 'C3',
                      'C4', 'C4', 'C4', 'C4']
    configurations = [conf.replace('C', 'QM-PE_') for conf in configurations]

    parameter_repeated = parameter * 4
    box_data_list = []

    for i in range(4):
        flat_data = []
        for j in range(len(configurations)):
            for value in all_data[i][j]:
                flat_data.append({
                    'Configurations': configurations[j],
                    param_string: parameter[j % len(parameter)],
                    'Metric': [f'Avg. Resolution Time (in msec)', 'Avg. number of requests', 'Avg. inter vacation duration (in sec)', 'Avg. vacation duration (in sec)'][i],
                    'Value': value
                })
        box_data_list.append(pd.DataFrame(flat_data))

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))  # Adjust for 2x2 layout
    axs = axs.flatten()

    y_labels = [
        'Avg. Resolution Time (in msec)',
        'Avg. number of requests',
        'Avg. inter vacation duration (in sec)',
        'Avg. vacation duration (in sec)'
    ]
    titles = ['(a)', '(b)', '(c)', '(d)']

    for i in range(4):
        sns.boxplot(
            data=box_data_list[i],
            x="Configurations",
            y='Value',
            hue=param_string,
            palette=palette,
            ax=axs[i]
        )
        axs[i].set_xlabel(f"Configurations\n{titles[i]}")
        axs[i].set_ylabel(y_labels[i])
        axs[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f'box_plots_{param_string}.png')
    plt.close(fig)


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
    "policy_size": [100, 300, 600, 1000],
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

def plot_param(param: str, modes: list = ['line', 'box']):
    data_RT = [ store[param]['res_time'][key] for key in keys ]
    data_NAR = [ store[param]['no_of_jobs'][key] for key in keys ]
    data_IVT = [ store[param]['inter_vac_duration'][key] for key in keys ]
    data_VD = [ store[param]['vac_duration'][key] for key in keys ]
    # getplots(data_RT, data_NAR, data_IVT, data_VD, VARIANT_CONFIGS[param], param)
    if 'line' in modes:
        plot_line_plots(data_RT, data_NAR, data_IVT, data_VD, VARIANT_CONFIGS[param], param)
    if 'box' in modes:
        plot_box_plots(data_RT, data_NAR, data_IVT, data_VD, VARIANT_CONFIGS[param], param)


if __name__ == "__main__":
    plot_param('al_update_rate', ['line'])
    plot_param('arrival_rate', ['box'])
    plot_param('attributes', ['line'])
    plot_param('policy_size', ['line'])
    print("Done")