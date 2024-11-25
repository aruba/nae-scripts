import ast
from os import listdir
from os.path import isfile, join
import subprocess
import json

SCRIPTS_DIRECTORY = "recommended_scripts/"

def get_last_modified_time(file_path):
    """Gets the last modified time of a file from Git."""
    try:
        result = subprocess.run(['git', 'log', '-1', '--format="%ad"', '--date=iso', file_path], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            last_modified_time = result.stdout.strip().replace('"', '')
            return last_modified_time
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def get_variable_value(code, variable_name):
    tree = ast.parse(code)

    class ValueFinder(ast.NodeVisitor):

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable_name:
                    if isinstance(node.value, ast.Constant):
                        self.value = node.value.value
                    else:
                        self.value = node.value

    finder = ValueFinder()
    finder.visit(tree)
    return finder.value

def parse_variable_dict(dict_object):
    keys_objects = dict_object.keys
    values_objects = dict_object.values
    keys = []
    values = []
    final_value_dict = {}
    for key in keys_objects:
        keys.append(key.value)
    for value in values_objects:
        if isinstance(value, ast.List):
            temp_list = []
            for list_object in value.elts:
                temp_list.append(list_object.value)
            values.append(temp_list)
        else:
            values.append(value.value)
    for i in range(len(values)):
        final_value_dict[keys[i]] = values[i]
    return final_value_dict

script_filepath = "../{}".format(SCRIPTS_DIRECTORY)
filenames = [f for f in listdir(script_filepath) if isfile(join(script_filepath, f))]

metadata_object = {"scripts": {}}

for filename in filenames:
    if filename in ["metadata.json", "metadata_generator.py"]:
        continue
    reader = open("{}{}".format(script_filepath, filename))
    dict_object = get_variable_value(reader.read(), "Manifest")
    manifest_object = parse_variable_dict(dict_object)
    script_object = {}
    script_name_with_version = "{}.{}".format(manifest_object["Name"], manifest_object["Version"])
    script_object["script_name"] = manifest_object["Name"]
    script_object["version"] = manifest_object["Version"]
    script_object["script_name_with_version"] = script_name_with_version
    script_object["tags"] = manifest_object["AOSCXPlatformList"]
    script_object["supported_platforms"] = manifest_object["AOSCXPlatformList"]
    script_object["minimum_firmware"] = manifest_object["AOSCXVersionMin"]
    script_object["maximum_firmware"] = None
    if 'AOSCXVersionMax' in manifest_object:
        script_object["minimum_firmware"] = manifest_object["AOSCXVersionMax"]
    script_object["description"] = manifest_object["Description"]
    # script_object["last_modified"] = get_last_modified_time(filename)
    script_object["last_modified"] = "sample_time"
    script_object["location"] = "{}{}".format(SCRIPTS_DIRECTORY, filename)
    metadata_object['scripts'][filename] = script_object

with open('metadata.json', 'w') as outfile:
    json.dump(metadata_object, outfile, indent=4)