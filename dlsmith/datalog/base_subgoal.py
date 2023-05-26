from abc import ABC, abstractmethod


class BaseSubGoal(object):
    def __init__(self):
        self.name = None
        self.variables = list()     # A list of type Variable
        self.string = ""
        self.negated_subgoal = False
        self.operator = None

    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name

    def get_string(self):
        self.update_string()
        return self.string

    def get_variables(self):
        return self.variables

    def update_var_at_location_i(self, i, var):
        self.variables[i] = var

    def negate_subgoal(self):
        self.negated_subgoal = True

    def set_operator(self, op):
        self.operator = op

    def get_operator(self):
        return self.operator

    @abstractmethod
    def update_string(self):
        pass

    @abstractmethod
    def set_variables(self):
        pass
    
    @abstractmethod
    def get_string_with_variable_types(self):
        pass
    
    
    