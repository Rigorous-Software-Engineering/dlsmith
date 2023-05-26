


class ConstantGenerator(object):
    def __init__(self, param, randomness):
        self.randomness = randomness
        self.integer_constants = [randomness.get_random_integer(1,100) for i in range(param["number_of_constants"])]
        self.string_constants = [randomness.get_lower_case_alpha_string(2) for i in range(param["number_of_constants"])]

    def get_integer_constants(self):
        return self.integer_constants

    def get_string_constants(self):
        return self.string_constants

    def get_variable_value(self, variable_type):
        if variable_type == "integer" or variable_type == "i32":
            return self.randomness.random_choice(self.integer_constants)

        if variable_type == "string" or variable_type == "String":
            return self.randomness.random_choice(self.string_constants)
