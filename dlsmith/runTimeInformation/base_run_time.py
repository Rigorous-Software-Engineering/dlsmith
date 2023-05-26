from abc import ABC, abstractmethod

class node_data(object):
    def __init__(self, node, data):
        """
            One object of this contains one node data pair. self.data is a list in list
            a__  ->  ['"uy"', '"xk"']
            b__  ->  ['44', '57']
            c__  ->  ['"bl"']
            e__  ->  ['32']
            f__  ->  ['27']
            h__  ->  ['32', '"bl"']
            h__  ->  ['32', '"uu"']
        """
        self.node = node
        self.data = data    # Type: list
    def get_data(self):
        return self.data
    def get_node(self):
        return self.node


class RunTimeBase(object):
    def __init__(self, dependencyGraph, logger):
        self.dependencyGraph = dependencyGraph
        self.path_to_program = None
        self.logger = logger
        self.run_time_data = list() # List of node_data() objects
        self.run_time_information_available = False
        self.nodes_with_non_empty_output = list()

    def set_path_to_program(self, path):
        self.path_to_program = path
    def get_path_to_program(self):
        return self.path_to_program
    def is_run_time_information_available(self):
        return self.run_time_information_available
    def get_node_data(self, node):
        for i in self.run_time_data:
            if i.get_node() == node:
                return i.get_data()
        return []

    def compute_nodes_with_non_empty_output(self):
        for node in self.dependencyGraph.get_all_rule_nodes() + self.dependencyGraph.get_complex_nodes():
            if len(self.get_node_data(node)) != 0:
                self.nodes_with_non_empty_output.append(node)
        self.logger.add_log_text("[RunTimeBase] The dependency graph has " \
                + str(len(self.nodes_with_non_empty_output)) + " nodes with non-empty output result.")

    def get_nodes_with_non_empty_output(self):
        return self.nodes_with_non_empty_output


    @abstractmethod
    def generate_facts_from_output(self, node):
        """
            From the imported data, generate facts for the node for the given language
        """
        pass
    
    @abstractmethod
    def import_run_time_data(self):
        pass
