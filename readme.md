[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

# AHAP Content Tools
These tools are intended to help manage "Another Hour Another Planet" (AHAP) objects. It's all written in python and uses only the standard library, but it uses subprocess to run git commands and in one nonessential script to use grep (noted below).


## Main Use
1. Clone the repo somewhere outside your game folders.
    - `git clone https://github.com/MarkLindsay/AHAP_content_tools.git /your/existing/folder/AHAP_content_tools`
2. Edit the **config.json**
    - data_source_path
        - put in the path to your AnotherPlanetData folder
    - content_parser_mode
        - choose which git tags to run the scripts on (of the AnotherPlanet_v## variety)
            - "working"
                - actually isn't any particular tag, it's your current working tree (i.e. the files you have currently)
            - "latest"
                - just the most recent tag
            - "missing"
                - all tags that aren't represented in this script's version folder
            - "all"
                - all tags (regenerates even if the version folder exists)
    - use_author_handles
        - This is only used in the leaderboards.
        - The file (author_handles.json) gets generated with empty names, and added to, when you run AHAP_content_leaderboard.py.
        - This file is untracked in the .gitignore... for privacy? Your author id is contained in the .oxz files you've shared, but I've left it out unless I can get consent to include a handle for you.
        - If you want to replace the author ids with a name, set this to true.
            - Also, fill out the names you want to associate with the author ids in author_handles.json after it gets generated for you.
3. Run **AHAP_content_parser.py**
    - this creates a folder either matching the tag or else "working" in the sub folder AHAP_Versions
    - nothing is modified in your AnotherPlanetData folder
    - content_xyz.json files are created for animations, objects, sounds, sprites, and transitions.
        - These should be equivalent to the original game data. They are meant to be straight conversions into json.
4. Run **AHAP_content_leaderboard.py**
    - this generates the leaderboard charts for animations, objects, sounds, sprites, and transitions.
        - leaderboard_all.txt has all the charts. The individual files are there for - I don't know why.
    - TODO
        - add music and ground tiles

## other scripts
These aren't in the best shape. Use at your own risk.
- AHAP_content_health.py
    - It's purpose is to check for errors in the original game data.
    - I remember it recreating the original game data files and comparing them to the actual game files to see if I could and what would be different.
- diff_list.py
    - I think I thought it would help me document changes to each version as I made them.
    - It just does git diff to grab object file names and formats it into markdown so I could add notes.
- import_trt_file.py
    - This one is handy if you can't get Wotte's importer/exporter working (like me on Linux).
    - The file management is ad-hoc. It might not even work.
    - You have to first import the .oxz into the Editor, take note of the first item number, and edit the script.
    - It worked the one time I needed it, but only after rolling back to the version the oxz was created from (else you likely have colliding sprite ids, or something).
- search_in_git_tag_history_for_file_matching_regex.py
    - Use this to find deleted objects in past versions.
    - This one uses grep
    - Edit the script to give it the search string
    - It checks out each git tag and searches all the files for your string
    - An optional pause before going to the next tag if searches have been found