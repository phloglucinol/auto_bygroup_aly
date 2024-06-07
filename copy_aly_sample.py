import os
import shutil
import re
from glob import glob

def sort_csv(csvs, sort_second_ascending, sort_third_ascending):
    csvs = [ csv.split('.csv')[0] for csv in csvs]
    csvs = [ csv.split('lambda')[-1] for csv in csvs]
    csv_float = [(f'lambda{csv}.csv', tuple(map(float, csv.split('_')))) for csv in csvs]
    sorted_csvs = sorted(csv_float, key=lambda x: (x[1][0], x[1][1] if sort_second_ascending else -x[1][1], x[1][2] if sort_third_ascending else -x[1][2]))
    return [csv[0] for csv in sorted_csvs]

# Function to copy and rename csv files
def copy_and_rename_csv_files(base_dir, sorted_csvs):
    # Create target directory for copied files
    target_dir = os.path.join(base_dir, 'sample_csv_data')
    os.makedirs(target_dir, exist_ok=True)
    
    for idx, csv in enumerate(sorted_csvs, start=1):
        src_file_path = os.path.join(base_dir, 'ana_used_data', csv)
        dst_file_path = os.path.join(target_dir, f'state_s{idx}.csv')
        shutil.copy(src_file_path, dst_file_path)

# Main function to execute the script
def main(base_dir, sort_second_ascending=True, sort_third_ascending=True):
    lambda_csvs = [ f for f in os.listdir(os.path.join(base_dir, 'ana_used_data')) ]
    sorted_csvs = sort_csv(lambda_csvs, sort_second_ascending, sort_third_ascending)
    # print(f'sorted_folders: {sorted_folders}')
    copy_and_rename_csv_files(base_dir, sorted_csvs)
    # print(f'Processed {len(sorted_folders)} folders.')

# Example usage
if __name__ == '__main__':
    # Set to False for descending order as needed
    base_dir = '.'
    main(base_dir, sort_second_ascending=False, sort_third_ascending=False)
