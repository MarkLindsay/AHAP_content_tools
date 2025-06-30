#!/usr/bin/env python3
# This script generates a Markdown list of changed object files in the objects directory of a git repository.
# It gets the ID and name, and formats them into a Markdown list for comment on changes.

import os
import sys
import subprocess
import yaml
from pathlib import Path
import AHAP_content_parser

def get_changed_files(directory):
    # Change to directory to run git commands
    os.chdir(directory)
    # Get list of changed files using git diff
    result = subprocess.run(['git', 'diff', '--name-only'], 
                          capture_output=True, 
                          text=True)
    # Also get staged files
    staged = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                          capture_output=True,
                          text=True)
    
    # Combine both lists and filter for .txt files in objects directory
    all_changes = result.stdout.splitlines() + staged.stdout.splitlines()
    return [f for f in all_changes if f.startswith('objects/') and f.endswith('.txt')]

def parse_objects_directory(directory):
    # Get changed files
    changed_files = get_changed_files(directory)
    
    # Store objects to sort them later
    objects = {}
    
    for rel_path in changed_files:
        file_path = Path(directory) / rel_path
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    id_line = lines[0].strip()
                    name = lines[1].strip()
                    
                    if id_line.startswith('id='):
                        obj_id = id_line.split('=')[1]
                        objects[int(obj_id)] = {
                            'name': name,
                            'description': ''  # Placeholder for manual description
                        }
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
    
    # Sort by ID
    sorted_objects = dict(sorted(objects.items()))
    
    # Output as Markdown list
    print("# Changes:")
    for obj_id, data in sorted_objects.items():
        print(f"- {obj_id}: {data['name']}")
        print(f"    - {data['description']}" if data['description'] else "    - change")

if __name__ == "__main__":
    # configure the game data folder
    config = AHAP_content_parser.load_config()
    data_source_path = config["data_source_path"]
    parse_objects_directory(data_source_path)