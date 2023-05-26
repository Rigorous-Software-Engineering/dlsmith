
from abc import ABC, abstractmethod

class BaseProgram(object):
    def __init__(self, dependencyGraph, params, randomness, logging, parsedProgramText):
        self.randomness = randomness
        self.dependencyGraph = dependencyGraph
        self.params = params
        self.logging = logging
        self.parsed_program_text = parsedProgramText
        self.declarations = list()
        self.facts = list()
        self.all_rules = list()        
        self.output_rule_name = ""
        self.program_string = ""
        self.program_path = None
        self.program_file_path = None
        self.generate_rules()
        self.generate_declarations()
        self.output_result_path = None
        self.program_file_name = None


    def get_program_string(self):
        return self.program_string

    def get_data_dependency_graph(self):
        return self.dependencyGraph


    @abstractmethod
    def generate_program_string(self):
        pass

    @abstractmethod
    def export_program_string(self, program_number, core_path):
        pass

    @abstractmethod
    def generate_facts(self):
        pass

    @abstractmethod
    def generate_rules(self):
        pass

    @abstractmethod
    def generate_facts(self):
        pass
    
    @abstractmethod
    def generate_declarations(self):
        pass
    
    def set_program_file_name(self, file_name):
        self.program_file_name = file_name
    
    def get_program_file_name(self): 
        return self.program_file_name

    def get_program_string(self):
        return self.program_string

    def get_program_path(self):
        return self.program_path

    def get_program_file_path(self):
        return self.program_file_path

    def get_output_rule_name(self):
        return self.output_rule_name

    def set_output_result_path(self, new_path):
        self.output_result_path = new_path
    def get_output_result_path(self):
        return self.output_result_path
