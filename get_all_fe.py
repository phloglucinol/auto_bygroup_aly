import os
import re
import math
import pandas as pd
import numpy as np
import glob
import scipy

# Define the prefixes in the desired order
PREFIX_ORDER = ['restraints', 'electrostatics', 'sterics']

def check_free_ene_csv(sys_path):
    # 获取当前文件夹路径
    # print(sys_path)
    sides = ['complex', 'ligand']
    # 定义要查找的文件夹名称前缀列表
    folder_prefixes = ['restraints', 'electrostatics', 'sterics']

    # 初始化一个标志变量,用于跟踪是否所有文件夹都满足条件
    all_folders_satisfied = True
    for side in sides:
        current_dir = os.path.join(sys_path, 'openmm_run', side)

        # 使用 glob 模块查找符合条件的文件夹
        for prefix in folder_prefixes:
            folder_pattern = os.path.join(current_dir, f"{prefix}*")
            # print(folder_pattern)
            folders = glob.glob(folder_pattern)
            # print(folders)
            for folder_path in folders:
                # print(folder_path)
                # 检查文件夹是否存在
                if os.path.isdir(folder_path):
                    # 构建 free_ene.csv 文件的完整路径
                    free_ene_path = os.path.join(folder_path, 'sample_csv_data', 'fe_cal_out', 'free_ene.csv')

                    # 检查 free_ene.csv 文件是否存在
                    if not os.path.isfile(free_ene_path):
                        all_folders_satisfied = False
                        break
                        # print(f"free_ene.csv file not found in {free_ene_path}")
                        

    return all_folders_satisfied



def get_aly_restr_lig(res_info_csv):
    K = 8.314472*0.001  # Gas constant in kJ/mol/K
    V = 1.66            # standard volume in nm^3
    T = 300.0           # Temperature in Kelvin
    res_df = pd.read_csv(res_info_csv, )
    r0 = float(res_df.iloc[0, 4])/10 # distance in A
    K_r = 4184.0 # force constant for distance (kJ/mol/nm^2)

    thA = float(res_df.iloc[0, 5]) # Angle in rad
    K_thA = 41.84 # force constant for angle (kJ/mol/rad^2)

    thB = float(res_df.iloc[0, 6]) # Angle in rad
    K_thB = 41.84 # force constant for angle (kJ/mol/rad^2)

    K_phiA = 41.84 # force constant for angle (kJ/mol/rad^2)
    K_phiB = 41.84 # force constant for angle (kJ/mol/rad^2)
    K_phiC = 41.84 # force constant for angle (kJ/mol/rad^2)

    arg =(
        (8.0 * math.pi**2.0 * V) / (r0**2.0 * math.sin(thA) * math.sin(thB))
        *
        (
            ( (K_r * K_thA * K_thB * K_phiA * K_phiB * K_phiC)**0.5 ) / ( (2.0 * math.pi * K * T)**(3.0) )
        )
    )
    dG = - K * T * math.log(arg)
    return abs(dG)/4.184

def numerical_distance_integrand(r, r0, kr, R, T):
    r_eff = abs(r-r0)
    if r_eff <0 :
        r_eff =0 
    return (r**2)*np.exp(-(kr*r_eff**2)/(2*R*T))

def numerical_angle_integrand(theta, theta0, spring_constant, R, T):
    return np.sin(theta) * np.exp(-spring_constant / (2 * R*T) * (theta - theta0) ** 2)

def numerical_torsion_integrand(phi, phi0, spring_constant, R, T):
    d_tor = phi-phi0
#     dphi = d_tor
    dphi = d_tor - np.floor(d_tor / (2 * np.pi) + 0.5) * (2 * np.pi)
    return np.exp(-spring_constant/(2 * R*T)*dphi**2)

def get_aly_restr_lig_single_atom(res_info_csv):
    R = 8.314472*0.001  # Gas constant in kJ/mol/K
    v0 = 1.66            # standard volume in nm^3
    T = 298.15          # Temperature in Kelvin
    K_r = 4184.0*4 # force constant for distance (kJ/mol/nm^2)
    res_df = pd.read_csv(res_info_csv, )
    r0 = float(res_df.iloc[0, 4])/10 # distance in A to distance in nm
    thetaA = float(res_df.iloc[0, 5]) # Angle in rad
    K_ang = 41.84 # force constant for angle (kJ/mol/rad^2)
    phiA = float(res_df.iloc[0, 7]) # Torsion in rad
    K_tor = 41.84 # force constant for torsion (kJ/mol/rad^2)
#     One distance
    rmin = max(0, r0-4*np.sqrt(R*T/K_r))
    rmax = r0+4*np.sqrt(R*T/K_r) # # Dist. which gives restraint energy = 8 RT
    I = lambda r: numerical_distance_integrand(r, r0, K_r, R, T)
    z_r = scipy.integrate.quad(I, rmin, rmax)[0]
    dg = z_r
#    One angle
    I = lambda theta: numerical_angle_integrand(theta, thetaA, K_ang, R, T)
    z_ang = scipy.integrate.quad(I, 0, np.pi)[0]
    dg *= z_ang
#    One torsion
    I = lambda phi: numerical_torsion_integrand(phi, phiA, K_tor, R, T)
    z_tor = scipy.integrate.quad(I, -np.pi, np.pi)[0]
    dg *= z_tor

    dg = -R*T*np.log(v0/dg)
    print(dg/4.184)
    return abs(dg/4.184)


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
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    sorted_dirs = sorted(dirs, key=sort_key)
    return sorted_dirs

def read_and_filter_csv(file_path):
    """
    Read the last row of the csv file.
    """
    df = pd.read_csv(file_path, sep='|')
    last_row = df.iloc[-1]
    return last_row

def get_final_fe_result(dataframe_, system_name):
    df = dataframe_
    # Extract specific values
    com_res_fe = df[(df['side_name'] == 'complex') & (df['alchemical_process_name'] == 'restraints')]['free_energy(kcal/mol)'].values[0]
    com_res_std = df[(df['side_name'] == 'complex') & (df['alchemical_process_name'] == 'restraints')]['std'].values[0]
    
    lig_res_fe = df[(df['side_name'] == 'ligand') & (df['alchemical_process_name'] == 'restraints')]['free_energy(kcal/mol)'].values[0]
    lig_res_std = df[(df['side_name'] == 'ligand') & (df['alchemical_process_name'] == 'restraints')]['std'].values[0]
    
    # Sum free_energy and calculate sqrt of sum of squares of std for electorstatics and sterics
    def sum_fe_and_sqrt_std(data, side, process_start):
        sum_fe = data[(data['side_name'] == side) & (data['alchemical_process_name'].str.startswith(process_start))]['free_energy(kcal/mol)'].sum()
        sqrt_std = np.sqrt((data[(data['side_name'] == side) & (data['alchemical_process_name'].str.startswith(process_start))]['std'] ** 2).sum())
        return sum_fe, sqrt_std
    
    com_ele_fe, com_ele_std = sum_fe_and_sqrt_std(df, 'complex', 'electrostatics')
    lig_ele_fe, lig_ele_std = sum_fe_and_sqrt_std(df, 'ligand', 'electrostatics')
    
    com_vdw_fe, com_vdw_std = sum_fe_and_sqrt_std(df, 'complex', 'sterics')
    lig_vdw_fe, lig_vdw_std = sum_fe_and_sqrt_std(df, 'ligand', 'sterics')
    
    # Calculate fe_std and fe
    fe_std = np.sqrt(com_res_std**2 + lig_res_std**2 + com_ele_std**2 + lig_ele_std**2 + com_vdw_std**2 + lig_vdw_std**2)
    fe = lig_res_fe + lig_ele_fe + lig_vdw_fe - (-com_res_fe + com_ele_fe + com_vdw_fe)##Note: -com_res_fe just for wrong MD of tianjin Mpro simulations.
    #print('-----------',-com_res_fe) 
    # Save variables to a CSV
    results_df = pd.DataFrame([[system_name, com_res_fe, com_res_std, lig_res_fe, lig_res_std, com_ele_fe, com_ele_std, lig_ele_fe, lig_ele_std, com_vdw_fe, com_vdw_std, lig_vdw_fe, lig_vdw_std, fe, fe_std]],columns=['system_name', 'com_res_fe', 'com_res_std', 'lig_res_fe', 'lig_res_std', 'com_ele_fe', 'com_ele_std', 'lig_ele_fe', 'lig_ele_std', 'com_vdw_fe', 'com_vdw_std', 'lig_vdw_fe', 'lig_vdw_std', 'fe', 'fe_std'],
    )
    results_df.to_csv('final_fe_data.csv', index=False, sep='|')

def main():
    data = []
    system_name = os.path.basename(os.getcwd())
    root_paths = [os.path.join(os.getcwd(), 'openmm_run', sub_dir) for sub_dir in ['complex', 'ligand']]
    if check_free_ene_csv(os.getcwd()):
        print('All free_ene.csv files exist!')
        for root_path in root_paths:
            sorted_dirs = list_and_sort_directories(root_path)
            for dir_name in sorted_dirs:
                csv_path = os.path.join(root_path, dir_name, 'sample_csv_data', 'fe_cal_out', 'free_ene.csv')
                if os.path.exists(csv_path):
                    last_row = read_and_filter_csv(csv_path)
                    data.append([
                        os.path.basename(root_path),  # side_name
                        dir_name,  # alchemical_process_name
                        last_row['free_energy(kcal/mol)'],
                        last_row['bar_std'],
                        last_row['delta_A_what_to_what']  # lambda_info
                    ])
        complex_path = os.path.join(os.getcwd(), 'openmm_run', 'complex')
        aly_res_dg = get_aly_restr_lig_single_atom(f'{complex_path}/res_databystd.csv')
        # Write the aly_res_dg to the text
        with open('aly_res_dg.txt', 'w') as f:
            f.write(str(aly_res_dg))
        data.append(['ligand', 'restraints', aly_res_dg, 0.0, "None"])
        
        # Convert the collected data into a DataFrame
        columns = ['side_name', 'alchemical_process_name', 'free_energy(kcal/mol)', 'std', 'lambda_info']
        df = pd.DataFrame(data, columns=columns)
        
        # Save the DataFrame to a CSV file with '|' as the delimiter
        df.to_csv('collected_data.csv', index=False, sep='|')
        get_final_fe_result(df, system_name)

if __name__ == "__main__":
    main()
