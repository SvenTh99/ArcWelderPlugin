# coding=utf-8
# #################################################################################
# Arc Welder: Anti-Stutter
#
# A plugin for OctoPrint that converts G0/G1 commands into G2/G3 commands where possible and ensures that the tool
# paths don't deviate by more than a predefined resolution.  This compresses the gcode file size, and reduces the number of gcodes per second sent to a 3D printer that supports arc commands (G2 G3)
#
# Copyright (C) 2020  Brad Hochgesang
# #################################################################################
# This program is free software:
# you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see the following:
# https://github.com/FormerLurker/ArcWelderPlugin/blob/master/LICENSE
#
# You can contact the author either through the git-hub repository, or at the
# following email address: FormerLurker@pm.me
##################################################################################
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import platform
import versioneer
import octoprint.server
from packaging.version import Version
import subprocess

########################################################################################################################
# The plugin's identifier, has to be unique
plugin_identifier = "arc_welder"
plugin_package = "octoprint_arc_welder"
plugin_name = "Arc Welder"
fallback_version = "1.0.0"
plugin_version = versioneer.get_version()
if plugin_version == "0+unknown" or Version(plugin_version) < Version(fallback_version):
    plugin_version = fallback_version
    try:
        plugin_version += "+u." + versioneer.get_versions()["full-revisionid"][0:7]
    except:
        pass
    print("Unknown Version, falling back to " + plugin_version + ".")

plugin_cmdclass = versioneer.get_cmdclass()
plugin_description = """Converts line segments to curves, which reduces the number of gcodes per second, hopefully eliminating stuttering."""
plugin_author = "Brad Hochgesang"
plugin_author_email = "FormerLurker@pm.me"
plugin_url = "https://github.com/FormerLurker/ArcWelderPlugin"
plugin_license = "AGPLv3"
plugin_requires = ["six", "OctoPrint>1.3.8", "setuptools>=6.0"]

if Version(octoprint.server.VERSION) < Version("1.4"):
    plugin_requires.extend(["flask_principal>=0.4,<1.0"])

if (3, 0) < sys.version_info < (3, 3):
    print("Adding faulthandler requirement.")
    plugin_requires.append("faulthandler>=3.1")

plugin_additional_data = ["data/*.json", "data/lib/c/*.cpp", "data/lib/c/*.h"]
plugin_additional_packages = ["octoprint_arc_welder_setuptools"]

# --------------------------------------------------------------------------------------------------------------------
# More advanced options
# --------------------------------------------------------------------------------------------------------------------

# Ensure CMake is installed
try:
    subprocess.check_call(["cmake", "--version"])
except FileNotFoundError:
    raise RuntimeError("CMake is not installed. Please install it to build C++ extensions.")

# C++ Extension compiler setup using CMake
plugin_ext_sources = [
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/array_list.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/circular_buffer.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/extruder.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/gcode_comment_processor.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/gcode_parser.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/gcode_position.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/parsed_command.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/parsed_command_parameter.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/position.cpp",
    "octoprint_arc_welder/data/lib/c/gcode_processor_lib/utilities.cpp",
    "octoprint_arc_welder/data/lib/c/arc_welder/arc_welder.cpp",
    "octoprint_arc_welder/data/lib/c/arc_welder/segmented_arc.cpp",
    "octoprint_arc_welder/data/lib/c/arc_welder/segmented_shape.cpp",
    "octoprint_arc_welder/data/lib/c/py_arc_welder/py_logger.cpp",
    "octoprint_arc_welder/data/lib/c/py_arc_welder/py_arc_welder.cpp",
    "octoprint_arc_welder/data/lib/c/py_arc_welder/py_arc_welder_extension.cpp",
    "octoprint_arc_welder/data/lib/c/py_arc_welder/python_helpers.cpp",
]

cpp_gcode_parser = Extension(
    "PyArcWelder",
    sources=plugin_ext_sources,
    language="c++",
    include_dirs=[
        "octoprint_arc_welder/data/lib/c/arc_welder",
        "octoprint_arc_welder/data/lib/c/gcode_processor_lib",
        "octoprint_arc_welder/data/lib/c/py_arc_welder",
    ],
    extra_compile_args=["-O3", "-std=c++11"],
    extra_link_args=[],
)

# Advanced build options (e.g., building with CMake)
additional_setup_parameters = {
    "ext_modules": [cpp_gcode_parser],
    "cmdclass": {"build_ext": build_ext},
}

try:
    import octoprint_setuptools
except:
    print("Could not import OctoPrint's setuptools, are you sure you are running that under the same python installation that OctoPrint is installed under?")
    import sys
    sys.exit(-1)

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
    identifier=plugin_identifier,
    package=plugin_package,
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    mail=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    requires=plugin_requires,
    additional_packages=plugin_additional_packages,
    ignored_packages=[],
    additional_data=plugin_additional_data,
    cmdclass=plugin_cmdclass,
)

if len(additional_setup_parameters):
    from octoprint.util import dict_merge
    setup_parameters = dict_merge(setup_parameters, additional_setup_parameters)

setup(**setup_parameters)
