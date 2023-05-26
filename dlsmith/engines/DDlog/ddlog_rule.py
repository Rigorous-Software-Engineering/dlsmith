from dlsmith.datalog.base_rule import BaseRule
from dlsmith.engines.DDlog.ddlog_subgoal import DDlogSubGoal

class DDlogRule(BaseRule):

    def generate_head(self):
        self.head = DDlogSubGoal()
        self.head.set_name(self.rule_node.get_name())
        head_variables = self.rule_node.get_levelled_variable_objects(self.level).get_vars()
        self.head.set_variables(head_variables)

    def generate_body_subgoals(self):
        """
            Get body nodes contained within each rule node 
        """
        edges = [edge for edge in self.rule_node.get_all_incoming_rule_edges() if edge.get_level() == self.level]

        for edge in edges:
            ddlog_subgoal = DDlogSubGoal()
            ddlog_subgoal.set_name(edge.get_start_node().get_name())
            ddlog_subgoal.set_variables(edge.get_join_variables())
            if edge.get_charge() == "-ve": ddlog_subgoal.negate_subgoal()
            self.subgoals.append(ddlog_subgoal)


    def generate_rule_string(self):
        self.rule_string += self.head.get_string() + " :- " 
        for subgoal in self.subgoals: 
            self.rule_string += subgoal.get_string() + ", "
        self.rule_string = self.rule_string[:-2] + "."