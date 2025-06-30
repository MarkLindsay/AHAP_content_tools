import os
import re
import json
import glob
import subprocess

def get_pattern_object():
    return r"""id=(?P<id>\d+)\n
               (?P<name>^[^#=\n]*)((?P<tag_splitter>[# ]+)(?P<tags>[^\n]*))?\n
               containable=(?P<containable>\d+)\n
               containSize=(?P<containSize>\d+\.\d+),vertSlotRot=(?P<vertSlotRot>-?\d+\.\d+)\n
               permanent=(?P<permanent>\d+),minPickupAge=(?P<minPickupAge>\d+)\n
               noFlip=(?P<noFlip>\d+)\n
               sideAccess=(?P<sideAccess>\d+)\n
               heldInHand=(?P<heldInHand>\d+)\n
               blocksWalking=(?P<blocksWalking>\d+),leftBlockingRadius=(?P<leftBlockingRadius>\d+),rightBlockingRadius=(?P<rightBlockingRadius>\d+),drawBehindPlayer=(?P<drawBehindPlayer>\d+)\n
               mapChance=(?P<mapChance>\d+\.\d+)([#]biomes_(?P<biomes>.*))?\n
               heatValue=(?P<heatValue>-?\d+)\n
               rValue=(?P<rValue>\d+\.\d+)\n
               person=(?P<person>\d+),noSpawn=(?P<noSpawn>\d+)\n
               male=(?P<male>\d+)\n
               deathMarker=(?P<deathMarker>\d+)\n
               homeMarker=(?P<homeMarker>\d+)\n
               floor=(?P<floor>\d+)\n
               floorHugging=(?P<floorHugging>\d+)\n
               foodValue=(?P<foodValue>\d+)\n
               speedMult=(?P<speedMult>\d+\.\d+)\n
               heldOffset=(?P<heldOffsetX>-?\d+\.\d+),(?P<heldOffsetY>-?\d+\.\d+)\n
               clothing=(?P<clothing>[nhtbsp])\n
               clothingOffset=(?P<clothingOffsetX>-?\d+\.\d+),(?P<clothingOffsetY>-?\d+\.\d+)\n
               deadlyDistance=(?P<deadlyDistance>\d+)\n
               useDistance=(?P<useDistance>\d+)\n
               sounds=(?P<sound_creation>.+),(?P<sound_using>.+),(?P<sound_eating>.+),(?P<sound_decay>.+)\n
               creationSoundInitialOnly=(?P<creationSoundInitialOnly>\d+)\n
               creationSoundForce=(?P<creationSoundForce>\d+)\n
               numSlots=(?P<numSlots>\d+)[#]timeStretch=(?P<timeStretch>\d+\.\d+)\n
               slotSize=(?P<slotSize>\d+\.\d+)\n
               slotsLocked=(?P<slotsLocked>\d+)\n
               numSprites=(?P<numSprites>\d+)\n
               spritesAdditiveBlend=(?P<spritesAdditiveBlend>.*)\n
               spritesDrawnBehind=(?P<spritesDrawnBehind>.*)\n
               headIndex=(?P<headIndex>-?\d+)\n
               bodyIndex=(?P<bodyIndex>-?\d+)\n
               backFootIndex=(?P<backFootIndex>.+)\n
               frontFootIndex=(?P<frontFootIndex>.+)\n
               numUses=(?P<numUses>\d+),(?P<numUsesPer>\d+\.\d+)\n
               useVanishIndex=(?P<useVanishIndex>.*)\n
               useAppearIndex=(?P<useAppearIndex>.*)\n
               pixHeight=(?P<pixHeight>\d+)\n?
               author=(?P<author>\w+)"""


def get_pattern_sprite():
    return r"""(?P<name>\S*)[ ]
               (?P<number_1>-?\d+)[ ]
               (?P<number_2>-?\d+)[ ]
               (?P<number_3>-?\d+)[ ]
               author=(?P<author>\w+)"""


def get_pattern_transition_file_name():
    return r"""(?P<actor>-?\d+)_
               (?P<target>-?\d+)
               (_(?P<last_actor>LA))?
               (_(?P<last_target>LT))?"""


def get_pattern_transition():
    return r"""(?P<new_actor>-?\d+)[ ]
               (?P<new_target>-?\d+)[ ]
               (?P<auto_decay_seconds>-?\d+)[ ]
               (?P<actor_min_use_fraction>\d+\.\d+)[ ]
               (?P<target_min_use_fraction>\d+\.\d+)[ ]
               (?P<reverse_use_actor_flag>-?\d+)[ ]
               (?P<reverse_use_target_flag>-?\d+)[ ]
               (?P<move>-?\d+)[ ]
               (?P<desired_move_dist>-?\d+)[ ]
               (?P<no_use_actor_flag>-?\d+)[ ]
               (?P<no_use_target_flag>-?\d+)
               (?:\nauthor=(?P<author>\w+))?"""


def get_pattern_animation_file_name():
    return r"""(?P<animated_object>\d+)_
               (?:(?P<secondary_type>\d+)x)?
               (?P<animation_type>\d+)"""


def get_pattern_animation():
    # return r"""(?P<everything_before_author>.*)
    #            (?:\nauthor=(?P<author>\w+))?"""
    return r"""(?:author=(?P<author>\w+))"""


def get_pattern_sound_file_name():
    return r"""(?P<sound_id>\d+)"""


def get_pattern_sound():
    # return r"""(?P<everything_before_author>.*)
    #            (?:\nauthor=(?P<author>\w+))?"""
    return r"""(?:author=(?P<author>\w+)$)"""


def get_pattern_sprite_composition():
    return r"""spriteID=(?P<spriteID>\d+)\n
               pos=(?P<pos_x>-?\d+\.\d+),(?P<pos_y>-?\d+\.\d+)\n
               rot=(?P<rot>-?\d+\.\d+)\n
               hFlip=(?P<hFlip>[01])\n
               color=(?P<color_R>\d+\.\d+),(?P<color_G>\d+\.\d+),(?P<color_B>\d+\.\d+)\n
               ageRange=(?P<ageRange_min>-?\d+\.\d+),(?P<ageRange_max>-?\d+\.\d+)\n
               parent=(?P<parent>-?\d+)\n
               invisHolding=(?P<invisHolding>\d),invisWorn=(?P<invisWorn>\d),behindSlots=(?P<behindSlots>\d)\n
               (invisCont=(?P<invisCont>[01])\n)?"""


def get_pattern_slot_pos():
    return r"""slotPos=(?P<slotPosX>-?\d+\.\d+),(?P<slotPosY>-?\d+\.\d+),vert=(?P<vert>-?\d+),parent=(?P<parent>-?\d+)"""


def get_transition_attributes(transition_id, transition_text):
    attributes = {}
    # Get the attributes from the transition id
    attributes.update(get_regex_dict(
        transition_id, get_pattern_transition_file_name()))
    if attributes["last_actor"] != None:
        attributes["last_actor"] = True
    else:
        attributes["last_actor"] = False
    if attributes["last_target"] != None:
        attributes["last_target"] = True
    else:
        attributes["last_target"] = False
    # Get the attributes from the transition text
    attributes.update(get_regex_dict(
        transition_text, get_pattern_transition()))
    return attributes


def get_animation_attributes(animation_id, animation_text):
    attributes = {}
    # Get the attributes from the animation id
    attributes.update(get_regex_dict(
        animation_id, get_pattern_animation_file_name()))
    # Get the attributes from the animation text
    attributes.update(get_regex_dict(
        animation_text, get_pattern_animation()))
    return attributes


def get_sound_attributes(sound_id, sound_text):
    attributes = {}
    # Get the attributes from the sound id
    attributes.update(get_regex_dict(
        sound_id, get_pattern_sound_file_name()))
    # Get the attributes from the sound text
    attributes.update(get_regex_dict(
        sound_text, get_pattern_sound()))
    return attributes


def get_attributes_one_by_one(object_text, patterns):
    attributes = {}
    for pattern in patterns.split("\n"):
        pattern = re.compile(pattern, re.VERBOSE | re.MULTILINE)
        match = pattern.search(object_text)
        if match:
            attribute = {k: v for k, v in match.groupdict().items()}
        else:
            attribute = {k: None for k in pattern.groupindex.keys()}
        attributes.update(attribute)
    return attributes


def get_regex_dict(text, raw_pattern):
    raw_pattern = re.compile(raw_pattern, re.VERBOSE | re.MULTILINE | re.DOTALL)
    match = raw_pattern.search(text)
    if match:
        attributes_dict = {k: v for k, v in match.groupdict().items()}
    else:
        attributes_dict = {k: None for k in raw_pattern.groupindex.keys()}
    return attributes_dict


def extract_object_sprites(object_text):
    """
    Extract list of sprites.
    Also removes the sprite data from the object text before returning it.
    """
    pattern = re.compile(get_pattern_sprite_composition(), re.VERBOSE | re.MULTILINE)
    matches = pattern.finditer(object_text)
    sprites = [match.groupdict() for match in matches]
    text_reduced = pattern.sub("", object_text)
    return text_reduced, sprites


def extract_object_slotPos(object_text):
    """
    Extract list of slotPos.
    Also removes the slotPos data from the object text before returning it.
    """
    pattern = re.compile(get_pattern_slot_pos(), re.VERBOSE | re.MULTILINE)
    matches = pattern.finditer(object_text)
    slotPos = [match.groupdict() for match in matches]
    text_reduced = pattern.sub("", object_text)
    return text_reduced, slotPos


def get_file_text(object_path):
    if os.path.exists(object_path):
        try:
            with open(object_path, "r", encoding="utf-8", errors="replace") as file:
                lines = file.readlines()
                non_ascii_lines = [line for line in lines if any(ord(c) >= 128 for c in line)]
                if non_ascii_lines:
                    print(f"Non-ASCII characters found in {object_path}:")
                    for line in non_ascii_lines:
                        print(line.strip())
                ascii_lines = [line for line in lines if all(ord(c) < 128 for c in line)]
                return ''.join(ascii_lines)
        except UnicodeDecodeError:
            print(f"Error decoding file: {object_path}")
            return None
    else:
        print(f"File does not exist: {object_path}")
        return None


def get_text_file_names(data_path):
    text_files = glob.glob(data_path + "/*.txt")
    text_file_names = [re.split(r"[/]|[.]", text_file)[-2]
                       for text_file in text_files]
    return text_file_names


def write_json(data, path):
    with open(path, "w") as file:
        json.dump(data, file, indent=4, sort_keys=True)


def split_sound(sound_data):
    sounds = [
        {"sound_id": sound.split(":")[0], "sound_volume": sound.split(":")[1]}
        for sound in sound_data.split("#")
    ]
    return sounds


def regenerate_json_objects(data_path):
    object_file_names = get_text_file_names(data_path)
    object_ids = [
        file_name for file_name in object_file_names if file_name.isnumeric()]
    object_others = [
        file_name for file_name in object_file_names if not file_name.isnumeric()
    ]
    content_objects = {}
    for object_id in object_ids:
        object_file_path = os.path.join(data_path, f"{object_id}.txt")
        object_text = get_file_text(object_file_path)
        if object_text is not None:
            object_text, object_sprites = extract_object_sprites(object_text)
            object_text, object_slotPos = extract_object_slotPos(object_text)
            # if object_id == "1206":
            #     print(object_text)
            object_attributes = get_attributes_one_by_one(
                object_text, get_pattern_object())
            if object_attributes["biomes"]:
                object_attributes["biomes"] = object_attributes["biomes"].split(",")
            else:
                object_attributes["biomes"] = ["0"]
            # try:
            #     object_attributes["spritesAdditiveBlend"] = object_attributes["spritesAdditiveBlend"].split(",")
            # except AttributeError:
            #     object_attributes["spritesAdditiveBlend"] = []
            if object_attributes["spritesAdditiveBlend"] != None:
                object_attributes["spritesAdditiveBlend"] = object_attributes["spritesAdditiveBlend"].split(",")
            else:
                object_attributes["spritesAdditiveBlend"] = ["0"]
            
            if object_attributes["spritesDrawnBehind"] != None:
                object_attributes["spritesDrawnBehind"].split(",")
            else:
                object_attributes["spritesDrawnBehind"] = ["0"]
            
            object_attributes["useVanishIndex"] = object_attributes["useVanishIndex"].split(",")
            object_attributes["useAppearIndex"] = object_attributes["useAppearIndex"].split(",")
            
            object_attributes["sound_creation"] = split_sound(object_attributes["sound_creation"])
            object_attributes["sound_using"] = split_sound(object_attributes["sound_using"])
            object_attributes["sound_eating"] = split_sound(object_attributes["sound_eating"])
            object_attributes["sound_decay"] = split_sound(object_attributes["sound_decay"])
            
            object_attributes["backFootIndex"] = object_attributes["backFootIndex"].split(",")
            object_attributes["frontFootIndex"] = object_attributes["frontFootIndex"].split(",")
            
            content_objects[object_id] = object_attributes
            content_objects[object_id]["sprites"] = object_sprites
            content_objects[object_id]["slotPos"] = object_slotPos
        else:
            content_objects[object_id] = None
    sorted_content_objects = dict(
        sorted(content_objects.items(), key=lambda item: int(item[0])))
    return sorted_content_objects


def regenerate_json_sprites(data_path):
    sprite_file_names = get_text_file_names(data_path)
    sprite_ids = [
        file_name for file_name in sprite_file_names if file_name.isnumeric()]
    content_sprites = {}
    for sprite_id in sprite_ids:
        sprite_file_path = os.path.join(data_path, f"{sprite_id}.txt")
        sprite_text = get_file_text(sprite_file_path)
        if sprite_text is not None:
            sprite_attributes = get_attributes_one_by_one(
                sprite_text, get_pattern_sprite())
            content_sprites[sprite_id] = sprite_attributes
        else:
            content_sprites[sprite_id] = None
    sorted_content_sprites = dict(
        sorted(content_sprites.items(), key=lambda item: int(item[0])))
    return sorted_content_sprites


def regenerate_json_transitions(data_path):
    transition_file_names = get_text_file_names(data_path)
    transition_ids = transition_file_names
    # get transitions
    content_transitions = {}
    for transition_id in transition_ids:
        transition_file_path = os.path.join(data_path, f"{transition_id}.txt")
        transition_text = get_file_text(transition_file_path)
        if transition_text is not None:
            transition_attributes = get_transition_attributes(
                transition_id, transition_text
            )
            content_transitions[transition_id] = transition_attributes
        else:
            content_transitions[transition_id] = None
    # Define a custom sorting key function
    def sorting_key(item):
        transition = item[1]
        actor = int(transition.get("actor", ""))
        target = int(transition.get("target", ""))
        return (actor, target)
    # Sort the dictionary by the custom key
    sorted_content_transitions = dict(
        sorted(content_transitions.items(), key=sorting_key))
    return sorted_content_transitions


def regenerate_json_animations(data_path):
    animation_file_names = get_text_file_names(data_path)
    animation_ids = animation_file_names
    # get animations
    content_animations = {}
    for animation_id in animation_ids:
        animation_file_path = os.path.join(data_path, f"{animation_id}.txt")
        animation_text = get_file_text(animation_file_path)
        if animation_text is not None:
            animation_attributes = get_animation_attributes(
                animation_id, animation_text
            )
            content_animations[animation_id] = animation_attributes
        else:
            content_animations[animation_id] = None
    # Define a custom sorting key function
    def sorting_key(item):
        animation = item[1]
        animated_object = int(animation.get("animated_object", ""))
        animation_type = int(animation.get("animation_type", ""))
        return (animated_object, animation_type)
    # Sort the dictionary by the custom key
    sorted_content_animations = dict(
        sorted(content_animations.items(), key=sorting_key))
    return sorted_content_animations


def get_aiff_file_names(data_path):
    text_files = glob.glob(data_path + "/*.aiff")
    text_file_names = [re.split(r"[/]|[.]", text_file)[-2]
                       for text_file in text_files]
    return text_file_names


def regenerate_json_sounds(data_path):
    sound_file_authors = [id for id in get_text_file_names(data_path) if "nextSoundNumber" not in id]
    sound_file_authors = sorted(sound_file_authors, key=lambda item: int(item))
    sound_file_names = sorted(get_aiff_file_names(data_path), key=lambda item: int(item))
    sound_ids = sound_file_names
    # get sounds
    content_sounds = {}
    for sound_id in sound_ids:
        sound_file_path = os.path.join(data_path, f"{sound_id}.txt")
        sound_text = get_file_text(sound_file_path)
        if sound_text is not None:
            sound_attributes = get_sound_attributes(
                sound_id, sound_text
            )
            content_sounds[sound_id] = sound_attributes
        else:
            content_sounds[sound_id] = {"sound_id":sound_id, "author":None}
    # Define a custom sorting key function
    def sorting_key(item):
        sound = item[1]
        sound_id = int(sound.get("sound_id", ""))
        return (sound_id)
    # Sort the dictionary by the custom key
    sorted_content_sounds = dict(
        sorted(content_sounds.items(), key=sorting_key))
    return sorted_content_sounds


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as file:
        return json.load(file)


def get_content_paths(data_source_path, tag=None):
    """
    Returns a dictionary of all relevant paths.
    If tag is provided, returns paths for the versioned output directory.
    """
    base_paths = {
        "objects": os.path.join(data_source_path, "objects"),
        "sprites": os.path.join(data_source_path, "sprites"),
        "transitions": os.path.join(data_source_path, "transitions"),
        "animations": os.path.join(data_source_path, "animations"),
        "sounds": os.path.join(data_source_path, "sounds"),
    }
    if tag:
        script_dir = os.path.dirname(__file__)
        version_dir = os.path.join(script_dir, "AHAP_Versions", tag)
        base_paths.update({
            "script_dir": script_dir,
            "version_dir": version_dir,
            "objects_json": os.path.join(version_dir, "content_objects.json"),
            "sprites_json": os.path.join(version_dir, "content_sprites.json"),
            "transitions_json": os.path.join(version_dir, "content_transitions.json"),
            "animations_json": os.path.join(version_dir, "content_animations.json"),
            "sounds_json": os.path.join(version_dir, "content_sounds.json"),
        })
    return base_paths


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


def get_current_head():
    # Try to get the current branch name
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True)
    branch = result.stdout.strip()
    if branch != "HEAD":
        return branch  # On a branch
    # Detached HEAD, get commit hash
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return result.stdout.strip()


def get_git_tags():
    """Retrieve all Git tags in the repository."""
    result = subprocess.run(['git', 'tag'], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error retrieving Git tags:", result.stderr)
        return []
    tags = result.stdout.splitlines()
    return natural_sort(tags)

def get_matching_tags():
    tags = get_git_tags()
    return [tag for tag in tags if re.match(r"AnotherPlanet_v\d+", tag)]


def load_and_get_git_tags(data_source_path, how_many_latest_tags=1):
    """
    Change to the repo directory, ensure the working tree is clean, get, filter, and sort git tags.
    Raises RuntimeError if the working tree is not clean.
    Optionally filter tags using a function or substring.
    """
    os.chdir(data_source_path)
    if not check_clean_working_tree():
        raise RuntimeError("Working tree is not clean. Please commit or stash your changes before running this script.")
    tags = get_git_tags()
    tags = [tag for tag in tags if "AnotherPlanet_v" in tag]
    if how_many_latest_tags > 0:
        tags = [tags[-how_many_latest_tags]]
    return tags

def filter_tags_by_mode(tags, content_parser_mode, config):
    """
    Filter tags based on the specified mode.
    Modes:
    - "working": Returns only the "working" tag. (default mode)
    - "latest": Returns the latest tag.
    - "missing": Returns tags that are missing in the data source path.
    - "all": Returns all tags.
    """
    tags = [tag for tag in tags if "AnotherPlanet_v" in tag]
    match content_parser_mode:
        case "working":
            tags = ["working"]
        case "latest":
            tags = [tags[-1]]
        case "missing":
            tags = [tag for tag in tags if not os.path.exists(get_content_paths(config["data_source_path"], tag)["version_dir"])]
        case "all":
            pass
        case _:
            raise ValueError(f"Unknown content_parser_mode: {content_parser_mode}")
    return tags

def natural_sort(tags):
    """Sort tags in natural order."""
    def extract_key(tag):
        # Extract numeric parts for sorting
        return [int(part) if part.isdigit() else part for part in re.split(r'(\d+)', tag)]
    return sorted(tags, key=extract_key, reverse=False)


def main():
    config = load_config()
    # switch directories
    os.chdir(config["data_source_path"])
    # remember the current HEAD
    current_head = get_current_head()
    
    # develop the list of tags to work over
    content_parser_mode = config.get("content_parser_mode", "working")
    tags = get_git_tags()
    tags = filter_tags_by_mode(tags, content_parser_mode, config)
    
    # Loop through each tag
    for tag in tags:
        print(f"Processing: {tag}")
        if tag != "working":
            # Checkout the tag
            if not check_clean_working_tree():
                raise RuntimeError("Working tree is not clean. Please commit or stash your changes before running this script.")
            try:
                subprocess.run(['git', 'checkout', tag], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print(f"Error processing tag {tag}: {e}")
        
        # get paths
        paths = get_content_paths(config["data_source_path"], tag)
        # Ensure the version directory exists
        if not os.path.exists(paths["version_dir"]):
            os.makedirs(paths["version_dir"])
        
        # Regenerate JSON files
        print("Regenerating objects...")
        objects = regenerate_json_objects(paths["objects"])
        write_json(objects, paths["objects_json"])
        print(f"Regenerating objects is done: {len(objects)}")
        print()
        print("Regenerating sprites...")
        sprites = regenerate_json_sprites(paths["sprites"])
        write_json(sprites, paths["sprites_json"])
        print(f"Regenerating sprites is done: {len(sprites)}")
        print()
        print("Regenerating transitions...")
        transitions = regenerate_json_transitions(paths["transitions"])
        write_json(transitions, paths["transitions_json"])
        print(f"Regenerating transitions is done: {len(transitions)}")
        print()
        print("Regenerating animations...")
        animations = regenerate_json_animations(paths["animations"])
        write_json(animations, paths["animations_json"])
        print(f"Regenerating animations is done: {len(animations)}")
        print()
        print("Regenerating sounds...")
        sounds = regenerate_json_sounds(paths["sounds"])
        write_json(sounds, paths["sounds_json"])
        print(f"Regenerating sounds is done: {len(sounds)}")
        print()

    # Checkout back to your original branch or commit
    if content_parser_mode != "working":
        print(f"Returning to previous HEAD: {current_head}")
        subprocess.run(['git', 'checkout', current_head], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
