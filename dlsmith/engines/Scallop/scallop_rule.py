
from dlsmith.datalog.base_rule import BaseRule
from dlsmith.engines.Scallop.scallop_subgoal import ScallopSubGoal


class ScallopRule(BaseRule):

    def generate_head(self):
        self.head = ScallopSubGoal()
        self.head.set_name(self.rule_node.get_name())
        head_variables = self.rule_node.get_levelled_variable_objects(self.level).get_vars()
        self.set_probability(self.rule_node.get_levelled_variable_objects(self.level).get_probability())
        self.head.set_variables(head_variables)

    def generate_body_subgoals(self):
        edges = [edge for edge in self.rule_node.get_all_incoming_rule_edges() if edge.get_level() == self.level]
        negated_subgoals = list()
        for edge in edges:
            scallop_subgoal = ScallopSubGoal()
            scallop_subgoal.set_name(edge.get_start_node().get_name())
            scallop_subgoal.set_variables(edge.get_join_variables())
            # Set the operator for the subgoal
            scallop_subgoal.set_operator(edge.get_operator())
            if edge.get_charge() == "-ve": 
                scallop_subgoal.negate_subgoal()
                negated_subgoals.append(scallop_subgoal)
                # All negated subgoals are pushed at the end.
                continue
            self.subgoals.append(scallop_subgoal)
        self.subgoals += negated_subgoals

    def generate_rule_string(self):
        if self.get_probability() is not None: 
            self.rule_string += "rel " + self.get_probability() + "::" + self.head.get_string() + " = "
        else: 
            self.rule_string += "rel " + self.head.get_string() + " = "

        for subgoal in self.subgoals:
            self.rule_string += subgoal.get_string() + ", "
        self.rule_string = self.rule_string[:-2]


    def generate_complex_rule_string(self):
        if self.get_probability() is not None: 
            self.rule_string += "rel " + self.get_probability() + "::" + self.head.get_string() + " = "
        else: 
            self.rule_string += "rel " + self.head.get_string() + " = "

        for i, subgoal in enumerate(self.subgoals):
            if subgoal.get_operator() is None: subgoal.set_operator("and")
            if i == 0:
                self.rule_string += subgoal.get_string() 
            elif i == 1 and len(self.subgoals) > 2:
                self.rule_string += " " + subgoal.get_operator() + " (" + subgoal.get_string()
            else:
                self.rule_string += " " + subgoal.get_operator() + " " + subgoal.get_string()

        if len(self.subgoals) > 2:
            self.rule_string += ")"