import os
import shutil
import re
from glob import glob


# Function to sort the folders based on the given criteria
def sort_folders(folders, sort_second_ascending, sort_third_ascending):
    # Convert folder names to tuples of floats for sorting
    folders_float = [(folder, tuple(map(float, folder.split('_')))) for folder in folders]
    # Sort folders based on the specified criteria
    sorted_folders = sorted(folders_float, key=lambda x: (x[1][0], x[1][1] if sort_second_ascending else -x[1][1], x[1][2] if sort_third_ascending else -x[1][2]))
    # Return sorted folder names
    return [folder[0] for folder in sorted_folders]

# Function to copy and rename csv files
def copy_and_rename_csv_files(base_dir, sorted_folders):
    # Create target directory for copied files
    target_dir = os.path.join(base_dir, 'sample_csv_data')
    os.makedirs(target_dir, exist_ok=True)
    
    for idx, folder in enumerate(sorted_folders, start=1):
        folder_path = os.path.join(base_dir, folder)
        for file in os.listdir(folder_path):
            if file.startswith('lambda') and file.endswith('.csv'):
                src_file_path = os.path.join(folder_path, file)
                dst_file_path = os.path.join(target_dir, f'state_s{idx}.csv')
                shutil.copy(src_file_path, dst_file_path)

# Main function to execute the script
def main(base_dir, sort_second_ascending=True, sort_third_ascending=True):
    # Regular expression to match folders named with three floating-point numbers separated by underscores
    regex = re.compile(r'^\d+(\.\d+)?_\d+(\.\d+)?_\d+(\.\d+)?$')
    folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and regex.match(d)]
    sorted_folders = sort_folders(folders, sort_second_ascending, sort_third_ascending)
    # print(f'sorted_folders: {sorted_folders}')
    copy_and_rename_csv_files(base_dir, sorted_folders)
    # print(f'Processed {len(sorted_folders)} folders.')

# Example usage
if __name__ == '__main__':
    # Set to False for descending order as needed
    base_dir = '.'
    main(base_dir, sort_second_ascending=False, sort_third_ascending=False)