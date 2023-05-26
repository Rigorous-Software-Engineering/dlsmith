from copy import deepcopy
from dlsmith.datalog.base_rule import BaseRule
from dlsmith.engines.Souffle.souffle_subgoal import SouffleSubGoal
from dlsmith.dataDependencyGraph.variable import Variable

class SouffleRule(BaseRule):
    
    def generate_head(self):
        self.head = SouffleSubGoal()
        self.head.set_name(self.rule_node.get_name())
        head_variables = self.rule_node.get_levelled_variable_objects(self.level).get_vars()
        self.head.set_variables(head_variables)
        

    def generate_body_subgoals(self):
        """
            Get body nodes contained within each rule node 
        """
        edges = [edge for edge in self.rule_node.get_all_incoming_rule_edges() if edge.get_level() == self.level]

        for edge in edges:
            souffle_subgoal = SouffleSubGoal()
            souffle_subgoal.set_name(edge.get_start_node().get_name())
            souffle_subgoal.set_variables(edge.get_join_variables())
            if edge.get_charge() == "-ve": souffle_subgoal.negate_subgoal()
            self.subgoals.append(souffle_subgoal)


    def generate_rule_string(self):
        self.rule_string += self.head.get_string() + " :- " 
        for subgoal in self.subgoals: 
            self.rule_string += subgoal.get_string() + ", "
        self.rule_string = self.rule_string[:-2] + "."