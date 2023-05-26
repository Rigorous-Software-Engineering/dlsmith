import string


class VariableGenerator(object):
    def __init__(self):
        self.call_number = -1

    def generate_new_upper_case_variabe(self, letters_to_exclude=list()):
        while(True):
            self.call_number += 1
            cycle = int(self.call_number / len(string.ascii_uppercase))
            letter = string.ascii_uppercase[self.call_number % len(string.ascii_uppercase)]
            for i in range(cycle):
                letter += letter
            if letter in letters_to_exclude:
                continue
            return letter

    def generate_new_lower_case_variabe(self, letters_to_exclude=list()):
        while(True):
            self.call_number += 1
            cycle = int(self.call_number / len(string.ascii_lowercase))
            letter = string.ascii_lowercase[self.call_number % len(string.ascii_lowercase)]
            for i in range(cycle):
                letter += letter
            if letter in letters_to_exclude:
                continue
            return letter



def generate_var_not_in_list(var_names):
    call_number = 0
    while(True):
        cycle = int(call_number / len(string.ascii_lowercase))
        letter = string.ascii_lowercase[call_number % len(string.ascii_lowercase)]
        for i in range(cycle): letter += letter
        if letter not in var_names: return letter
        call_number += 1