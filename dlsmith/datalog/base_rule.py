from abc import ABC, abstractmethod

from dlsmith.utils.variableGenerator import VariableGenerator

class BaseRule(object):
    def __init__(self, randomness, level, rule_node):
        self.randomness = randomness
        self.level = level
        self.rule_node = rule_node
        self.head = None
        self.subgoals = list()      # List of subgoal
        self.rule_string = ""
        self.variableGenerator = VariableGenerator()
        self.probability = None

    def get_head(self):
        return self.head
    def get_rule_string(self):
        return self.rule_string


    @abstractmethod
    def generate_rule_string(self):
        pass
    @abstractmethod
    def generate_head(self):
        pass

    @abstractmethod
    def generate_body_subgoals(self):
        """
            dependencies: A list of Nodes connected with an incoming edge
        """
        pass
    @abstractmethod
    def set_probability(self, prob):
        self.probability = prob
    @abstractmethod
    def get_probability(self):
        return self.probability
