import os
import glob
import sys

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
                        print(f"free_ene.csv file not found in {free_ene_path}")
                        sys.exit(1)
                        # print(f"free_ene.csv file not found in {free_ene_path}")
                        

    return all_folders_satisfied

if __name__ == '__main__':
    sys_path = os.getcwd()
    check_free_ene_csv(sys_path)

