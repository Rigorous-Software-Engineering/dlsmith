from dlsmith.datalog.base_subgoal import BaseSubGoal


class FlixSubGoal(BaseSubGoal):
   
    def update_string(self):
        self.string = ""
        if self.negated_subgoal: self.string += "not "
        self.string += self.name + "("
        for variable in self.variables:
            self.string += variable.get_name() + ", "
        
        if len(self.variables) == 0: 
            self.string += ")"
        else:
            self.string = self.string[:-2] + ")"
        
    def set_variables(self, variables):
        self.variables = variables
