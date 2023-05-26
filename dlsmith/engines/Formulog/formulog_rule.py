from dlsmith.datalog.base_rule import BaseRule
from dlsmith.engines.Formulog.formulog_subgoal import FormulogSubGoal
from copy import deepcopy
class FormulogRule(BaseRule):

    def generate_head(self):
        self.head = FormulogSubGoal()
        self.head.set_name(self.rule_node.get_name())
        head_variables = self.rule_node.get_levelled_variable_objects(self.level).get_vars()
        self.head.set_variables(deepcopy(head_variables))

        for variable in self.head.get_variables(): 
            variable.set_name("Var_" + variable.get_name())


    def generate_body_subgoals(self):
        """
            Get body nodes contained within each rule node 
        """
        edges = [edge for edge in self.rule_node.get_all_incoming_rule_edges() if edge.get_level() == self.level]

        for edge in edges:
            ddlog_subgoal = FormulogSubGoal()
            ddlog_subgoal.set_name(edge.get_start_node().get_name())
            ddlog_subgoal.set_variables(deepcopy(edge.get_join_variables()))
            if edge.get_charge() == "-ve": ddlog_subgoal.negate_subgoal()
            self.subgoals.append(ddlog_subgoal)

            # Formulog kay nakhray
            for variable in ddlog_subgoal.get_variables(): 
                variable.set_name("Var_" + variable.get_name())



    def generate_rule_string(self):

        # ***********************************************************************************************
        # WARNING: Not a well understood change. 
        # To avoid "Variable usage errors", we will remove the variabels in a rule that occur only once.
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