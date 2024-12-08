import os
import shutil


def clear_folder(folder_path='html'):
    """
    Remove all contents inside the specified folder.

    Args:
    folder_path (str): Path to the folder to clear. Default is 'html'.
    """
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Iterate over all files and subdirectories in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if it's a file or directory and remove it
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directory
        print(f"All contents of the '{folder_path}' folder have been removed.")
    else:
        print(f"The folder '{folder_path}' does not exist.")
