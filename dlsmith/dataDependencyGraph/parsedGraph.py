import os
import copy

from termcolor import colored

from dlsmith.dataDependencyGraph.ruleNode import RuleNode
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.file_operations import pick_seed_program
from dlsmith.utils.variableGenerator import VariableGenerator

"""
    This will generate some parsed text, and some 
"""

class ParsedGraph(object):
    def __init__(self, randomness, engine, path_to_home, logger, params, debug):
        self.randomness = randomness
        self.engine = engine
        self.logger = logger
        self.params = params
        self.debug = debug
        
        # This is the only thing we need from this data structure
        self.parsed_text = ""
        self.parsed_nodes = list()
        self.type_declerations = list()

        if self.engine == "souffle": 
            self.path_to_seeds_dir = os.path.join(path_to_home, "seeds", self.params["souffle_seeds_dir"])
        if self.engine == "ddlog" : 
            self.path_to_seeds_dir = os.path.join(path_to_home, "seeds", self.params["ddlog_seeds_dir"])
        if self.engine == "formulog":
            self.path_to_seeds_dir = os.path.join(path_to_home, "seeds", self.params["formulog_seeds_dir"])
        if self.engine == "flix":
            self.path_to_seeds_dir = os.path.join(path_to_home, "seeds", self.params["flix_seeds_dir"])
        if self.engine == "ascent":
            self.path_to_seeds_dir = os.path.join(path_to_home, "seeds", self.params["ascent_seeds_dir"])
        if self.engine == "scallop" or self.engine == "scallop_compiler":
            self.path_to_seeds_dir = os.path.join(path_to_home, "seeds", self.params["scallop_seeds_dir"])
        
        if self.engine == "souffle" or self.engine == "ddlog" or self.engine == "formulog" or self.engine == "scallop":
            self.seed_dir_path, self.seed_file_path = pick_seed_program(self.randomness, self.path_to_seeds_dir)
        else:
            self.seed_dir_path, self.seed_file_path = None, None

        if self.seed_dir_path is None: 
            print(colored("No seed file found", "yellow", attrs=["bold"]))
            return None
        
        self.logger.add_log_text("[ParsedGraph] Path to seed file: " + self.seed_file_path)
        if debug: print(colored("Seed file: ", "magenta", attrs=["bold"]) + self.seed_file_path)
        if self.engine == "souffle": 
            self.parse_souffle_program()
        if self.engine == "ddlog": 
            self.parse_ddlog_program()
        if self.engine == "formulog": 
            self.parse_formulog_program()
        if self.engine == "scallop" or self.engine == "scallop_compiler":
            self.parse_scallop_program()
        self.logger.add_log_text("[ParsedGraph] Parsed " + str(len(self.parsed_nodes)) + " nodes from the seed file")


    def get_type_declerations(self):
        return self.type_declerations
    def get_parsed_nodes(self):
        return self.parsed_nodes
    def get_parsed_node_names(self):
        return [node.get_name() for node in self.parsed_nodes]
    def get_parsed_program_text(self):
        return self.parsed_text
    def get_seed_folder_path(self):
        return self.seed_dir_path
    def get_seed_file_path(self):
        return self.seed_file_path

    def parse_scallop_program(self):
        """
            Read types
            using 
            // TypeInformation: RelationName(string, integer)
        """
        self.logger.add_log_text("[ParsedGraph] Parsing seed file")
        with open(self.seed_file_path, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                # Get type information for each variable. 
                if line.find("type") != -1:
                    if line.find("<:") != -1: 
                        """   
                            type Name <: String
                            type Attr <: String
                            type Rela <: String
                            type ObjectId <: usize
                        """
                        # We don't want consider these cases
                        self.parsed_text += line + "\n"
                        continue
                    temp_string = copy.deepcopy(line)
                    temp_string = temp_string.replace("type ", "")
                    parsed_node_name = temp_string[0:temp_string.find("(")]
                    node = RuleNode(parsed_node_name, 0, None, None, None, True)
                    variables_with_types = line[line.find("(") + 1 : line.find(")")].replace(" ", "").split(",")
                    if variables_with_types[0] == "":
                        pass
                    else:
                        node_variables = list()
                        var_gen = VariableGenerator()
                        for var in variables_with_types:
                            var_name = var_gen.generate_new_lower_case_variabe()
                            var_type = var
                            var = Variable(var_name, var_type, None)
                            node_variables.append(var)
                        node.over_write_variables(node_variables)
                    self.parsed_nodes.append(node)
                    self.parsed_text += line + "\n"
                    continue

                if line[0:2] == "//" or line == "":
                    continue

                if line.find("query") != -1: 
                    continue

                self.parsed_text += line + "\n"


    def parse_ddlog_program(self):
        def get_variables_with_types(all_vars_and_types):
            """
                input relation DDValTest2(a: Map<usize, string>, b: (bool, Set<u128>))
                -> ["a: Map<usize, string>", "b: (bool, Set<u128>)"]
            """
            all_vars_and_types = all_vars_and_types.replace(" ", "")
            variables_with_types = list()
            while True:
                if all_vars_and_types.find(":") == -1: break
                location_of_first_colon = all_vars_and_types.find(":")
                var_name = all_vars_and_types[0:location_of_first_colon]
                var_type = ""
                if all_vars_and_types[location_of_first_colon + 1:].find(":") == -1:
                    # No more colons left
                    var_type = all_vars_and_types[location_of_first_colon + 1:]
                    variables_with_types.append(var_name + ":" + var_type)
                    break
                else:
                    location_of_next_colon = all_vars_and_types[location_of_first_colon + 1:].find(":")
                    location_of_last_comma = all_vars_and_types[0: location_of_next_colon+ location_of_first_colon].rfind(",")
                    var_type = all_vars_and_types[location_of_first_colon + 1: location_of_last_comma]
                    all_vars_and_types = all_vars_and_types[location_of_last_comma + 1:]
                    variables_with_types.append(var_name + ":" + var_type)
            return variables_with_types

        if self.debug: print(colored("Parsing the seed file", "blue", attrs=["bold"]))
        self.logger.add_log_text("[ParsedGraph] Parsing seed file")
        with open(self.seed_file_path, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:                
                if line.find("::") != -1: 
                    # Ignore this for now
                    self.parsed_text += line + "\n"
                    continue

                #  Declarations?
                if line[0:14] == "input relation" or line[0:15] == "output relation" or line[0:8] == "relation":
                    temp_string = copy.deepcopy(line)
                    if line[0:14] == "input relation": temp_string = temp_string.replace("input relation ", "")
                    if line[0:15] == "output relation": temp_string = temp_string.replace("output relation ", "")
                    if line[0:8] == "relation": temp_string = temp_string.replace("relation ", "")
                    parsed_node_name = temp_string[0:temp_string.find("(")]
                    parsed_node_name = parsed_node_name.replace(" " , "")
                    node = RuleNode(parsed_node_name, 0, None, None, None, True)
                    if line[0:14] == "input relation": self.parsed_text += "input relation " + parsed_node_name + "("
                    if line[0:15] == "output relation": self.parsed_text += "relation " + parsed_node_name + "("
                    if line[0:8] == "relation": self.parsed_text += "relation " + parsed_node_name + "("
                    variables_with_types = get_variables_with_types(line[line.find("(") + 1 : -1])
                    if len(variables_with_types) == 0:
                        # arity 0
                        self.parsed_text += ")\n"
                    else:
                        # arity greater than 0
                        node_variables = list()
                        for var in variables_with_types:
                            var_name = var[:var.find(":")]
                            var_type = var[var.find(":") + 1:]
                            var = Variable(var_name, var_type, None)
                            self.parsed_text += var_name + ":" + var_type + ","
                            node_variables.append(var)
                        self.parsed_text = self.parsed_text[:-1] + ")\n"
                        node.over_write_variables(node_variables)
                    self.parsed_nodes.append(node)
                    continue
                self.parsed_text += line + "\n"


    def parse_formulog_program(self):
        def get_variables_with_types(all_vars_and_types):
            if all_vars_and_types.find("(") == -1: return list()
            remove_init_brackets = all_vars_and_types[all_vars_and_types.find("(") + 1 : all_vars_and_types.rfind(")")]
            if remove_init_brackets.find("(") != -1: return None # We do not want to include funny things like input q((i32, string) union).
            return remove_init_brackets.split(",")

        self.logger.add_log_text("[ParsedGraph] Parsing seed file")
        var_generator = VariableGenerator()
        with open(self.seed_file_path, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                
                # Declaration?            
                if line[0:6] == "input " or line[0:7] == "output ":
                    temp_string = copy.deepcopy(line)
                    if line[0:6] == "input ": temp_string = temp_string.replace("input ", "")
                    if line[0:7] == "output ": temp_string = temp_string.replace("output ", "")
                    parsed_node_name = ""
                    if temp_string.find("(") == -1: 
                        parsed_node_name = temp_string[0:]
                        parsed_node_name = parsed_node_name.replace(".", "")
                    else:
                        parsed_node_name = temp_string[0:temp_string.find("(")]
                        parsed_node_name = parsed_node_name.replace(" " , "")
                    node = RuleNode(parsed_node_name, 0, None, None, None, True)
                    variables_with_types = get_variables_with_types(line)
                    if variables_with_types is None: 
                        self.parsed_text += line + "\n"
                        continue
                    elif len(variables_with_types) == 0:
                        # arity 0
                        pass
                    else:
                        # arity greater than 0
                        node_variables = list()
                        for var_type in variables_with_types:
                            var_name = var_generator.generate_new_lower_case_variabe()
                            var = Variable(var_name, var_type, None)
                            node_variables.append(var)
                        node.over_write_variables(node_variables)
                    self.parsed_nodes.append(node)
                    self.parsed_text += line + "\n"
                    continue
                
                # Empty line
                if line == "":
                    continue

                self.parsed_text += line + "\n"


    def parse_souffle_program(self):
        self.logger.add_log_text("[ParsedGraph] Parsing seed file")
        with open(self.seed_file_path, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                # Type definition?
                if line.find(".type") != -1:
                    self.parsed_text += line + "\n"
                    self.type_declerations.append(line)
                    continue

                # Declaration?
                # Inner declarations are ignored (in a component for example)
                if line[0:5] == ".decl" != -1:
                    temp_string = copy.deepcopy(line)
                    temp_string = temp_string.replace(".decl ", "")
                    parsed_node_name = temp_string[0:temp_string.find("(")]
                    parsed_node_name = parsed_node_name.replace(" " , "")
                    node = RuleNode(parsed_node_name, 0, None, None, None, True)
                    #self.parsed_text += ".decl " + parsed_node_name + "("
                    variables_with_types = line[line.find("(") + 1 : line.find(")")].replace(" ", "").split(",")
                    if variables_with_types[0] == "":
                        # arity 0
                        #self.parsed_text += ")\n"
                        pass
                    else:
                        # arity greater than 0
                        node_variables = list()
                        for var in variables_with_types:
                            var_name = var[:var.find(":")]
                            var_type = var[var.find(":") + 1:]
                            var = Variable(var_name, var_type, None)
                            #self.parsed_text += var_name + ":" + var_type + ","
                            node_variables.append(var)
                        #self.parsed_text = self.parsed_text[:-1] + ")\n"
                        node.over_write_variables(node_variables)
                    self.parsed_text += line + "\n"
                    self.parsed_nodes.append(node)
                    continue

                # Input?
                if line.find(".input") != -1:
                    self.parsed_text += line + "\n"
                    continue

                # Comment or empty line or output?
                if line[0:2] == "//" or line == "" or line.find(".output") != -1:
                    continue
                    
                # Rule defintion
                if line.find(":-") != -1:
                    self.parsed_text += line + "\n"
                    continue

                # Otherwise it is probably a fact
                self.parsed_text += line + "\n"