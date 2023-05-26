from termcolor import colored

class Edge(object):
    def __init__(self, start, end, charge, level):
        self.start_node = start
        self.end_node = end
        self.charge = charge
        self.transformed = False
        self.level = level
        self.operator = None
        self.join_variables = list()
        assert charge == "+ve" or charge == "-ve"


    def get_start_node(self):
        return self.start_node
    def get_join_variables(self):
        return self.join_variables
    def set_join_variables(self, variables): 
        self.join_variables = variables
    def get_end_node(self):
        return self.end_node
    def get_charge(self):
        return self.charge
    def get_level(self):
        return self.level
    def set_charge(self, charge):
        self.charge = charge
    def set_level(self, level):
        self.level = level
    def set_operator(self, op):
        self.operator = op
    def get_operator(self):
        return self.operator

    def set_tranformed_flag_to_true(self):
        self.transformed = True
    def get_transformed_flag(self):
        return self.transformed


    def check_edge_removal_safety(self):
        """
            Check if it is safe to remove this edge or not.
            It is not safe if removing this edge will unground a variable in the END_NODE head or in the negative subgoals in the body of the END_NODE.
        """
        if self.charge == "-ve": return True
        
        other_positive_edges = [edge for edge in self.end_node.get_all_incoming_rule_edges() if edge.get_level() == self.level and edge.get_charge() == "+ve" and edge != self]
        other_positive_variables = list()
        for edge in other_positive_edges:
            other_positive_variables += edge.get_join_variables()
        other_positive_variables = [var.get_name() for var in other_positive_variables] + [var.get_name() for var in self.join_variables]
        for var_name in [var.get_name() for var in self.join_variables]:
            for i, var2 in enumerate(other_positive_variables):
                if var_name == var2:
                    other_positive_variables.pop(i)
                    break

        # Check if head is grounded at this level
        for var in [i.get_name() for i in self.end_node.get_levelled_variable_objects(self.level).get_vars()]:
            if var not in other_positive_variables: 
                return False

        # Check if variables in negative subgoals is grounded.
        all_negative_edges = [edge for edge in self.end_node.get_all_incoming_rule_edges() if edge.get_level() == self.level and edge.get_charge() == "-ve"]
        all_negative_variables = list()
        for edge in all_negative_edges:
            all_negative_variables += edge.get_join_variables()
        all_negative_variables = [var.get_name() for var in all_negative_variables]
        for var in all_negative_variables: 
            if var not in other_positive_variables:
                return False
        return True



    def check_if_safe_to_assign_neg_sign(self):
        other_positive_edges = [edge for edge in self.end_node.get_all_incoming_rule_edges() if edge.get_level() == self.level and edge.get_charge() == "+ve" and edge != self]
        other_positive_variables = list()
        for edge in other_positive_edges:
            other_positive_variables += edge.get_join_variables()
        other_positive_variables = [var.get_name() for var in other_positive_variables]
        for var in self.join_variables:
            if var.get_name() not in other_positive_variables: 
                return False
        return True 