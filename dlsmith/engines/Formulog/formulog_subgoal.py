

from dlsmith.datalog.base_subgoal import BaseSubGoal


class FormulogSubGoal(BaseSubGoal):
    
    def update_string(self):
        self.string = ""
        if self.negated_subgoal: self.string += "!"
        
        if len(self.variables) == 0: 
            self.string += self.name
        else:
            self.string += self.name + "("
            for variable in self.variables:
                self.string += variable.get_name() + ", "
            self.string = self.string[:-2] + ")"


    def set_variables(self, variables):
        self.variables = variables
        