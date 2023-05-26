from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.variableGenerator import VariableGenerator
from dlsmith.dataDependencyGraph.factNode import FactNode
from copy import deepcopy
from termcolor import colored


class LeveledVariables(object):
    """
        A small data structure that stores the level information and the variables
        (head variables)
    """
    def __init__(self, level, vars):
        self.level = level
        self.vars = vars
        self.probability = None

    def get_vars(self):
        return self.vars
    def get_level(self):
        return self.level
    def update_level(self, level):
        self.level=level
    def set_probability(self, prob):
        self.probability = prob
    def get_probability(self):
        return self.probability


"""
RuleNode: 

"""
class RuleNode(object):
    def __init__(self, name, depth, params, randomness, constantGenerator, isParsedNode=False):
        """


            NODE: name    - - - - - - - - - - -     stratum: NONE || Natural number
                                                   ancestry: NONE || +ve || -ve || UNKNOWN
        
        """

        self.name = name
        self.depth = depth
        self.params = params
        self.randomness = randomness
        self.constantGenerator = constantGenerator
        self.isParsedNode = isParsedNode
        self.incoming_rule_edges = list()
        self.outgoing_rule_edges = list()
        self.variables = list()
        self.fact_nodes = list()
        self.levelled_variable_objects = list()
        self.transformed = False
        self.generate_output = False
        self.stratum = "NONE"
        self.ancestry = "NONE"
        self.join_sign = "+ve"
        self.factInlined = False
        self.data_structure = ""
        self.inlining = False
        self.R_appended = False
        self.is_output_node = False
        self.is_complex_ = False

    def set_as_output_node(self):
        self.is_output_node = True
    def get_is_output_node(self):
        return self.is_output_node
    def is_parsed_node(self):
        return self.isParsedNode
    def get_stratum(self): 
        return self.stratum
    def get_ancestry(self):
        return self.ancestry
    def set_stratum(self, value):
        self.stratum = value
    def set_ancestry(self, sign):
        self.ancestry = sign
        assert sign == "+ve" or sign == "-ve" or sign == "UNKNOWN"
    def add_incoming_rule_edge(self, edge):
        self.incoming_rule_edges.append(edge)
    def get_all_incoming_rule_edges(self):
        return self.incoming_rule_edges
    def add_outgoing_rule_edge(self, edge):
        self.outgoing_rule_edges.append(edge)
    def get_all_outgoing_rule_edges(self):
        return self.outgoing_rule_edges
    def get_depth(self):
        return self.depth
    def over_write_variables(self, variables):
        self.variables = variables
    def get_variables(self):
        return self.variables
    def get_fact_nodes(self):
        return self.fact_nodes
    def append_fact_node(self, fact_node):
        self.fact_nodes.append(fact_node)
    def set_tranformed_flag_to_true(self):
        self.transformed = True
    def get_transformed_flag(self):
        return self.transformed
    def set_generate_output_to_true(self):
        self.generate_output = True
    def get_generate_output_flag(self):
        return self.generate_output
    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_R_appended(self):
        return self.R_appended
    def set_R_appended(self):
        self.R_appended = True
    def get_max_edge_level(self):
        if len(self.incoming_rule_edges) == 0: return 1
        return max([edge.get_level() for edge in self.incoming_rule_edges])
    def get_direct_parents(self):
        unique_direct_parents = list()
        for node in [edge.get_start_node() for edge in self.incoming_rule_edges]:
            if node not in unique_direct_parents:
                unique_direct_parents.append(node)
        return unique_direct_parents
    def get_direct_children(self):
        unique_direct_children = list()
        for node in [edge.get_end_node() for edge in self.outgoing_rule_edges]:
            if node not in unique_direct_children:
                unique_direct_children.append(node)
        return unique_direct_children
    def get_all_levelled_variable_objects(self):
        return self.levelled_variable_objects
    def get_levelled_variable_objects(self, level):
        return [i for i in self.levelled_variable_objects if i.get_level() == level][0]    
    def set_levelled_variable_objects(self, level_variable_object):
        self.levelled_variable_objects.append(level_variable_object)
    def get_incoming_edges_at_a_level(self, level):
        return len([i for i in self.incoming_rule_edges if i.get_level() == level])
    
    def get_all_join_variables_at_a_level(self, level):
        all_vars = list()
        for edge in [i for i in self.incoming_rule_edges if i.get_level() == level]:
            for var in edge.get_join_variables(): 
                all_vars.append(var)
        return all_vars

    def remove_levelled_variable_object_for_level(self, level):
        for i, var_obj in enumerate(self.levelled_variable_objects):
            if var_obj.get_level() == level:
                self.levelled_variable_objects.pop(i)
    def set_data_structure(self, ds):
        self.data_structure = ds
    def get_data_structure(self):
        return self.data_structure
    def set_inline_2_true(self):
        self.inlining = True
    def set_inline_2_false(self):
        self.inlining = False
    def get_inline_flag(self):
        return self.inlining
    def set_factInlined_to_True(self):
        self.factInlined = True
    def set_factInlined_to_False(self):
        self.factInlined = False
    def return_factInlined_status(self):
        return self.factInlined
    def set_is_complex_to_true(self):
        self.is_complex_ = True
    def is_complex(self):
        return self.is_complex_

    """
        Generate node variables depending on the types that are flowing into the node
        This is quite cool actually!
    """
    def generate_node_variables(self):
        all_parent_nodes = [edge.get_start_node() for edge in self.incoming_rule_edges]
        self.variableGenerator = VariableGenerator()
        if len(all_parent_nodes) == 0:
            for var in range(self.randomness.get_random_integer(1, self.params["max_number_of_variables"])):
                new_variable = Variable(name=self.variableGenerator.generate_new_lower_case_variabe(), 
                                    vtype=self.randomness.random_choice(self.params["general_types"]), 
                                    value=None)
                self.variables.append(new_variable)
            return 0

        type_choices = list()
        for parent_node in all_parent_nodes:
            if len(parent_node.get_variables()) == 0 and not parent_node.is_parsed_node():
                parent_node.generate_node_variables()
            type_choices += [var.get_type() for var in parent_node.get_variables()]
        
        if len(type_choices) == 0: 
            # No variables are flowing into the node.
            return 0

        for var in range(self.randomness.get_random_integer(1, self.params["max_number_of_variables"])):
            new_variable = Variable(name=self.variableGenerator.generate_new_lower_case_variabe(), 
                                    vtype=self.randomness.random_choice(type_choices), 
                                    value=None)
            self.variables.append(new_variable)



    def generate_fact_nodes(self):
        # Generate new nodes here depending on the variables in the rule node itself. 
        for i in range(self.randomness.get_random_integer(self.params["min_number_of_fact_nodes"], self.params["max_number_of_fact_nodes"])):
            # Generate a factNode here.             
            fact_node = FactNode(constantGenerator=self.constantGenerator, variables=deepcopy(self.variables), name=self.name)
            # Set probability for the fact (only Scallop uses this)
            if self.randomness.flip_a_coin():
                probability = self.randomness.get_small_random_float(0, 0)
                fact_node.set_probability(probability)
            self.fact_nodes.append(fact_node)

    def generate_a_singular_fact_node(self):
        fact_node = FactNode(constantGenerator=self.constantGenerator, variables=deepcopy(self.variables), name=self.name)
        # Set probability for the fact (only Scallop uses this)
        if self.randomness.flip_a_coin():
                probability = self.randomness.get_small_random_float(0, 0)
                fact_node.set_probability(probability)
        self.fact_nodes.append(fact_node)
        return fact_node



    def generate_joins(self):
        """
            TODO: Simplify this...
        """
        
        if len(self.incoming_rule_edges) == 0: return 0
        # Generate join information for each level 
        for level in range(1, self.get_max_edge_level()+1): 
            # Get all variable types flowing in 
            var_types_flowing_in = list()
            for parent_node in [edge.get_start_node() for edge in self.incoming_rule_edges if edge.get_level() == level]:
                var_types_flowing_in += [var.get_type() for var in parent_node.get_variables()]
            # For each variable type, generate a fresh variable
            temp_var_generator = VariableGenerator()
            fresh_variables = list()
            for var_type in var_types_flowing_in:
                fresh_variables.append(Variable(name=temp_var_generator.generate_new_lower_case_variabe(), vtype=var_type, value=None))
            for edge in [edge for edge in self.incoming_rule_edges if edge.get_level() == level]: 
                parent_node = edge.get_start_node()
                body_node = RuleNode(name=parent_node.get_name(), depth=parent_node.get_depth(), params=self.params, 
                                randomness=self.randomness, constantGenerator=None)
                body_node.over_write_variables(parent_node.get_variables())
                variables = body_node.get_variables()
                fresh_body_variables = list()
                for var in variables:
                    variable_choices = [var_choice for var_choice in fresh_variables if var_choice.get_type() == var.get_type()]
                    chosen_variable = deepcopy(self.randomness.random_choice(variable_choices))
                    fresh_body_variables.append(chosen_variable)
                body_node.over_write_variables(fresh_body_variables)
                edge.set_join_variables(fresh_body_variables) # Add the variable information in the edge as well
        # Ground the variables in the head
        # Generate LeveledVariables object with correct variables
        for level in range(1, self.get_max_edge_level() + 1):
            edges_at_this_level = [edge for edge in self.incoming_rule_edges if edge.get_level() == level and edge.get_charge() == "+ve"]
            positive_variables = list()
            for edge in edges_at_this_level: positive_variables += edge.get_join_variables()
            fresh_variables = deepcopy(self.variables)
            for var in fresh_variables:
                new_var_name = self.randomness.random_choice([pos_var.get_name() for pos_var in positive_variables if pos_var.get_type() == var.get_type()])
                var.set_name(new_var_name)
            levelled_variable_object = LeveledVariables(level=level, vars=fresh_variables)
            # Assign a probability to this rule (Only used by Scallop)
            if self.randomness.flip_a_coin(): levelled_variable_object.set_probability(self.randomness.get_small_random_float(0,0))
            self.levelled_variable_objects.append(levelled_variable_object)




    def remove_a_fact_node(self):
        """
            If the node has some fact nodes then remove the first one. 
        """
        if len(self.fact_nodes) == 0: return 1
        self.fact_nodes = self.fact_nodes[1:]