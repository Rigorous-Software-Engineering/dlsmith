from dlsmith.datalog.base_rule import BaseRule
from dlsmith.engines.Ascent.ascent_subgoal import AscentSubGoal


class AscentRule(BaseRule):

    def generate_head(self):
        self.head = AscentSubGoal()
        self.head.set_name(self.rule_node.get_name())
        head_variables = self.rule_node.get_levelled_variable_objects(self.level).get_vars()
        self.head.set_variables(head_variables)

    def generate_body_subgoals(self):
        edges = [edge for edge in self.rule_node.get_all_incoming_rule_edges() if edge.get_level() == self.level]
        negated_subgoals = list()
        for edge in edges:
            ascent_subgoal = AscentSubGoal()
            ascent_subgoal.set_name(edge.get_start_node().get_name())
            ascent_subgoal.set_variables(edge.get_join_variables())
            if edge.get_charge() == "-ve": 
                ascent_subgoal.negate_subgoal()
                negated_subgoals.append(ascent_subgoal)
                # All negated subgoals are pushed at the end. Ascent kay nakhray
                continue
            self.subgoals.append(ascent_subgoal)
        self.subgoals += negated_subgoals


    def generate_rule_string(self):
        self.rule_string += self.head.get_string() + " <-- "
        for subgoal in self.subgoals:
            self.rule_string += subgoal.get_string() + ", "
        self.rule_string = self.rule_string[:-2] + ";"
