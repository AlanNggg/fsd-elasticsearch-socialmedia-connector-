import glob

path = r'\\10.18.25.144\Web';

file_paths = glob.glob(path + '/**/*', recursive=True)

# Get all files
for file_path in file_paths:
    print(file_path)

# Get all folders
folder_paths = glob.glob(path + '/**/', recursive=True)
for folder_path in folder_paths:
    print("Folder:", folder_path)