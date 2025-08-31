# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import os
import sys
import ctypes
import shutil

moved_count = 0
error_count = 0

def to_long_path(path):
    path = os.path.abspath(path)
    if not path.startswith("\\\\?\\"):
        if path.startswith("\\\\"):  # UNC path
            path = "\\\\?\\UNC\\" + path[2:]
        else:
            path = "\\\\?\\" + path
    return path

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()

def organize_files(cwd):
    global moved_count, error_count
    for root, dirs, files in os.walk(cwd, topdown=False):
        for file in files:
            try:
                file_path = to_long_path(os.path.join(root, file))
                folder_path = to_long_path(os.path.join(root, os.path.splitext(file)[0]))
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                dest_path = to_long_path(os.path.join(folder_path, file))
                # If file already exists, make a unique name
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(file)
                    counter = 1
                    while os.path.exists(to_long_path(os.path.join(folder_path, f"{base}_{counter}{ext}"))):
                        counter += 1
                    dest_path = to_long_path(os.path.join(folder_path, f"{base}_{counter}{ext}"))
                shutil.move(file_path, dest_path)
                moved_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        run_as_admin()
    cwd = to_long_path(os.getcwd())
    print(f"Current working directory: {cwd}")
    try:
        organize_files(cwd)
    except Exception as e:
        print(f"Failed to organize files in {cwd}: {e}")
    finally:
        print(f"\nSummary:")
        print(f"  Files moved:   {moved_count}")
        print(f"  Errors:        {error_count}")
        os.system("cmd /k")
