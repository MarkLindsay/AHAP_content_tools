import os
import json
import subprocess
import AHAP_content_parser


def read_json(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def write_json(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


def count_attribute(items, attribute):
    # Initialize an empty dictionary to store the counts
    attribute_counts = {}

    # Iterate through the input dictionary
    for item_id, item_data in items.items():
        # Get the attribute value, defaulting to "blank" if not present
        value = item_data.get(attribute, None)
        if value is None:
            value = "blank"
        if value == "0" and attribute == "biomes":
            pass
        # Increment the count for the attribute value
        attribute_counts[value] = attribute_counts.get(value, 0) + 1

    # Sort the attribute counts by the count value in descending order
    sorted_attribute_counts = dict(
        sorted(attribute_counts.items(), key=lambda item: item[1], reverse=True)
    )

    # Return the sorted attribute counts and the total count as a tuple
    return sorted_attribute_counts


def generate_leaderboard(
    title, attribute, items, min_percent=-1.0, min_count=-1, top_how_many=-1
):
    # need to add one for returning just the top x leaders.
    item_counts = count_attribute(items, attribute)
    # Define column widths in a list
    column_widths = [
        max(10, len(attribute)),
        5,
        4,
        10,
    ]  # [attribute, count_width, percent_width, bar_width]
    bars = [
        " ",
        "▏",
        "▎",
        "▍",
        "▌",
        "▋",
        "▊",
        "▉",
        "█",
    ]  # full bar not used so there is a gap between "full" bars
    total = sum(item_counts.values())

    lines = []

    # ┌─────────────── Objects ────────────────┐
    lines.append(f"┌{' ' + title.capitalize() + ' ':─^{sum(column_widths) + 11}}┐")
    # │ author     │ Count │    % │ Bar        │
    lines.append(
        f"│ {attribute:<{column_widths[0]}} │ {'Count':>{column_widths[1]}} │ {'%':>{column_widths[2]}} │ {'Bar':<{column_widths[3]}} │"
    )
    # ├────────────┼───────┼──────┼────────────┤
    lines.append(
        f"├─{'':─<{column_widths[0]}}─┼─{'':─>{column_widths[1]}}─┼─{'':─^{column_widths[2]}}─┼─{'':─<{column_widths[3]}}─┤"
    )
    crop_flag = True
    counter = top_how_many
    for key, value in item_counts.items():
        percent = value / total
        if min_percent != -1.0:
            if percent < min_percent:
                if crop_flag:
                    # ├────────────┼───────┼──────┼────────────┤
                    # │........... Under 1% omitted ...........│
                    # lines.append(
                    #     f"├─{'':─<{column_widths[0]}}─┼─{'':─>{column_widths[1]}}─┼─{'':─^{column_widths[2]}}─┼─{'':─<{column_widths[3]}}─┤"
                    # )
                    lines.append(
                        f"│{' Percents under ' + str(int(min_percent*100)) + '% omitted ':.^{sum(column_widths) + 11}}│"
                    )
                    crop_flag = False
                continue
        if min_count != -1:
            if value < min_count:
                if crop_flag:
                    # ├────────────┼───────┼──────┼────────────┤
                    # │........... Under 1% omitted ...........│
                    # lines.append(
                    #     f"├─{'':─<{column_widths[0]}}─┼─{'':─>{column_widths[1]}}─┼─{'':─^{column_widths[2]}}─┼─{'':─<{column_widths[3]}}─┤"
                    # )
                    lines.append(
                        f"│{' Counts under ' + str(min_count) + ' omitted ':.^{sum(column_widths) + 11}}│"
                    )
                    crop_flag = False
                continue
        if top_how_many != -1:
            if counter < 1:
                if crop_flag:
                    # ├────────────┼───────┼──────┼────────────┤
                    # │........... Under 1% omitted ...........│
                    # lines.append(
                    #     f"├─{'':─<{column_widths[0]}}─┼─{'':─>{column_widths[1]}}─┼─{'':─^{column_widths[2]}}─┼─{'':─<{column_widths[3]}}─┤"
                    # )
                    lines.append(
                        f"│{' Top ' + str(top_how_many) + ' only ':.^{sum(column_widths) + 11}}│"
                    )
                    crop_flag = False
                continue
            counter -= 1

        full_bar = 10 * 8
        percent_bar = percent * full_bar
        if percent_bar < 1:
            pass
        full_bars = int(percent_bar // 8)
        partial_bar = int(round(percent_bar % 8, 0))
        if percent == 1:
            bar = bars[7] * full_bars
        else:
            bar = bars[7] * full_bars + bars[max(1, partial_bar - 1)]
        # │ 5ED1F9012B │   552 │  50% │ ▉▉▉▉▉      │
        author = get_author(key, column_widths[0])
        lines.append(
            f"│ {author:<{column_widths[0]}} │ {value:>{column_widths[1]}} │ {value/total:>{column_widths[2]}.0%} │ {bar:<{column_widths[3]}} │"
        )
    # ├────────────┼───────┼──────┼────────────┤
    lines.append(
        f"├─{'':─<{column_widths[0]}}─┼─{'':─>{column_widths[1]}}─┼─{'':─^{column_widths[2]}}─┼─{'':─<{column_widths[3]}}─┤"
    )
    # │     Totals │  1112 │ 100% │ ▉▉▉▉▉▉▉▉▉▉ │
    lines.append(
        f"│ {'Totals':>{column_widths[0]}} │ {total:>{column_widths[1]}} │ {1:>{column_widths[2]}.0%} │ {'▉▉▉▉▉▉▉▉▉▉':<{column_widths[3]}} │"
    )
    # └────────────┴───────┴──────┴────────────┘
    lines.append(
        f"└─{'':─<{column_widths[0]}}─┴─{'':─>{column_widths[1]}}─┴─{'':─^{column_widths[2]}}─┴─{'':─<{column_widths[3]}}─┘"
    )

    # Join the lines into a single string
    leaderboard = "\n".join(lines)
    return leaderboard


def save_leaderboard_all(leaderboard_dir):
    # Combine all leaderboard files into a single file
    output_file = os.path.join(leaderboard_dir, "leaderboard_all.txt")
    leaderboard_files = [
        "leaderboard_objects.txt",
        "leaderboard_sprites.txt",
        "leaderboard_transitions.txt",
        "leaderboard_animations.txt",
        "leaderboard_sounds.txt",
    ]

    with open(output_file, "w") as outfile:
        for i, fname in enumerate(leaderboard_files):
            with open(os.path.join(leaderboard_dir, fname)) as infile:
                outfile.write(infile.read())
                if i < len(leaderboard_files) - 1:
                    outfile.write("\n\n")  # Add a newline between files


def get_git_tag(path):
    try:
        result = subprocess.run(
            ["git", "describe", "--tags"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown_tag"


def get_author(author_id, column_width):
    config = AHAP_content_parser.load_config()
    if config.get("use_author_handles") == False:
        return author_id
    # get current script directory
    script_dir = os.path.dirname(__file__)
    author_handles = os.path.join(script_dir, "author_handles.json")
    if os.path.exists(author_handles):
        data = read_json(author_handles)
        handles = data.get(author_id, author_id)
        author = handles.get("handle", author_id)
        author = author[:column_width]
        if author == "":
            author = author_id
        return author
    else:
        return author_id


def get_object_name_by_id(objects, object_id):
    object_id = str(object_id)
    if object_id == "0":
        name = "nothing"
    elif object_id == "-1":
        name = "auto decay"
    elif object_id == "-2":
        name = "photo?"
    else:
        name = objects.get(object_id)["name"]
    return name


def main():
    config = AHAP_content_parser.load_config()
    # switch directories
    os.chdir(config["data_source_path"])
    # remember the current HEAD
    current_head = AHAP_content_parser.get_current_head()
    
    # develop the list of tags to work over
    content_parser_mode = config.get("content_parser_mode", "working")
    tags = AHAP_content_parser.get_git_tags()
    tags = AHAP_content_parser.filter_tags_by_mode(tags, content_parser_mode, config)

    # Loop through each tag
    for tag in tags:
        print(f"Processing: {tag}")
        if tag != "working":
            # Checkout the tag
            if not AHAP_content_parser.check_clean_working_tree():
                raise RuntimeError("Working tree is not clean. Please commit or stash your changes before running this script.")
            try:
                subprocess.run(['git', 'checkout', tag], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"Error processing tag {tag}: {e}")
        
        # get paths
        paths = AHAP_content_parser.get_content_paths(config["data_source_path"], tag)
        # Ensure the version directory exists
        if not os.path.exists(paths["version_dir"]):
            raise RuntimeError(f"Version directory {paths['version_dir']} does not exist. Please run AHAP_content_parser first.")

        # load JSON files
        objects = read_json(paths["objects_json"])
        sprites = read_json(paths["sprites_json"])
        transitions = read_json(paths["transitions_json"])
        animations = read_json(paths["animations_json"])
        sounds = read_json(paths["sounds_json"])

        # save leaderboard files
        # objects
        leaderboard = generate_leaderboard("Objects", "author", objects)
        output_path = os.path.join(paths["version_dir"], "leaderboard_objects.txt")
        with open(output_path, "w") as file:
            file.write(leaderboard)
        print(leaderboard)

        # sprites
        leaderboard = generate_leaderboard("Sprites", "author", sprites)
        output_path = os.path.join(paths["version_dir"], "leaderboard_sprites.txt")
        with open(output_path, "w") as file:
            file.write(leaderboard)
        print(leaderboard)

        # transitions
        leaderboard = generate_leaderboard("Transitions", "author", transitions)
        output_path = os.path.join(paths["version_dir"], "leaderboard_transitions.txt")
        with open(output_path, "w") as file:
            file.write(leaderboard)
        print(leaderboard)

        # animations
        leaderboard = generate_leaderboard("Animations", "author", animations)
        output_path = os.path.join(paths["version_dir"], "leaderboard_animations.txt")
        with open(output_path, "w") as file:
            file.write(leaderboard)
        print(leaderboard)

        # sounds
        leaderboard = generate_leaderboard("Sounds", "author", sounds)
        output_path = os.path.join(paths["version_dir"], "leaderboard_sounds.txt")
        with open(output_path, "w") as file:
            file.write(leaderboard)
        print(leaderboard)

        # all together
        save_leaderboard_all(paths["version_dir"])

        # save author files
        author_objects = {
            author: [v["name"] for k, v in objects.items() if v.get("author") == author]
            for author in set(v.get("author") for v in objects.values())
        }
        write_json(os.path.join(paths["version_dir"], "author_objects.json"), author_objects)

        author_sprites = {
            author: [v["name"] for k, v in sprites.items() if v.get("author") == author]
            for author in set(v.get("author") for v in sprites.values())
        }
        write_json(os.path.join(paths["version_dir"], "author_sprites.json"), author_sprites)

        author_transitions = {}
        for k, v in transitions.items():
            author = v.get("author")
            if author:
                if author not in author_transitions:
                    author_transitions[author] = []

                actor = get_object_name_by_id(objects, v["actor"])
                target = get_object_name_by_id(objects, v["target"])
                new_actor = get_object_name_by_id(objects, v["new_actor"])
                new_target = get_object_name_by_id(objects, v["new_target"])

                recipe = f"{actor} + {target} | {new_actor} & {new_target} | {k}"
                author_transitions[author].append(recipe)
        write_json(os.path.join(paths["version_dir"], "author_transitions.json"), author_transitions)

        # generate author handles file
        author_handles_path = os.path.join(paths["script_dir"], "author_handles.json")
        if not os.path.exists(author_handles_path):
            author_handles = {}
        else:
            author_handles = read_json(author_handles_path)
        all_authors = (
            set(author_handles.keys())
            .union(set(v.get("author") for v in objects.values()))
            .union(set(v.get("author") for v in sprites.values()))
            .union(set(v.get("author") for v in transitions.values()))
            .union(set(v.get("author") for v in animations.values()))
            .union(set(v.get("author") for v in sounds.values()))
        )
        for author in all_authors:
            if author == None:
                author = "blank"
                author_handles[author] = {"handle": "jason"}
            if author not in author_handles:
                author_handles[author] = {"handle": ""}
        write_json(author_handles_path, author_handles)

    # Checkout back to your original branch or commit
    if content_parser_mode != "working":
        print(f"Returning to previous HEAD: {current_head}")
        subprocess.run(['git', 'checkout', current_head], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
