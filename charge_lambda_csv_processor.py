import pandas as pd
import numpy as np
import os
import sys
import shutil
import re

class One_thero_data():
    def __init__(self, root_path,):
        self.root_path = root_path
        self.recover_meta_data()
        for file in os.listdir(os.path.join(self.root_path, 'metadata')):
            if file.startswith('state') and file.endswith('.csv'):
                output_dir = os.path.join(self.root_path, 'process_data')
                os.makedirs(output_dir, exist_ok=True)
                intra_mol_ene_dir = os.path.join(output_dir, 'intra_mol_ene_data')
                all_mol_ene_dir = os.path.join(output_dir, 'all_mol_ene_data')
                mol_env_ene_dir = os.path.join(output_dir, 'mol_env_ene_data')
                os.makedirs(intra_mol_ene_dir, exist_ok=True)
                os.makedirs(all_mol_ene_dir, exist_ok=True)
                os.makedirs(mol_env_ene_dir, exist_ok=True)
                state_num = re.search(r's(\d+)', file).group(1)
                output_intra_mol_ene_csv = os.path.join(intra_mol_ene_dir, f'state_s{state_num}.csv')
                output_all_mol_ene_csv = os.path.join(all_mol_ene_dir, f'state_s{state_num}.csv')
                output_mol_env_ene_csv = os.path.join(mol_env_ene_dir, f'state_s{state_num}.csv')
                intra_mol_ene, all_mol_ene, mol_env_ene = self.process_csv(os.path.join(self.root_path, 'metadata', file))
                intra_mol_ene.to_csv(output_intra_mol_ene_csv, sep='|', index=False)
                all_mol_ene.to_csv(output_all_mol_ene_csv, sep='|', index=False)
                mol_env_ene.to_csv(output_mol_env_ene_csv, sep='|', index=False)

    def recover_meta_data(self, ):
        csvs_base_path = self.root_path
        if os.path.exists(os.path.join(csvs_base_path, 'metadata')):
            for file in os.listdir(os.path.join(csvs_base_path, 'metadata')):
                if file.startswith('state') and file.endswith('.csv'):
                    src_file_path = os.path.join(csvs_base_path, 'metadata', file)
                    dst_file_path = os.path.join(csvs_base_path, file)
                    shutil.copy(src_file_path, dst_file_path)
        else:
            os.makedirs(os.path.join(csvs_base_path, 'metadata'))
            for file in os.listdir(csvs_base_path):
                if file.startswith('state') and file.endswith('.csv'):
                    src_file_path = os.path.join(csvs_base_path, file)
                    dst_file_path = os.path.join(csvs_base_path, 'metadata', file)
                    shutil.copy(src_file_path, dst_file_path)

    def process_csv(self, file_path):
        df = pd.read_csv(file_path, sep='|')
        
        headers = df.columns.tolist()
        tuples = [tuple(h.strip('()').split(', ')) for h in headers if h.startswith('(')]
        
        tuples = [(float(t[0]), float(t[1]), float(t[2]), float(t[3]), float(t[4])) for t in tuples]
        
        intra_mol_tuples = [t for t in tuples if t[3] == 0.0]
        all_mol_tuples = [t for t in tuples if t[3] == 1.0]
        
        intra_mol_columns = ['times(ps)', 'lambda_restraints', 'lambda_electrostatics', 'lambda_sterics'] + [str(t) for t in intra_mol_tuples]
        all_mol_columns = ['times(ps)', 'lambda_restraints', 'lambda_electrostatics', 'lambda_sterics'] + [str(t) for t in all_mol_tuples]
        intra_mol_ene = df[intra_mol_columns]
        all_mol_ene = df[all_mol_columns]
        
        mol_env_ene_data = {
            'times(ps)': df['times(ps)'],
            'lambda_restraints': df['lambda_restraints'],
            'lambda_electrostatics': df['lambda_electrostatics'],
            'lambda_sterics': df['lambda_sterics']
        }
        for intra_t in intra_mol_tuples:
            for all_t in all_mol_tuples:
                if intra_t[:3] == all_t[:3]:
                    new_col = tuple(intra_t[:3])
                    mol_env_ene_data[new_col] = all_mol_ene[str(all_t)] - intra_mol_ene[str(intra_t)]
                    break
        
        mol_env_ene = pd.DataFrame(mol_env_ene_data)

        intra_mol_ene.columns = ['times(ps)', 'lambda_restraints', 'lambda_electrostatics', 'lambda_sterics'] + [str(t[:3]) for t in intra_mol_tuples]
        all_mol_ene.columns = ['times(ps)', 'lambda_restraints', 'lambda_electrostatics', 'lambda_sterics'] + [str(t[:3]) for t in all_mol_tuples]
        
        return intra_mol_ene, all_mol_ene, mol_env_ene

a = One_thero_data(root_path='.')
