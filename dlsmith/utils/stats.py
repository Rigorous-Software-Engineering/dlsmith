
import json 
import os
from termcolor import colored

class Stats(object):
    def __init__(self, core_dir_path):
        """

            {
                "server" : "pinky22",
                "core_id" : 1,
                "program_number" : 10,
                
                // Transformations go from here on.... 
                "EQU_NODE_ADD" : 2, 
                "" :  
            }

        """
        self.path_to_transformation_stats = os.path.join(core_dir_path, "transformation_stats.json")
        self.EQUIVALENT = ["EQU_NODE_ADD", "EQU_NODE_REM", "EQU_EDGE_ADD", "EQU_EDGE_REM", "EQU_LEVEL_ADD", "EQU_LEVEL_ADD_2", "EQU_COLLAPSE_EDGE", "EQU_FACT_INLINE", "ADD_EQU", "MOD_EQU", "REM_EQU"]
        self.EXPAND = ["ADD_EQU", "MOD_EQU", "REM_EQU", "EXP_EDGE_ADD", "EXP_EDGE_REM", "EXP_NODE_ADD", "EXP_NODE_REM", "MOD_EXP"]
        self.CONTRACT = ["CON_EDGE_ADD", "CON_EDGE_REM", "CON_NODE_ADD", "CON_NODE_REM", "CON_ADD_SELF_EDGE", "MOD_CON"]
        self.json_dict = dict()

        # Create a stats.json file here?
        for transformation in self.EQUIVALENT + self.CONTRACT + self.EXPAND:
            self.json_dict[transformation] = 0

        
    def dump_transformation_stats_as_json(self):
        with open(self.path_to_transformation_stats, 'w') as f:
            json.dump(self.json_dict, f)

    def increment_transformation_count(self, transformation):
        self.json_dict[transformation] += 1

    def display_transformation_stats(self, path_to_temp_folder):
        print("TRANSFORMATION STATS:\n")
        
        # Import all stats json files

        # Get all the server folders
        servers = list()
        core_directories = list()
        for r,d,f in os.walk(path_to_temp_folder):
            for dd in d: servers.append(dd)
            break
        servers = [i for i in servers if i != "errors" and i != "soundness"]
        for server in servers:
            for r,d,f in os.walk(os.path.join(path_to_temp_folder, server)):
                for dd in d: core_directories.append(os.path.join(path_to_temp_folder, server, dd))
                break
    
        for core_dir in core_directories:
            with open(os.path.join(core_dir, "transformation_stats.json")) as f:
                data = json.load(f)
                # data should be a dict now
                for key in data.keys():
                    self.json_dict[key] += data[key]

        for key in self.json_dict:
            if self.json_dict[key] == 0: 
                print(key + " : " + colored(str(self.json_dict[key]), "red", attrs=["bold"]))
            else:
                print(key + " : " + colored(str(self.json_dict[key]), "green", attrs=["bold"]))