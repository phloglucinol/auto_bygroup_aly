import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the prefixes in the desired order
PREFIX_ORDER = ['restraints', 'electrostatics', 'sterics']

def sort_key(dir_name):
    """
    Generate a sort key for each directory name.
    """
    match = re.match(r'(restraints|electrostatics|sterics)(?:_group(\d+))?', dir_name)
    if not match:
        return (float('inf'),)  # Place unmatched items at the end
    prefix, group_num = match.groups()
    group_num = int(group_num) if group_num else 0
    return (PREFIX_ORDER.index(prefix), group_num)

def list_and_sort_directories(path):
    """
    List and sort directories within a given path.
    """
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and re.match(r'(restraints|electrostatics|sterics)(?:_group(\d+))?', d)]
    sorted_dirs = sorted(dirs, key=sort_key)
    return sorted_dirs


def list_and_sort_csv(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.csv') and f.startswith('state')]
    sorted_files = sorted(files, key=lambda f: int(f.split('_s')[-1].split('.')[0]))
    return sorted_files

def custom_sort_key(side_alchemical_process_name):
    side, alchemical_process_name = side_alchemical_process_name.split('-')
    side_order = ['complex', 'ligand']
    def extract_number(prefix, text):
        pattern = prefix + r'(\d+)'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        else:
            return -1
    if alchemical_process_name.startswith('restraints'):
        return 10000
    elif alchemical_process_name.startswith('electrostatics'):
        return 20000+extract_number('electrostatics_group', alchemical_process_name)*1000+side_order.index(side)*100
    elif alchemical_process_name.startswith('sterics'):
        return 30000+extract_number('sterics_group', alchemical_process_name)*1000+side_order.index(side)*100

def plot_each_side_alchemical_process_time(time_df):
    # Assuming time_df is your initial DataFrame
    # Group by 'side_name' and 'alchemical_process_name'
    group_df = time_df.groupby(['side_name', 'alchemical_process_name'])

    # Iterate over each group
    for (side_name, alchemical_process_name), group in group_df:
        # Identify the lambda column with changes
        lambda_columns = ['restraint_lambda', 'electrostatics_lambda', 'sterics_lambda']
        std_devs = group[lambda_columns].std()
        changing_lambda_col = std_devs.idxmax()  # Column with the highest standard deviation
        
        # Check if there is a variation in the lambda column
        if std_devs.max() > 0:
            # Prepare data for plotting
            x_values = group[changing_lambda_col]
            y_values = group['simulation_time_ns']

            # Plotting
            plt.figure(figsize=(10, 6))
            plt.bar(x_values, y_values)
            
            plt.xlabel(f'{changing_lambda_col}')
            plt.ylabel('Simulation Time (ns)')
            plt.title(f'Simulation Time vs {changing_lambda_col}\nGroup: {side_name}, {alchemical_process_name}')

            # Save the plot as an image file
            image_filename = f'{side_name}_{alchemical_process_name}_simulationtime.png'
            plt.savefig(image_filename)
            plt.close()  # Close the figure to free up memory
            print(f"Saved chart for group: {side_name}, {alchemical_process_name} to {image_filename}")
        else:
            print(f"No significant variation found for group: {side_name}, {alchemical_process_name}. Chart not generated.")

def plot_every_themoprocess_time(df):
    # Sort dataframe by alchemical_process_name for consistent plotting
    # df.sort_values(by=['alchemical_process_name', 'side_name'], inplace=True)

    # Unique alchemical_process_names for plotting groups
    process_names = df['alchemical_process_name'].unique()
    # print(process_names)

    # Preparing figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))

    # Width of a bar
    bar_width = 0.35

    # Positions of the first bar in each group
    positions = np.arange(len(process_names))

    # Custom offsets for 'complex' and 'ligand' within each group
    offsets = {'complex': -bar_width/2, 'ligand': bar_width/2}

    # Colors for visual distinction
    colors = {'complex': 'tab:blue', 'ligand': 'orange'}

    for side_name in ['complex', 'ligand']:
        bar_positions = [pos + offsets[side_name] for pos in positions]
        # bar_heights = [df[(df['alchemical_process_name'] == process) & (df['side_name'] == side_name)]['simulation_time_ns'].values[0] for process in process_names]
        bar_heights = [
        df[(df['alchemical_process_name'] == process) & (df['side_name'] == side_name)]['simulation_time_ns'].values[0]
        if len(df[(df['alchemical_process_name'] == process) & (df['side_name'] == side_name)]['simulation_time_ns'].values) > 0
        else 0
        for process in process_names
    ]
        ax.bar(bar_positions, bar_heights, width=bar_width, label=side_name, color=colors[side_name])

    # Setting x-ticks to be in the middle of each group
    ax.set_xticks(positions)
    ax.set_xticklabels(process_names, rotation=45, ha="right")

    # Adding some labels and a legend
    ax.set_xlabel('Alchemical Process Name')
    ax.set_ylabel('Simulation Time (ns)')
    ax.set_title('Simulation Time by Process and Side')
    ax.legend()
    plt.tick_params(which='major',width=3, length=6)#设置大刻度的大小
    # plt.tick_params(which='minor',width=2, length=4)#设置小刻度的大小
    ax=plt.gca();#获得坐标轴的句柄
    ax.spines['bottom'].set_linewidth(4);#设置底部坐标轴的粗细
    ax.spines['left'].set_linewidth(4);#设置左边坐标轴的粗细
    ax.spines['right'].set_linewidth(4);#设置右边坐标轴的粗细
    ax.spines['top'].set_linewidth(4);#设置上部坐标轴的粗细
    plt.tight_layout()
    plt.savefig('every_themoprocess_time.png', format="png",dpi=600, transparent=True)
    plt.clf()
    # plt.show()

def main():
    time_per_iteration = 100 # fs
    system_name = os.path.basename(os.getcwd())
    root_paths = [os.path.join(os.getcwd(), 'openmm_run', sub_dir) for sub_dir in ['complex', 'ligand']]
    regex = re.compile(r'^\d+(\.\d+)?_\d+(\.\d+)?_\d+(\.\d+)?$')
    time_df = pd.DataFrame()
    for root_path in root_paths:
        sorted_dirs = list_and_sort_directories(root_path)
        # print(sorted_dirs)
        for dir_name in sorted_dirs:
            base_dir = os.path.join(root_path, dir_name)
            lambda_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and regex.match(d)]
            data = []
            for lambda_folder in lambda_folders:
                lambda_path = os.path.join(base_dir, lambda_folder)
                for file in os.listdir(lambda_path):
                    if file.startswith('lambda') and file.endswith('.csv'):
                        csv_file = os.path.join(lambda_path, file)
                        state_df = pd.read_csv(csv_file, sep='|')
                        niterations = len(state_df)
                        state_ns = niterations*time_per_iteration/1000/1000
                        data.append([
                            system_name,
                            os.path.basename(root_path), # complex or ligand
                            dir_name, # alchemical process name
                            lambda_folder, # lambda value
                            state_ns, # time in ns
                            state_df.iloc[0,1], # restraints lambda value
                            state_df.iloc[0,2], # electrostatics lambda value
                            state_df.iloc[0,3], # sterics lambda value
                        ])
                        # print(f'{os.path.basename(root_path)}/{dir_name}/{lambda_folder}: {state_ns:.2f} ns')
            columns = ['system_name', 'side_name', 'alchemical_process_name', 'lambda_value','simulation_time_ns', 'restraint_lambda', 'electrostatics_lambda', 'sterics_lambda']
            one_time_df = pd.DataFrame(data, columns=columns)
            time_df = pd.concat([time_df, one_time_df])
            # alc_process_path = os.path.join(root_path, dir_name, 'sample_csv_data')
            # sorted_files = list_and_sort_csv(alc_process_path)
            # data = []
            # for csv_file in sorted_files:
            #     state_df = pd.read_csv(os.path.join(alc_process_path, csv_file), sep='|')
            #     # print(state_df.iloc[0,1])
            #     niterations = len(state_df)
            #     state_ns = niterations*200/1000/1000
            #     data.append([
            #         system_name,
            #         os.path.basename(root_path), # complex or ligand
            #         dir_name, # alchemical process name
            #         int(csv_file.split('_s')[-1].split('.')[0]), # state number
            #         state_ns, # time in ns
            #         state_df.iloc[0,1], # restraints lambda value
            #         state_df.iloc[0,2], # electrostatics lambda value
            #         state_df.iloc[0,3], # sterics lambda value
            #     ])
            #     # print(f'{os.path.basename(root_path)}/{dir_name}/{csv_file}: {state_ns:.2f} ns')
            # columns = ['system_name', 'side_name', 'alchemical_process_name', 'state_number', 'simulation_time_ns', 'restraint_lambda', 'electrostatics_lambda', 'sterics_lambda']
            # one_time_df = pd.DataFrame(data, columns=columns)
            # time_df = pd.concat([time_df, one_time_df])
    # plot_each_side_alchemical_process_time(time_df)
    # time_df.to_csv('lambda_time.csv', index=False)
    com_simulation_time = time_df[time_df['side_name'] == 'complex']['simulation_time_ns'].sum()
    lig_simulation_time = time_df[time_df['side_name'] == 'ligand']['simulation_time_ns'].sum()
    print(f'Total simulation time for complex: {com_simulation_time:.2f} ns')
    print(f'Total simulation time for ligand: {lig_simulation_time:.2f} ns')
    print(f'Total simulation time for {system_name}: {com_simulation_time+lig_simulation_time:.2f} ns')
    grouped_sum = time_df.groupby(['side_name', 'alchemical_process_name'])['simulation_time_ns'].sum().reset_index()
    grouped_sum['sort_cotain'] = grouped_sum['side_name'] + '-' + grouped_sum['alchemical_process_name']
    grouped_sum['sort_key'] = grouped_sum['sort_cotain'].apply(custom_sort_key)
    grouped_sum = grouped_sum.sort_values(by='sort_key')
    grouped_sum = grouped_sum.drop(columns=['sort_cotain'])
    grouped_sum = grouped_sum.drop(columns=['sort_key'])
    plot_every_themoprocess_time(grouped_sum)
    time_df = pd.concat([time_df, grouped_sum])
    
    time_df.to_csv('lambda_time.csv', index=False)
    total_time_data = [system_name, com_simulation_time, lig_simulation_time, com_simulation_time+lig_simulation_time]
    total_time_count_df = pd.DataFrame([total_time_data,], columns = ['system_name', 'complex_time(ns)', 'ligand_time(ns)', 'total_time(ns)'])
    total_time_count_df.to_csv('total_time.csv', index=False)

if __name__ == '__main__': 
    main()
