import os
from glob import glob
import re
PREFIX_ORDER=['restraints', 'electrostatics', 'sterics']
side_order = ['complex', 'ligand']

def sort_key(dir_name):
    """
    Generate a sort key for each directory name.
    """
    # print(dir_name)
    com_lig_match = re.match(r'.*(complex|ligand).*', dir_name)
    com_lig = com_lig_match.groups()[0]
    match = re.match(r'.*(restraints|electrostatics|sterics)(?:_group(\d+))?.*', dir_name)
    if not match:
        return (float('inf'),)  # Place unmatched items at the end
    prefix, group_num = match.groups()
    group_num = int(group_num) if group_num else 0
    return (side_order.index(com_lig), PREFIX_ORDER.index(prefix), group_num)


class Bygroup_ABFE_files_getter():
    def __init__(self, root_path=None):
        if root_path is None:
            self.root_path = os.getcwd()
        else:
            self.root_path = root_path
        self.timeseries_png_files = []
        
    def get_timeseries_png_files(self, ):
        glob_pattern = os.path.join(self.root_path, 'openmm_run', '*', '*', 'sample_csv_data', 'fe_cal_out', 'time_serial_check', '*.png')
        files = glob(glob_pattern)
        # abs_files = [os.path.abspath(f) for f in files]
        self.timeseries_png_files = sorted(files, key=sort_key)
        self.timeseries_png_files.insert(0, os.path.join(self.root_path, f'{os.path.basename(self.root_path)}_complex_fe_time_serial.png'))
        self.timeseries_png_files.insert(0, os.path.join(self.root_path, f'{os.path.basename(self.root_path)}_ligand_fe_time_serial.png'))
        self.timeseries_png_files.insert(0, os.path.join(self.root_path, f'{os.path.basename(self.root_path)}_whole_mol_fe_time_serial.png'))
        # print(self.timeseries_png_files)
        return self.timeseries_png_files

    def get_reweighting_png_files(self,):
        glob_pattern = os.path.join(self.root_path, 'openmm_run', '*', '*', 'sample_csv_data', 'fe_cal_out', 'dG_diff_*timeall.png')
        files = glob(glob_pattern)
        self.reweighting_png_files = sorted(files, key=sort_key)
        print(self.reweighting_png_files)
        return self.reweighting_png_files
    
    def get_simu_time_png_files(self,):
        glob_pattern = os.path.join(self.root_path, 'every_themoprocess_time.png')
        files = glob(glob_pattern)
        self.simu_time_png_files = files
        print(self.simu_time_png_files)
        return self.simu_time_png_files

    def get_dGdl_png_files(self, ):
        glob_pattern = os.path.join(self.root_path, 'openmm_run', '*', '*', 'sample_csv_data', 'fe_cal_out', '*_dG_dl.png')
        files = glob(glob_pattern)
        self.dGdl_png_files = sorted(files, key=sort_key)
        print(self.dGdl_png_files)
        return self.dGdl_png_files
    

if __name__ == '__main__':
    ts = Bygroup_ABFE_files_getter(root_path='/nfs/export3_25T/Bygroup_FEP_data/CDK2_bygroup/2nd_batch/1ke7')
    ts.get_timeseries_png_files()