#!/usr/bin/env python3
import os
import re

# Global variables
THIS_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
# (will be created if they do not exist)
TRTS_TO_BE_IMPORTED_FOLDER = os.path.join(THIS_SCRIPT_PATH, "to_be_imported")
GAME_DATA_FOLDER = "/home/mark/OHOL/AHAP/AnotherPlanetData"
OUTPUT_FOLDER = os.path.join(GAME_DATA_FOLDER, "transitions")
OXZ_MIN_OBJECT_ID = 1403

def setup_folders():
    """
    Sets up the necessary folders for the script.
    Creates the TRTS_TO_BE_IMPORTED_FOLDER and OUTPUT_FOLDER if they do not exist.
    """
    os.makedirs(TRTS_TO_BE_IMPORTED_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_trt_files():
    """
    Returns a list of TRT files in the TRTS_TO_BE_IMPORTED_FOLDER.
    The TRT files are expected to have a .trt extension.
    """
    setup_folders()  # Ensure folders are set up
    return [f for f in os.listdir(TRTS_TO_BE_IMPORTED_FOLDER) if f.endswith('.trt')]

def get_file_text(file_path):
    """
    Reads the content of the file at the given file_path and returns it as a string.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_old_ids(file_text):
    """
    Reads the first line of the file, splits it on commas, and returns an ordered list of integers.
    """
    first_line = file_text.splitlines()[0]  # Get the first line
    ordered_list = [int(x.strip()) for x in first_line.split(',') if x.strip().isdigit()]
    # reverse the list to match the order in the file
    ordered_list.reverse()
    return ordered_list

def is_list_unique(lst):
    """
    Checks if all elements in the list are unique.
    Returns True if unique, False otherwise.
    """
    return len(lst) == len(set(lst))

def replace_ids_in_text(file_text, replace_ids):
    """
    Replaces original object IDs with new IDs in the file text based on the provided mapping.
    Will replace numbers progressively, so be careful with the order of replacement.
    """
    # To avoid overlapping number space, replace IDs in two steps:
    # 1. Replace all original IDs with temporary unique placeholders.
    # 2. Replace placeholders with new IDs.

    # Step 1: Create temporary placeholders
    temp_map = {}
    for idx, orig_id in enumerate(replace_ids.keys()):
        temp_map[orig_id] = f"__TEMP_ID_{idx}__"
    print(temp_map)
    
    # Replace original IDs with placeholders, including IDs that may appear as part of filenames (e.g., 1621_1615.txt)
    for orig_id, temp_placeholder in temp_map.items():
        # Replace occurrences where the ID is surrounded by non-digit characters or at string boundaries
        file_text = re.sub(
            pattern=rf'(?<!\d){orig_id}(?!\d)',
            repl=temp_placeholder,
            string=file_text,
            count=0,
            flags=0
        )

    # Step 2: Replace placeholders with new IDs using re.sub for efficiency
    for orig_id, new_id in replace_ids.items():
        temp_placeholder = temp_map[orig_id]
        # Use re.escape to safely match the placeholder string
        pattern = re.compile(re.escape(temp_placeholder))
        file_text = pattern.sub(str(new_id), file_text)

    return file_text

def prepare_transition_files(new_text):
    """
    Saves off the transition files.
    """
    # remove the first line from the file text
    new_text = "\n".join(new_text.splitlines()[1:])  # Remove the first line
    new_text = re.sub(r'\n;;\s*$', '', new_text)  # Remove a trailing ';;' line if present
    file_blocks = re.split(r'\n;;\n', new_text)
    files_prepared = {}
    for block in file_blocks:
        if len(block.splitlines()) > 1:
            file_name = block.splitlines()[0].strip()  # Get the first line as the file name
            file_contents = "\n".join(block.splitlines()[1:]).strip()
            files_prepared[file_name] = file_contents  # Store the file contents without leading/trailing whitespace
    return files_prepared

def save_new_text(new_text, file_name):
    """
    Saves the new text to a file in the OUTPUT_FOLDER.
    """
    file_path = os.path.join(OUTPUT_FOLDER, file_name)
    try:
        with open(file_path, 'w') as file:
            file.write(new_text)
        print(f"Saved: {file_path}")
    except Exception as e:
        print(f"Error saving file {file_name}: {e}")


def save_transition_files(files_prepared, output_folder):
    """
    Saves the prepared transition files to the specified output folder.
    Each file is saved with its name and contents.
    """
    for file_name, file_contents in files_prepared.items():
        file_path = os.path.join(output_folder, file_name)
        try:
            with open(file_path, 'w') as file:
                file.write(file_contents)
            print(f"Saved: {file_path}")
        except Exception as e:
            print(f"Error saving file {file_name}: {e}")


if __name__ == "__main__":
    setup_folders()  # Ensure folders are set up
    trt_files = get_trt_files()
    if not trt_files:
        print("No TRT files found in the to_be_imported folder.")
    # process each TRT file completely before doing the next, else you may collide the number space.
    for each_file in trt_files:
        # get original ids
        TRT_FILE_PATH = os.path.join(TRTS_TO_BE_IMPORTED_FOLDER, each_file)
        file_text = get_file_text(TRT_FILE_PATH)  # Read the file content
        old_ids = get_old_ids(file_text)
        print(old_ids)
        
        # get new ids
        new_ids = list(range(OXZ_MIN_OBJECT_ID, OXZ_MIN_OBJECT_ID + len(old_ids)))
        print(new_ids)
        
        # replace ids in text
        if is_list_unique(old_ids) and is_list_unique(new_ids):
            # map original ids to new ids
            replace_ids = dict(zip(old_ids, new_ids))
            new_text = replace_ids_in_text(file_text, replace_ids)
        
        files_prepared = prepare_transition_files(new_text)
        
        # save new_text to files
        file_name = os.path.splitext(each_file)[0] + "_new.trt"
        file_path = os.path.join(OUTPUT_FOLDER, file_name)
        save_new_text(new_text, file_path)
        
        save_transition_files(files_prepared, OUTPUT_FOLDER)