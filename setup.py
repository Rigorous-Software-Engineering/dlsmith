

from setuptools import setup, find_packages
import json
import os

# Get path to home
HOME = os.path.dirname(os.path.realpath(__file__))

# Create param.json file at home directory location. Copy everything from default_params.json
default_parameters = os.path.join(HOME, "dlsmith", "default_params.json")
with open(default_parameters) as f:
    data = json.load(f)
    json_dump = json.dumps(data, indent=4)

# Create params.json at home
data["home"] = HOME
file=open(os.path.join(HOME, "params.json"),"w")
file.write("")
file.close()
with open(os.path.join(HOME, "params.json"), "w") as outfile:
	json.dump(data, outfile, indent=4)

# create get_home()
home_path_data = "def get_home():\n\treturn'" + HOME + "'\n"
file = open(os.path.join(HOME, "dlsmith", "home.py"), "w")
file.write(home_path_data)
file.close()

setup( 
	name='dlsmith',
	version='1.0.0',
	description='Framework to test Datalog engines',
	keywords='fuzzing, Dataflow graphs',
	install_requires=['termcolor', 'pyfiglet', 'nose2'],
	packages=find_packages(),
	entry_points={
        'console_scripts': ['dlsmith = dlsmith.__main__:main']
    }
)
