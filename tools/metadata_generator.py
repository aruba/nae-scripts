import ast
from os import listdir
from os.path import isdir, isfile, join
import subprocess
import json

SCRIPTS_DIRECTORY = "recommended_scripts/"
README_FILENAME = "README.md"
METADATA_GENERATOR_FILENAME = "metadata_generator.py"
PYTHON_FILENAME_EXTENSION = ".py"
DIRECTORY_ROOT_PREFIX = "../"

HIGH_LEVEL_README_HEADING = '''\
# Recommended NAE Scripts\n
These are the scripts recommended by HPE Aruba Networks for customers to use on their switches. \
These scripts have been tested and determined to add value.  Below is a list of all of the scripts with a short description. \
You can click on each script directory to see all available versions (different versions have different firwmare support), as \
well as a README with a more detailed description of each script.  All of these scripts can also be seen in the switch Web UI \
NAE script portal.\n
'''

LICENSES_AND_REFERENCES = '''\
## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
'''


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

def get_variable_value(code, variable_name, required):
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
    if not hasattr(finder, "value"):
        if required:
            print("Error: required variable {} was not found".format(variable_name, code))
            return None
        else:
            return None
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

def create_script_level_readme(long_description, summary, min_firmware, max_firmware, supported_platforms, script_version, script_name, metadata_object):
    # get all versions of this script
    long_description_string = ""
    if long_description is not None:
        long_description_string = long_description    
    script_versions = []
    current_version = float(script_version)
    for key in metadata_object['scripts']:
        if script_name in key:
            this_script_version_string = metadata_object['scripts'][key]['script_name_with_version'].replace("{}.".format(script_name), "")
            this_script_version = float(this_script_version_string)
            # check to see if this is newest version
            if this_script_version > current_version:
                # if not newest version, return None
                return None
            script_object = metadata_object['scripts'][key].copy()
            script_object['version'] = this_script_version_string
            script_versions.append(script_object)
    software_versions_string = ""
    platforms_string = ""
    for script_object in script_versions:
        minimum_version = "ArubaOS-CX {} Minimum".format(script_object['minimum_firmware'])
        maximum_version = ""
        if script_object['maximum_firmware'] is not None:
            maximum_version = ", ArubaOS-CX {} Maximum".format(script_object['maximum_firmware'])
        software_versions_string = "{}Script Version {}: {}{}\n".format(software_versions_string, script_object['version'], minimum_version, maximum_version)
        platforms_list_string = ""
        for platform in script_object["supported_platforms"]:
            platforms_list_string += "{}, ".format(platform)
        platforms_string = "{}Script Version {}: {}\n".format(platforms_string, script_object['version'], platforms_list_string.strip(", "))
    return '''\
## Summary

{}

## Supported Software Versions

{}
## Supported Platforms

{}
{}
## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
'''.format(summary, software_versions_string, platforms_string, long_description_string)

script_filepath = join(DIRECTORY_ROOT_PREFIX, SCRIPTS_DIRECTORY)
script_list = get_script_list(script_filepath)

metadata_object = {"scripts": {}}
high_level_description_object = {}

for (filename, filepath) in script_list:
    if filename in [METADATA_GENERATOR_FILENAME]:
        continue
    filepath_from_directory_root = filepath.replace(DIRECTORY_ROOT_PREFIX, "", 1)
    reader = open(filepath)
    read_info = reader.read()
    dict_object = get_variable_value(read_info, "Manifest", required=True)
    long_description = get_variable_value(read_info, "LONG_DESCRIPTION", required=False)
    manifest_object = parse_variable_dict(dict_object)
    script_object = {}
    script_name_with_version = "{}.{}".format(manifest_object["Name"], manifest_object["Version"])
    script_object["script_name_with_version"] = script_name_with_version
    script_object["supported_platforms"] = manifest_object["AOSCXPlatformList"]
    script_object["minimum_firmware"] = manifest_object["AOSCXVersionMin"]
    maximum_firmware = None
    if 'AOSCXVersionMax' in manifest_object:
        maximum_firmware = manifest_object["AOSCXVersionMax"]
    script_object["maximum_firmware"] = maximum_firmware
    script_object["description"] = manifest_object["Description"]
    script_object["last_modified"] = get_last_modified_time(filepath)
    script_object["location"] = filepath_from_directory_root
    metadata_object['scripts'][filename] = script_object
    high_level_description_object[manifest_object["Name"]] = manifest_object["Description"]
    # write long description to script-level README
    readme_filepath = join(filepath.replace(filename, "", 1), README_FILENAME)
    readme_file_contents = create_script_level_readme(
        long_description,
        manifest_object["Description"],
        manifest_object["AOSCXVersionMin"],
        maximum_firmware,
        manifest_object["AOSCXPlatformList"],
        manifest_object["Version"],
        manifest_object["Name"],
        metadata_object
    )
    if readme_file_contents is not None:
        with open(readme_filepath, 'w') as outfile:
            outfile.write(readme_file_contents)

# Create metadata file
with open('metadata.json', 'w') as outfile:
    json.dump(metadata_object, outfile, indent=4)

# Create high-level README file
with open(join(DIRECTORY_ROOT_PREFIX, SCRIPTS_DIRECTORY, README_FILENAME), 'w') as outfile:
    outfile.write(HIGH_LEVEL_README_HEADING)
    for script_name in high_level_description_object:
        outfile.write("### {}:\n{}\n\n".format(script_name, high_level_description_object[script_name]))
