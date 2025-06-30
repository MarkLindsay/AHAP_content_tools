import os
import json
import subprocess
import pprint
import AHAP_content_parser


def write_object_table(object_dict, object_table_path):
    for object_id, object_data in object_dict.items():
        # Remove the 'sprites' key if it exists
        if "sprites" in object_data:
            del object_data["sprites"]

        # write to plain text table
        # repeated_format = "{:>6}| {:<50}| {:<50}| " + "{:<30}| " * (len(object_data.keys()) - 3)
        repeated_format = "{:<50}| " * (len(object_data.keys()))
        linear_keys = repeated_format.format(*object_data.keys())
        linear_values = repeated_format.format(
            *object_data.values()
        )  # something wrong here

        with open(object_table_path, "a+") as file:
            file.seek(0)
            if len(file.readlines()) == 0:
                file.write(linear_keys + "\n")
                file.write(linear_values + "\n")
            else:
                file.write(linear_values + "\n")


def read_json(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def attribute_descriptions():
    return read_json(os.path.join(os.path.dirname(__file__), "content_object_atribute_descriptions.json"))


def get_default_object_attributes():
    return read_json(os.path.join(os.path.dirname(__file__), "content_object_attribute_defaults.json"))


def print_none_items(data_source_path, none_items):
    for none_id, none_attributes in none_items.items():
        print("")
        print(f"  Name: {none_attributes.get('name', none_id)}")
        print(f"  Path: {os.path.join(data_source_path, none_id + '.txt')}")
        print("  Attributes that equal None:")
        for none_attribute in none_attributes["none_keys"]:
            print(f"    {none_attribute}")


def check_for_utf8_errors(source_dir):
    # loop object files and if there is a utf-8 error, print the file path
    file_names = AHAP_content_parser.get_text_file_names(source_dir)
    file_paths = [
        os.path.join(source_dir, file_name + ".txt") for file_name in file_names
    ]
    broken_files = []
    for file_path in file_paths:
        try:
            with open(file_path, "r") as file:
                file.readlines()
        except UnicodeDecodeError:
            broken_files.append(file_path)
    if broken_files:
        print()
        print(f"{len(broken_files)} files with UnicodeDecodeError in that directory:")
        for broken_file in broken_files:
            print("\t", broken_file)
    else:
        print()
        print(f"0 files with UnicodeDecodeError in: {source_dir}")
    return broken_files

def get_attributes_with_none(data):
    # gather data with missing attributes
    # get a list of all attributes
    data_attributes = list(next(iter(data.values())).keys())
    # for each attribute, get a list of data with that attribute missing
    data_attributes_with_none = {}
    for attribute in data_attributes:
        filtered_data = {k: v for k,
                         v in data.items() if v[attribute] == None}
        data_attributes_with_none[attribute] = filtered_data
    # remove attributes that have no missing values
    data_attributes_with_none = {
        k: v for k, v in data_attributes_with_none.items() if v != {}}
    # sort the attributes by the number of missing values
    data_attributes_with_none = dict(sorted(
        data_attributes_with_none.items(), key=lambda item: len(item[1]), reverse=True))
    return data_attributes_with_none


def write_content_object(data, path):
    if data["author"] != None:
        author = f"\nauthor={data['author']}"
    else:
        author = ""
    
    if data["noFlip"] != None:
        noFlip = f"noFlip={data['noFlip']}\n"
    else:
        noFlip = ""
    
    if data["sideAccess"] != None:
        sideAccess = f"sideAccess={data['sideAccess']}\n"
    else:
        sideAccess = ""
    
    if data["creationSoundForce"] != None:
        creationSoundForce = f"creationSoundForce={data['creationSoundForce']}\n"
    else:
        creationSoundForce = ""
    
    if data["tags"] != None:
        name_and_tags = f"{data['name']}{data['tag_splitter']}{data['tags']}"
    else:
        name_and_tags = data["name"]
    
    if data["spritesAdditiveBlend"] != ["0"]:
        spritesAdditiveBlend_list = ",".join(data['spritesAdditiveBlend'])
        spritesAdditiveBlend = f"spritesAdditiveBlend={spritesAdditiveBlend_list}\n"
    else:
        spritesAdditiveBlend = ""
        
    if data["spritesDrawnBehind"] != ["0"]:
        spritesDrawnBehind_list = ",".join(data['spritesDrawnBehind'].split(","))
        spritesDrawnBehind = f"spritesDrawnBehind={spritesDrawnBehind_list}\n"
    else:
        spritesDrawnBehind = ""
    
    biomes_list = ",".join(data['biomes'])
    useVanishIndex_list = ",".join(data['useVanishIndex'])
    useAppearIndex_list = ",".join(data['useAppearIndex'])
    backFootIndex_list = ",".join(data['backFootIndex'])
    frontFootIndex_list = ",".join(data['frontFootIndex'])
    
    sprites = ""
    for sprite in data["sprites"]:
        if sprite['invisCont'] != None:
            invisCont = f"invisCont={sprite['invisCont']}\n"
        else:
            invisCont = ""
        sprite_text = (f"spriteID={sprite['spriteID']}\n"
                       f"pos={sprite['pos_x']},{sprite['pos_y']}\n"
                       f"rot={sprite['rot']}\n"
                       f"hFlip={sprite['hFlip']}\n"
                       f"color={sprite['color_R']},{sprite['color_G']},{sprite['color_B']}\n"
                       f"ageRange={sprite['ageRange_min']},{sprite['ageRange_max']}\n"
                       f"parent={sprite['parent']}\n"
                       f"invisHolding={sprite['invisHolding']},invisWorn={sprite['invisWorn']},behindSlots={sprite['behindSlots']}\n"
                       f"{invisCont}")
        sprites += sprite_text
    
    slotPos = ""
    for slot in data["slotPos"]:
        slot_text = (f"slotPos={slot['slotPosX']},{slot['slotPosY']},vert={slot['vert']},parent={slot['parent']}\n")
        slotPos += slot_text
    
    sounds = "sounds="
    for index, sound in enumerate(data["sound_creation"]):
        this_sound = f"{sound['sound_id']}:{sound['sound_volume']}"
        if index == 0:
            sounds = sounds + this_sound
        else:
            sounds = sounds + "#" + this_sound
    for index, sound in enumerate(data["sound_using"]):
        this_sound = f"{sound['sound_id']}:{sound['sound_volume']}"
        if index == 0:
            sounds = sounds + "," + this_sound
        else:
            sounds = sounds + "#" + this_sound
    for index, sound in enumerate(data["sound_eating"]):
        this_sound = f"{sound['sound_id']}:{sound['sound_volume']}"
        if index == 0:
            sounds = sounds + "," + this_sound
        else:
            sounds = sounds + "#" + this_sound
    for index, sound in enumerate(data["sound_decay"]):
        this_sound = f"{sound['sound_id']}:{sound['sound_volume']}"
        if index == 0:
            sounds = sounds + "," + this_sound
        else:
            sounds = sounds + "#" + this_sound
    
    
    text = (f"id={data['id']}\n"
            f"{name_and_tags}\n"
            f"containable={data['containable']}\n"
            f"containSize={data['containSize']},vertSlotRot={data['vertSlotRot']}\n"
            f"permanent={data['permanent']},minPickupAge={data['minPickupAge']}\n"
            f"{noFlip}"
            f"{sideAccess}"
            f"heldInHand={data['heldInHand']}\n"
            f"blocksWalking={data['blocksWalking']},leftBlockingRadius={data['leftBlockingRadius']},rightBlockingRadius={data['rightBlockingRadius']},drawBehindPlayer={data['drawBehindPlayer']}\n"
            f"mapChance={data['mapChance']}#biomes_{biomes_list}\n"
            f"heatValue={data['heatValue']}\n"
            f"rValue={data['rValue']}\n"
            f"person={data['person']},noSpawn={data['noSpawn']}\n"
            f"male={data['male']}\n"
            f"deathMarker={data['deathMarker']}\n"
            f"homeMarker={data['homeMarker']}\n"
            f"floor={data['floor']}\n"
            f"floorHugging={data['floorHugging']}\n"
            f"foodValue={data['foodValue']}\n"
            f"speedMult={data['speedMult']}\n"
            f"heldOffset={data['heldOffsetX']},{data['heldOffsetY']}\n"
            f"clothing={data['clothing']}\n"
            f"clothingOffset={data['clothingOffsetX']},{data['clothingOffsetY']}\n"
            f"deadlyDistance={data['deadlyDistance']}\n"
            f"useDistance={data['useDistance']}\n"
            f"{sounds}\n"
            f"creationSoundInitialOnly={data['creationSoundInitialOnly']}\n"
            f"{creationSoundForce}"
            f"numSlots={data['numSlots']}#timeStretch={data['timeStretch']}\n"
            f"slotSize={data['slotSize']}\n"
            f"slotsLocked={data['slotsLocked']}\n"
            f"{slotPos}"
            f"numSprites={data['numSprites']}\n"
            f"{sprites}"
            f"{spritesAdditiveBlend}"
            f"{spritesDrawnBehind}"
            f"headIndex={data['headIndex']}\n"
            f"bodyIndex={data['bodyIndex']}\n"
            f"backFootIndex={backFootIndex_list}\n"
            f"frontFootIndex={frontFootIndex_list}\n"
            f"numUses={data['numUses']},{data['numUsesPer']}\n"
            f"useVanishIndex={useVanishIndex_list}\n"
            f"useAppearIndex={useAppearIndex_list}\n"
            f"pixHeight={data['pixHeight']}"
            f"{author}"
            )
    # write to file
    with open(path, "w") as file:
        file.write(text)


# Function to delete all files in the directory
def clear_directory(directory_path):
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # Remove the file
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as file:
        return json.load(file)

def main():
    # configure the game data folder
    config = load_config()
    data_source_path = config["data_source_path"]
    AHAP_content_parser.validate_data_source_path(data_source_path)

    # Change to the repository directory
    os.chdir(data_source_path)
    
    # Check if the working tree is clean
    if not AHAP_content_parser.check_clean_working_tree():
        return
    
    # Get all Git tags
    tags = AHAP_content_parser.get_git_tags()
    if not tags:
        print("No tags found.")
        return
    # tags = ['AnotherPlanet_v1', 'AnotherPlanet_v2', 'AnotherPlanet_v3', 'AnotherPlanet_v4', 'AnotherPlanet_v5', 'AnotherPlanet_v6', 'AnotherPlanet_v7', 'AnotherPlanet_v8', 'AnotherPlanet_v9', 'AnotherPlanet_v10', 'AnotherPlanet_v11', 'AnotherPlanet_v12', 'AnotherPlanet_v13', 'AnotherPlanet_v14', 'AnotherPlanet_v15', 'AnotherPlanet_v16', 'AnotherPlanet_v17', 'AnotherPlanet_v18', 'AnotherPlanet_v19', 'AnotherPlanet_v20', 'AnotherPlanet_v21', 'AnotherPlanet_v22', 'AnotherPlanet_v23', 'AnotherPlanet_v24', 'AnotherPlanet_v25', 'AnotherPlanet_v26', 'AnotherPlanet_v27', 'AnotherPlanet_v28', 'AnotherPlanet_v29', 'AnotherPlanet_v30', 'AnotherPlanet_v31', 'AnotherPlanet_v32', 'AnotherPlanet_v33', 'AnotherPlanet_v34', 'AnotherPlanet_v35', 'AnotherPlanet_v36', 'AnotherPlanet_v37', 'AnotherPlanet_v38', 'AnotherPlanet_v39', 'AnotherPlanet_v40', 'AnotherPlanet_v41', 'AnotherPlanet_v42', 'AnotherPlanet_v43', 'AnotherPlanet_v44', 'AnotherPlanet_v45', 'AnotherPlanet_v46', 'AnotherPlanet_v47', 'AnotherPlanet_v48', 'AnotherPlanet_v49', 'AnotherPlanet_v50', 'AnotherPlanet_v51', 'AnotherPlanet_v52', 'AnotherPlanet_v53', 'AnotherPlanet_v54', 'AnotherPlanet_v55']
    tags = ['AnotherPlanet_v54']
    # Loop through each tag and search
    for tag in tags:
        # Checkout the tag
        print(f"Checking tag: {tag}")
        try:
            subprocess.run(['git', 'checkout', tag], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Error processing tag {tag}: {e}")
        
        # load content data
        script_dir = os.path.dirname(__file__)
        tag_dir = os.path.join(script_dir, tag)
        json_objects_path = os.path.join(tag_dir, "content_objects.json")
        json_sprites_path = os.path.join(tag_dir, "content_sprites.json")
        json_transitions_path = os.path.join(tag_dir, "content_transitions.json")

        # option to regenerate JSON files
        regen_json = False
        if regen_json:
            # Define paths for each type of content
            object_source_path = os.path.join(data_source_path, "objects")
            sprite_source_path = os.path.join(data_source_path, "sprites")
            transition_source_path = os.path.join(data_source_path, "transitions")
            # Regenerate JSON files
            AHAP_content_parser.regenerate_json_objects(
                object_source_path, json_objects_path
            )
            AHAP_content_parser.regenerate_json_sprites(
                sprite_source_path, json_sprites_path
            )
            AHAP_content_parser.regenerate_json_transitions(
                transition_source_path, json_transitions_path
            )

        # load JSON files
        objects = read_json(json_objects_path)
        sprites = read_json(json_sprites_path)
        transitions = read_json(json_transitions_path)


        # find objects with None attributes
        exclude_keys = [
            "tags",
            "author",
        ]  # these are optional attributes

        # temporary filter
        # objects = {k: v for k, v in objects.items() if 93 <= int(v['id']) <= 97}
        # objects = {k: v for k, v in objects.items() if 0 <= int(v['id']) <= 1000000}
        # objects = {k: v for k, v in objects.items() if int(v['id']) == 769}
        # objects = {k: v for k, v in objects.items() if int(v['id']) == 82004}
        # objects = {k: v for k, v in objects.items() if int(v['id']) == 1206}
    
    
        count_correct = 0
        count_wrong = 0
        non_invertible_objects = {}
        invertible_objects = {}
    
        # Clear the directory
        fixit_folder = os.path.join(script_dir, "fixed")
        clear_directory(fixit_folder)
    
        for id, data in objects.items():
            # text_path = data["path_to_text"]
            # config = AHAP_content_parser.load_config()
            # data_source_path = config["data_source_path"]
            object_path = os.path.join(data_source_path, "objects", f"{id}.txt")
            original_text = AHAP_content_parser.get_file_text(object_path)
            fixit_path = os.path.join(script_dir, "fix.txt")
            write_content_object(objects[id], fixit_path)
            fixed_text = AHAP_content_parser.get_file_text(fixit_path)
            if original_text != fixed_text:
                fixit_path = os.path.join(fixit_folder, f"{id}.txt")
                write_content_object(objects[id], fixit_path)
                count_wrong += 1
                non_invertible_objects[id] = data
                
                print(f"\n{object_path}")
                print(f"{fixit_path}")
            else:
                count_correct += 1
                invertible_objects[id] = data
        
        print(f"Correct: {count_correct}")
        print(f"Wrong: {count_wrong}")
    exit()
    
    
    # fixing things...
    objects_attributes_with_none = get_attributes_with_none(objects)
    print(len(objects_attributes_with_none))

    # apply default values to missing attributes
    # this doesn't catch right the ones that don't have keywords in the text.
    defaults = get_default_object_attributes()
    for attribute, default_value in defaults.items():
        attributes_as_none = {k: v for k,
                              v in objects.items() if v[attribute] is None}
        for id, data in attributes_as_none.items():
            # text_path = data["path_to_text"]
            config = AHAP_content_parser.load_config()
            data_source_path = config["data_source_path"]
            object_path = os.path.join(data_source_path, "objects", f"{id}.txt")
            text = AHAP_content_parser.get_file_text(object_path)
            if attribute not in text:
                objects[id][attribute] = default_value
                pass
        write_content_object(objects[id], os.path.join(script_dir, "fix.txt"))

    # gather objects with missing attributes
    objects_attributes_with_none = get_attributes_with_none(objects)
    print(len(objects_attributes_with_none))
    # sprites_attributes_with_none = get_attributes_with_none(sprites)
    # transitions_attributes_with_none = get_attributes_with_none(transitions)

    exit()

    # let's focus on one attribute at a time. Analyze how it's getting it wrong,
    # then devise and algorythm to fix it.
    # focused_items = objects_attributes_with_none['containSize']
    # for item_id, item_data in focused_items.items():
    #     config = AHAP_content_parser.load_config()
    #     data_source_path = config["data_source_path"]
    #     object_path = os.path.join(data_source_path, "objects", f"{item_id}.txt")
    #     print(object_path)
    #     item_text_path = object_path
    #     item_text = AHAP_content_parser.get_file_text(item_text_path)

    #     attributes = {}
    #     # float
    #     pattern = r"""containSize=(?P<containSize>\d+\.\d+),"""
    #     attributes = AHAP_content_parser.get_regex_dict(item_text, pattern)
    #     if attributes["containSize"] is not None:
    #         print(f"float: {attributes['containSize']}")
    #     # integer
    #     pattern = r"""containSize=(?P<containSize>\d+),"""
    #     attributes = AHAP_content_parser.get_regex_dict(item_text, pattern)
    #     if attributes["containSize"] is not None:
    #         print(f"integer: {attributes['containSize']}")

    # focused_items = {k: v for k, v in objects.items() if (
    #     0 <= int(v['id']) <= 1000000)}

    exit()


if __name__ == "__main__":
    main()
