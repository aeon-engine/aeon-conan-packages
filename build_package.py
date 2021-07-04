#!/usr/bin/python

import pathlib
import os
import sys
import yaml
from distutils.version import LooseVersion


def system(command):
    retcode = os.system(command)
    if retcode != 0:
        raise Exception("Error while executing:\n\t %s" % command)


def main(argv):
    if len(argv) < 1:
        raise Exception('Invalid argument count.')

    full_package_name = argv[0]
    package_namespace_split = full_package_name.split("@")

    if len(package_namespace_split) != 2:
        raise Exception('Given package must be name/version@user/channel or name@user/channel')

    package_name_split = package_namespace_split[0].split("/")
    package_name_split_components = len(package_name_split)

    if package_name_split_components != 1 and package_name_split_components != 2:
        raise Exception('Given package must be name/version@user/channel or name@user/channel')

    package_name = package_name_split[0]

    if package_name_split_components == 2 and package_name_split[1] != '':
        package_version = package_name_split[1]
    else:
        package_version = 'latest'

    user_channel_split = package_namespace_split[1].split("/")

    if len(user_channel_split) != 2:
        raise Exception('Given package must be name/version@user/channel')

    user = user_channel_split[0]
    channel = user_channel_split[1]

    package_root_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(),
        'recipes',
        package_name
    )

    if not os.path.exists(package_root_path):
        raise Exception('Unknown package')

    package_version_yaml = os.path.join(package_root_path, 'config.yml')

    with open(package_version_yaml, 'r') as stream:
        version_info = yaml.safe_load(stream)

        if package_version == 'latest':
            version_list = list(version_info['versions'].keys())

            if len(version_list) == 0:
                raise Exception('No versions.')

            version_list.sort(key=LooseVersion)

            package_version = version_list[0]
            print('Auto-selected version {}'.format(package_version), flush=True)

        if package_version not in version_info['versions']:
            raise Exception('Unknown package version')

        package_folder_name = version_info['versions'][package_version]['folder']

    full_package_path = os.path.join(package_root_path, package_folder_name)

    additional_params = " ".join(sys.argv[2:])

    full_package_name = '%s/%s@%s/%s' % (package_name, package_version, user, channel)

    with open('version.txt', 'w') as f:
        f.write(full_package_name)

    system('conan create %s %s %s' % (
        full_package_path, full_package_name, additional_params))


if __name__ == "__main__":
    main(sys.argv[1:])
