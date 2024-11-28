import ast
from os import listdir
from os.path import isdir, isfile, join
import subprocess
import json

# TODO:
# - Generate high-level and script-level READMEs
# - Get description for high-level README
# - Create directories for each script
# - Add long description to scripts
# - Get long description for script-level README

SCRIPTS_DIRECTORY = "recommended_scripts/"
METADATA_GENERATOR_FILENAME = "metadata_generator.py"
PYTHON_FILENAME_EXTENSION = ".py"
DIRECTORY_ROOT_PREFIX = "../"


def get_last_modified_time(file_path):
    """Gets the last modified time of a file from Git."""
    try:
        result = subprocess.run(['git', 'log', '-1', '--format="%ad"', '--date=format-local:"%m/%d/%y %H:%M:%S"', file_path], 
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

def get_script_list(script_filepath):
    filename_list = []
    for f in listdir(script_filepath):
        path = join(script_filepath, f)
        if isfile(path):
            if path.lower().endswith((PYTHON_FILENAME_EXTENSION)):
                filename_list.append((f, path))
        elif isdir(path):
            filename_list += get_script_list(path)
        else:
            print("Error getting filename for path {}".format(path))
    return filename_list

script_filepath = join(DIRECTORY_ROOT_PREFIX, SCRIPTS_DIRECTORY)
script_list = get_script_list(script_filepath)

metadata_object = {"scripts": {}}

for (filename, filepath) in script_list:
    if filename in [METADATA_GENERATOR_FILENAME]:
        continue
    filepath_from_directory_root = filepath.replace(DIRECTORY_ROOT_PREFIX, "", 1)
    reader = open(filepath)
    dict_object = get_variable_value(reader.read(), "Manifest")
    manifest_object = parse_variable_dict(dict_object)
    script_object = {}
    script_name_with_version = "{}.{}".format(manifest_object["Name"], manifest_object["Version"])
    script_object["script_name_with_version"] = script_name_with_version
    script_object["supported_platforms"] = manifest_object["AOSCXPlatformList"]
    script_object["minimum_firmware"] = manifest_object["AOSCXVersionMin"]
    script_object["maximum_firmware"] = None
    if 'AOSCXVersionMax' in manifest_object:
        script_object["minimum_firmware"] = manifest_object["AOSCXVersionMax"]
    script_object["description"] = manifest_object["Description"]
    script_object["last_modified"] = get_last_modified_time(filepath)
    script_object["location"] = filepath_from_directory_root
    metadata_object['scripts'][filename] = script_object

with open('metadata.json', 'w') as outfile:
    json.dump(metadata_object, outfile, indent=4)