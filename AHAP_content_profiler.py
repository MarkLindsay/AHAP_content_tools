import os
import json
import AHAP_content_parser


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    return read_json(config_path)


def read_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def write_json(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)


def get_object_name_by_id(objects, object_id):
    object_id = str(object_id)
    if object_id == "0":
        name = "nothing"
    elif object_id == "-1":
        name = "nothing"
    elif object_id == "-2":
        name = "photo?"
    else:
        # if "Wild Squish Plant" in objects.get(object_id)['name']:
        #     the_thing = objects.get(object_id)
        #     pass
        try:
            name = objects.get(object_id)['name'].strip()
        except:
            name = ""
        try:
            tag_splitter = objects.get(object_id)['tag_splitter'].strip()
        except:
            tag_splitter = ""
        try:
            tags = objects.get(object_id)['tags'].strip()
        except:
            tags = ""
        name = f"{name} {tag_splitter} {tags}".strip()
    return name

def look_at_me(*args):
    pass


def main():
    config = load_config()
    data_source_path = config["data_source_path"]
    AHAP_content_parser.validate_data_source_path(data_source_path)

    # paths to JSON files
    script_dir = os.path.dirname(__file__)
    json_objects_path = os.path.join(script_dir, "content_objects.json")
    json_sprites_path = os.path.join(script_dir, "content_sprites.json")
    json_transitions_path = os.path.join(
        script_dir, "content_transitions.json")
    json_animations_path = os.path.join(script_dir, "content_animations.json")
    json_sounds_path = os.path.join(script_dir, "content_sounds.json")

    # load JSON files
    objects = read_json(json_objects_path)
    sprites = read_json(json_sprites_path)
    transitions = read_json(json_transitions_path)
    animations = read_json(json_animations_path)
    sounds = read_json(json_sounds_path)

    # convert names
    profiled_transitions = {}
    for id, transition in transitions.items():
        transition["actor"] = get_object_name_by_id(
            objects, transition["actor"])
        transition["target"] = get_object_name_by_id(
            objects, transition["target"])
        transition["new_actor"] = get_object_name_by_id(
            objects, transition["new_actor"])
        transition["new_target"] = get_object_name_by_id(
            objects, transition["new_target"])
    if True:
        for id, transition in transitions.items():
            if (transition["actor"] == "nothing" and
                transition["target"] == transition["new_target"] and
                transition["new_actor"] == "nothing" and
                transition["new_target"] != "nothing" and
                transition["auto_decay_seconds"] != "0" and
                transition["move"] == "0" and
                    transition["reverse_use_target_flag"] == "0"):
                try:
                    profiled_transitions["something_just_sitting_there?"].append(transition)
                except:
                    profiled_transitions["something_just_sitting_there?"] = [transition]
        
        for id, transition in transitions.items():
            if (transition["actor"] == "nothing" and
                transition["target"] == transition["new_target"] and
                transition["new_actor"] == "nothing" and
                transition["new_target"] != "nothing" and
                transition["auto_decay_seconds"] != "0" and
                transition["move"] == "0" and
                    transition["reverse_use_target_flag"] == "1"):
                try:
                    profiled_transitions["regenerating_uses"].append(transition)
                except:
                    profiled_transitions["regenerating_uses"] = [transition]
        
        for id, transition in transitions.items():
            if (transition["flag"] == "LA"and
                transition["target"] == "nothing"):
                try:
                    profiled_transitions["last_actor"].append(transition)
                except:
                    profiled_transitions["last_actor"] = [transition]
        
    profiled_objects = {}
    for id, object in objects.items():
            try:
                foodValue = object["foodValue"]
            except:
                foodValue = "0"
            if (foodValue != "0"):
                try:
                    profiled_objects["food"].append(object)
                except:
                    profiled_objects["food"] = [object]
    
    look_at_me(profiled_transitions["last_actor"], profiled_transitions["regenerating_uses"])


if __name__ == "__main__":
    main()
