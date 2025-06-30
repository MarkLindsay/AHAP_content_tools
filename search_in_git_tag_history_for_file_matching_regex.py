#!/usr/bin/env python3

import subprocess
import os
import re

"""
This script searches for a specific string in the objects folder of a Git repository for each tag.
It retrieves all tags, checks out each tag, and searches for the string in the objects folder.
It prints the tag name, file paths where the string is found, and the first two lines of each file.
It also handles errors gracefully and returns to the main branch after processing.
Be sure to start with a clean working directory, as it checks out each tag.
It is assumed that the repository has a structure where the objects folder exists at the root level.
"""

# Global variables
REPO_DIR = "/home/mark/OHOL/AHAP/AnotherPlanetData"  # Replace with your repository path
SEARCH_STRING = " 1332 "  # Define the search string globally
REVERSE_TAGS = False  # Set to True to reverse the order of tags
PAUSE_ON_MATCH = False  # Set to True to pause after matches are found
# SEARCH_FOLDER = "objects"  # Folder to search within each tag
SEARCH_FOLDER = "transitions"  # Folder to search within each tag

def check_clean_working_tree():
    """Ensure the working tree is clean before proceeding."""
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error checking Git status:", result.stderr)
        return False
    if result.stdout.strip():
        print("Error: Working tree is not clean. Please commit or stash your changes before running this script.")
        return False
    return True

def natural_sort(tags):
    """Sort tags in natural order."""
    def extract_key(tag):
        # Extract numeric parts for sorting
        return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', tag)]
    return sorted(tags, key=extract_key, reverse=REVERSE_TAGS)

def get_git_tags():
    """Retrieve all Git tags in the repository."""
    result = subprocess.run(['git', 'tag'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error retrieving Git tags:", result.stderr)
        return []
    tags = result.stdout.splitlines()
    return natural_sort(tags)  # Sort tags in natural order

def search_in_objects(tag):
    """Search for a string in the Objects folder for a specific Git tag."""
    # Checkout the tag
    subprocess.run(['git', 'checkout', tag], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Check if the Objects folder exists
    objects_path = os.path.join(REPO_DIR, SEARCH_FOLDER)
    if not os.path.exists(objects_path):
        print(f"Tag: {tag} - Objects folder does not exist.")
        return
    
    # Search for the string in the Objects folder
    grep_result = subprocess.run(
        ['grep', '-E', '-i', '-rl', SEARCH_STRING, objects_path],
        capture_output=True,
        text=True
    )
    
    if grep_result.returncode == 0:
        file_paths = grep_result.stdout.strip().split('\n')
        for file_path in file_paths:
            print(f"    File: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[:2]:  # Print the first two lines with indentation
                        print(f"        {line.strip()}")
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
        
        # Pause if matches are found and PAUSE_ON_MATCH is enabled
        if PAUSE_ON_MATCH:
            input("Matches found. Press Enter to continue to the next tag...")
    elif grep_result.returncode != 1:
        print(f"Error searching in tag {tag}: {grep_result.stderr.strip()}")

def main():
    # Change to the repository directory
    os.chdir(REPO_DIR)
    
    # Check if the working tree is clean
    if not check_clean_working_tree():
        return
    
    # Get all Git tags
    tags = get_git_tags()
    if not tags:
        print("No tags found.")
        return
    
    # Loop through each tag and search
    for tag in tags:
        print(f"Checking tag: {tag}")
        try:
            search_in_objects(tag)
        except subprocess.CalledProcessError as e:
            print(f"Error processing tag {tag}: {e}")
    
    # Checkout back to the main branch
    return_to_branch = 'master'
    subprocess.run(['git', 'checkout', return_to_branch], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()