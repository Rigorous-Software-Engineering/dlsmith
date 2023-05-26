
from this import d
from dlsmith.datalog.base_rule import BaseRule
from dlsmith.engines.Flix.flix_subgoal import FlixSubGoal

class FlixRule(BaseRule):

    def generate_head(self):
        self.head = FlixSubGoal()
        self.head.set_name(self.rule_node.get_name())
        head_variables = self.rule_node.get_levelled_variable_objects(self.level).get_vars()
        self.head.set_variables(head_variables)


    def generate_body_subgoals(self):
        edges = [edge for edge in self.rule_node.get_all_incoming_rule_edges() if edge.get_level() == self.level]
        for edge in edges:
            flix_subgoal = FlixSubGoal()
            flix_subgoal.set_name(edge.get_start_node().get_name())
            flix_subgoal.set_variables(edge.get_join_variables())
            if edge.get_charge() == "-ve": flix_subgoal.negate_subgoal()
            self.subgoals.append(flix_subgoal)

    def generate_rule_string(self):
        # ***********************************************************************************************
        # Singular occurance of a variable is considered an error in Flix.
        # ***********************************************************************************************
        var_names = list()
        for var in [i.get_name() for i in self.head.get_variables()]:
            var_names.append(var)
        for sub_goal in  self.subgoals:
            for var in [i.get_name() for i in sub_goal.get_variables()]:
                var_names.append(var)
        for subgoal in self.subgoals:
            for var in subgoal.get_variables(): 
                if var_names.count(var.get_name()) <= 1:
                    var.set_name("_")   
        # ***********************************************************************************************


        self.rule_string += self.head.get_string() + " :- " 
        for subgoal in self.subgoals: 
            self.rule_string += subgoal.get_string() + ", "
        self.rule_string = self.rule_string[:-2] + "."