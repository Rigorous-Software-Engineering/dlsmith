
class FactNode(object):
    """
        A FactNode is always associated with some base node. 
    """ 
    def __init__(self, constantGenerator, variables, name, inlined=False):
        self.name = name
        self.constantGenerator = constantGenerator
        self.variables = variables
        if not inlined: self.generate_variable_values()
        self.transformed = False
        self.probability = None

    def generate_variable_values(self):
        for var in self.variables:
            var.set_value(self.constantGenerator.get_variable_value(var.get_type()))
    def get_value_string(self):
        value_string = "".join(str(i) + "," for i in [j.get_value() for j in self.variables])
        return value_string[:-1]
    def get_name(self):
        return self.name
    def get_variables(self):
        return self.variables
    def set_tranformed_flag_to_true(self):
        self.transformed = True
    def get_transformed_flag(self):
        return self.transformed
    def set_probability(self, prob):
        self.probability = prob
    def get_probability(self):
        return self.probability
