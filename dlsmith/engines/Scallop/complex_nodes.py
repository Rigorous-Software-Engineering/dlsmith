from random import random
from dlsmith.dataDependencyGraph.graphUtils import compute_node_charge_property_value
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.constantGenerator import ConstantGenerator
from dlsmith.dataDependencyGraph.ruleNode import LeveledVariables, RuleNode
from dlsmith.utils.variableGenerator import VariableGenerator
from dlsmith.dataDependencyGraph.edge import Edge
from termcolor import colored
from copy import deepcopy

def ScallopComplexNodes(dependencyGraph, logging, PARAMS, randomness, parsedGraph, DEBUG, fulllogs):
    """
        Start by creating a bunch of empty empty nodes.
        Empty nodes contain nothing but incoming fact nodes.
        Then create complex nodes. Complex nodes take edges from parsed nodes and fact nodes.
        Then normal rule nodes take edges from everything.
    """    

    def create_empty_nodes():
        constantGenerator = ConstantGenerator(param=PARAMS, randomness=randomness)
        variableGenerator = VariableGenerator()
        for i in range(randomness.get_random_integer(1,PARAMS["max_number_of_empty_nodes"])):
            empty_node = RuleNode(
                                    name="empty_" + variableGenerator.generate_new_lower_case_variabe(),
                                    depth=-1,
                                    params=PARAMS,
                                    randomness=randomness,
                                    constantGenerator=constantGenerator
                                )
            # Create fact nodes for this empty node.
            empty_node.generate_node_variables()
            for j in range(randomness.get_random_integer(1, PARAMS["max_number_of_fact_nodes"])):
                empty_node.generate_a_singular_fact_node()
            dependencyGraph.append_empty_nodes(empty_node)


    def create_complex_joins(complex_node):
        """
            Complex nodes are only one levelled.
        """
        # Create incoming edges to a complex node
        variableGenerator = VariableGenerator()
        for i in range(randomness.get_random_integer(1, PARAMS["max_number_of_incoming_edges_to_a_complex_node"])):
            random_empty_node_or_parsed_node = randomness.random_choice(dependencyGraph.get_empty_nodes() + dependencyGraph.get_parsed_graph().get_parsed_nodes())
            # Check which types are flowing into it already
            # Note: Complex nodes are always one levelled. 
            all_join_variables = complex_node.get_all_join_variables_at_a_level(1)
            edge = Edge(start=random_empty_node_or_parsed_node, end=complex_node, charge="+ve", level=1)
            if len(complex_node.get_all_incoming_rule_edges()) == 1:
                edge.set_operator(randomness.random_choice(["/\\", "and"]))
            else:
                edge.set_operator(randomness.random_choice(["\/", "/\\", "and", "or"]))
            join_variable_set = list()
            if len(all_join_variables) == 0:
                join_variable_set = deepcopy(random_empty_node_or_parsed_node.get_variables())
            else: 
                for var in random_empty_node_or_parsed_node.get_variables():
                    var_choices = [v for v in all_join_variables if v.get_type() == var.get_type()]
                    if randomness.flip_a_coin() and len(var_choices) != 0:
                        # Either choose an existing variable
                        chosen_variable = randomness.random_choice(var_choices)
                        join_variable_set.append(Variable(chosen_variable.get_name(), chosen_variable.get_type(), None))
                    else:
                        # Or create a brand new variable
                        new_variable_name = variableGenerator.generate_new_lower_case_variabe([i.get_name() for i in all_join_variables] + [i.get_name() for i in join_variable_set])
                        join_variable_set.append(Variable(new_variable_name, var.get_type(), None))
                all_join_variables += join_variable_set
            edge.set_join_variables(join_variable_set)
            complex_node.add_incoming_rule_edge(edge)


        # ground the head
        head_variables = list()
        variables_in_the_first_subgoal = complex_node.get_all_incoming_rule_edges()[0].get_join_variables()
        if len(variables_in_the_first_subgoal) != 0:
            for var in complex_node.get_variables():
                head_variables.append(randomness.random_choice(variables_in_the_first_subgoal))
                
        complex_node.over_write_variables(head_variables)
        levelled_variable_object = LeveledVariables(1, head_variables)
        levelled_variable_object.set_probability(randomness.get_small_random_float(0,0))
        complex_node.set_levelled_variable_objects(levelled_variable_object)


    def create_complex_nodes():
        constantGenerator = ConstantGenerator(param=PARAMS, randomness=randomness)
        variableGenerator = VariableGenerator()
        for i in range(randomness.get_random_integer(0,PARAMS["max_number_of_complex_nodes"])):
            complex_node = RuleNode(
                                    name="complex_" + variableGenerator.generate_new_lower_case_variabe(),
                                    depth=-1,
                                    params=PARAMS,
                                    randomness=randomness,
                                    constantGenerator=constantGenerator
                                )
            complex_node.generate_node_variables()
            create_complex_joins(complex_node)
            dependencyGraph.append_complex_node(complex_node)

    # Create a bunch of empty nodes first.
    create_empty_nodes()
    create_complex_nodes()
    
    # No complex node was generated. Abort
    if len(dependencyGraph.get_complex_nodes()) == 0: return 1

    # Join complex nodes with the rest of the graph
    for i in range(PARAMS["max_number_of_outgoing_edges_from_complex_nodes"]):
        random_complex_node = randomness.random_choice(dependencyGraph.get_complex_nodes())
        random_rule_node = randomness.random_choice(dependencyGraph.get_all_rule_nodes())
        level = randomness.get_random_integer(1, random_rule_node.get_max_edge_level())
        inflowing_types = [var.get_type() for var in random_rule_node.get_all_join_variables_at_a_level(level)]
        if len(inflowing_types) == 0:
            # In case of no inflowing types, no need to move further
            continue
        inflowing_variables = random_rule_node.get_all_join_variables_at_a_level(level)

        # Create an edge from random_complex_node to random_rule_node
        edge = Edge(start=random_complex_node, end=random_rule_node, charge="+ve", level=level)
        join_variable_set = list()
        variableGenerator = VariableGenerator()
        for var in random_complex_node.get_variables():
            variable_choices = [v for v in inflowing_variables if v.get_type() == var.get_type()]
            new_variable_name = ""
            if len(variable_choices) == 0:
                new_variable_name = variableGenerator.generate_new_lower_case_variabe([v.get_name() for v in inflowing_variables])
            else:
                new_variable_name = randomness.random_choice(variable_choices).get_name()
            new_variable = Variable(new_variable_name, var.get_type(), None)
            join_variable_set.append(new_variable)
        edge.set_join_variables(join_variable_set)
        random_rule_node.add_incoming_rule_edge(edge)
        random_complex_node.add_outgoing_rule_edge(edge)

    # This will compute the charge for the newly added complex and empty nodes 
    compute_node_charge_property_value(dependencyGraph.get_output_node(), [])

    # This will add complex nodes and empty nodes in the ancestry database 
    dependencyGraph.clear_ancestry_information()
    dependencyGraph.retrieve_ancestry_information()

    if fulllogs: 
        logging.add_log_text("[ScallopComplexNodesPass] Updated graph stats after ScallopComplexNodes graph pass:")
        logging.add_log_text("    >>> Number of nodes in positive ancestry: " + str(len(dependencyGraph.get_positive_ancestry()))  + "  ->  " + str([i.get_name() for i in dependencyGraph.get_positive_ancestry()]))
        logging.add_log_text("    >>> Number of nodes in negative ancestry: " + str(len(dependencyGraph.get_negative_ancestry()))  + "  ->  " + str([i.get_name() for i in dependencyGraph.get_negative_ancestry()]))
        logging.add_log_text("    >>> Number of nodes in unknown ancestry: " + str(len(dependencyGraph.get_unknown_ancestry()))  + "  ->  " + str([i.get_name() for i in dependencyGraph.get_unknown_ancestry()]))
        logging.add_log_text("    >>> Number of nodes not in ancestry: " + str(len(dependencyGraph.get_not_ancestry()))  + "  ->  " + str([i.get_name() for i in dependencyGraph.get_not_ancestry()]))
