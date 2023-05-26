"""
CONTRACTING Transformations on the Data Dependency Graph. 
"""

from termcolor import colored
from dlsmith.dataDependencyGraph.edge import Edge
from dlsmith.dataDependencyGraph.graphUtils import compute_node_charge_property_value, compute_strata_property_values, find_all_rule_ancestors, introduces_a_cycle_with_every_node_inlined
from dlsmith.dataDependencyGraph.ruleNode import RuleNode
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.variableGenerator import generate_var_not_in_list
from copy import deepcopy

def CON_NODE_ADD(dependencyGraph, randomness, logging, params, engine, stats):
    """
        For an output node O, adding a fact node to a rule node R will contract the result in O, if R 
        is in the negative ancestry of O. 
    """

    if len(dependencyGraph.get_negative_ancestry()) == 0: return 1
    chosen_rule_node = randomness.random_choice(dependencyGraph.get_negative_ancestry())
    # We only add a fact node if all the types are base types
    non_general_variable_types = [var.get_type() for var in chosen_rule_node.get_variables() if var.get_type() not in params["general_types"]]
    if len(non_general_variable_types) != 0 or len(chosen_rule_node.get_variables()) == 0: return 1
    new_fact_node = chosen_rule_node.generate_a_singular_fact_node()
    new_fact_node.set_tranformed_flag_to_true()
    logging.add_log_text("\t[CON_NODE_ADD]: Added a fact node in the rule node " + chosen_rule_node.get_name())
    stats.increment_transformation_count("CON_NODE_ADD")



def CON_NODE_REM(dependencyGraph, randomness, logging, engine, stats):
    """
        ** FACT NODE ** 
            For an output node O, removing a fact node F from a rule node R will contract
            the result in O, if the path from R to O has an even number of negative edges. 

        ** RULE NODE **
            Can we remove a Rule node completely from a graph and safely contract the results of an output node?
    """

    if len(dependencyGraph.get_positive_ancestry()) == 0: return 1
    chosen_rule_node = randomness.random_choice(dependencyGraph.get_positive_ancestry())
    chosen_rule_node.remove_a_fact_node()
    logging.add_log_text("\t[CON_NODE_REM]: Removed a fact node from " + chosen_rule_node.get_name())
    stats.increment_transformation_count("CON_NODE_REM")


def CON_EDGE_ADD(dependencyGraph, randomness, params, logging, engine, stats):
    """
        For an output node O, adding a postive edge from a rule node R_1 to a rule node R_2 will 
        contract the result in O, if R_2 is in the positive ancestory of O.
        1) R_1 can be any node in the graph.
        2) R_2 is in the positive ancestory of O with atleast one edge. SET_1
        3) R_2 is either at the same stratum as R_1 SET_2 OR not in the ancestry of R_1 SET_3.
            -> SET_1 ∩ {SET_2 U SET_3}
    """

    R_1 = randomness.random_choice(dependencyGraph.get_all_rule_nodes() + dependencyGraph.get_parsed_graph().get_parsed_nodes())        # Any node in the graph
    positive_ancestory_with_atleast_one_edge = [node for node in dependencyGraph.get_positive_ancestry() if len(node.get_all_incoming_rule_edges()) > 0]
    if len(positive_ancestory_with_atleast_one_edge) == 0: return 1
    # A node in the positive ancestory of O with atleast one edge
    SET_1 = positive_ancestory_with_atleast_one_edge
    
    ## Set of nodes not in the ancestry of R_1 [SET 2]
    ancestry_of_R_1 = find_all_rule_ancestors(R_1, [])
    SET_2 = [node for node in dependencyGraph.get_all_rule_nodes() if node not in ancestry_of_R_1]

    # Set of nodes at the same stratum as R_1 [SET 3]
    for node in dependencyGraph.get_all_rule_nodes(): node.set_stratum("NONE") # Refresh stratum info in the graph if any
    R_1.set_stratum(0)
    compute_strata_property_values(R_1, [])    
    SET_3 = [node for node in dependencyGraph.get_all_rule_nodes() if node.get_stratum() == 0]

    acceptable_values_for_R_2 = [node for node in SET_3 + SET_2 if node in SET_1]
    if len(acceptable_values_for_R_2) == 0: return 1
    R_2 = randomness.random_choice(acceptable_values_for_R_2)
    level = randomness.get_random_integer(1, R_2.get_max_edge_level())
    new_edge = Edge(start=R_1, end=R_2, charge="+ve", level=level)

    # Check if adding and edge from R_1 to R_2 will not violate any of inlining laws in souffle.
    if engine == "souffle":
        if introduces_a_cycle_with_every_node_inlined(R_2, R_1): 
            return 1

    # **** Add an edge from R_1 to R_2 ****
    R_1.add_outgoing_rule_edge(new_edge)
    R_2.add_incoming_rule_edge(new_edge)
    new_edge.set_tranformed_flag_to_true()

    # **** Add R_1 to the positve ancestry to O.
    if R_1 in dependencyGraph.get_not_ancestry():
        for i,node in enumerate(dependencyGraph.get_not_ancestry()):
            if node == R_1: dependencyGraph.get_not_ancestry().pop(i) 
        dependencyGraph.append_positive_ancestry(R_1)
    if R_1 in dependencyGraph.get_negative_ancestry():
        for i,node in enumerate(dependencyGraph.get_negative_ancestry()):
            if node == R_1: dependencyGraph.get_negative_ancestry().pop(i) 
        dependencyGraph.append_unknown_ancestry(R_1)


    # **** Add join variables in the edge ******
    all_edges_in_R_2_at_this_level = [edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_level() == level]
    all_positive_variables = list()
    for edge in all_edges_in_R_2_at_this_level: 
        all_positive_variables += edge.get_join_variables()
    new_variables_for_this_edge = list()
    for var_type in [var.get_type() for var in R_1.get_variables()]:
        pos_vars_of_this_type = [var for var in all_positive_variables if var.get_type() == var_type]
        if len(pos_vars_of_this_type) == 0:  
            # This is a new type
            new_var_name = generate_var_not_in_list([var.get_name() for var in all_positive_variables])
            new_var = Variable(new_var_name, var_type , None)
            all_positive_variables.append(new_var)
            new_variables_for_this_edge.append(new_var)
        else: 
            new_variables_for_this_edge.append(deepcopy(randomness.random_choice(pos_vars_of_this_type)))
    new_edge.set_join_variables(new_variables_for_this_edge)
    logging.add_log_text("\t[CON_EDGE_ADD]: Added an edge from " + R_1.get_name() + " to " + R_2.get_name())
    stats.increment_transformation_count("CON_EDGE_ADD")


def CON_EDGE_REM(dependencyGraph, randomness, logging, engine, stats):
    """
        For an output node O, removing an edge with label <n, +ve> from a rule node R_1 to a rule mode R_2 will
        contract O if R_2 is in the positive ancestry of O and 2 <= n <= max([edge.get_level() for edge in R_2.get_all_incoming_edges()])

        I think removing just one edge will be problematic. We have to pick a level and remove all the edges at that level.
    """

    positive_ancestory_with_atleast_two_levels = [node for node in dependencyGraph.get_positive_ancestry() if node.get_max_edge_level() > 1]
    if len(positive_ancestory_with_atleast_two_levels) == 0: return 1
    R_2 = randomness.random_choice(positive_ancestory_with_atleast_two_levels)
    level_to_remove = randomness.get_random_integer(1, R_2.get_max_edge_level())
    edges_to_remove = [edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_level() == level_to_remove]
    
    for edge in edges_to_remove:
        start_node = edge.get_start_node()
        for i, e in enumerate(R_2.get_all_incoming_rule_edges()):
            if e == edge: R_2.get_all_incoming_rule_edges().pop(i)
        for i, e in enumerate(start_node.get_all_outgoing_rule_edges()): 
            if e == edge: start_node.get_all_outgoing_rule_edges().pop(i)
    
    # ****** Decrease edge levels *****
    # This keeps everything clean and avoid many problems
    for edge in R_2.get_all_incoming_rule_edges():
        if edge.get_level() > level_to_remove: edge.set_level(edge.get_level() - 1)
    
    R_2.remove_levelled_variable_object_for_level(level_to_remove)
    for labelled_var_obj in R_2.get_all_levelled_variable_objects():
        if labelled_var_obj.get_level() > level_to_remove:
            labelled_var_obj.update_level(labelled_var_obj.get_level() - 1)


    # ****** Update ancestry *******
    # We have no option but to recompte the ancestry
    compute_node_charge_property_value(dependencyGraph.get_output_node(), [])
    dependencyGraph.retrieve_ancestry_information()
    logging.add_log_text("\t[CON_EDGE_REM]: Removed an incoming edge to" + R_2.get_name())
    stats.increment_transformation_count("CON_EDGE_REM")


def CON_ADD_SELF_EDGE(dependencyGraph, randomness, logging, engine, full_logs, stats):

    full_log_text = ""
    # R_2 must be in the positive ancestry 
    positive_ancestory_with_atleast_one_incoming_edge = [node for node in dependencyGraph.get_positive_ancestry() if len(node.get_all_incoming_rule_edges()) > 0]
    if len(positive_ancestory_with_atleast_one_incoming_edge) == 0: return 1
    R_2 = randomness.random_choice(positive_ancestory_with_atleast_one_incoming_edge)

    if engine == "souffle":
        if introduces_a_cycle_with_every_node_inlined(R_2, R_2): 
            return 1

    edge_level = randomness.get_random_integer(1, R_2.get_max_edge_level())
    full_log_text += "\n\t\t[con_add_self_edge]: Level for the self edge: " + str(edge_level)
    # Set join variables for this edge
    all_edges_in_R_2_at_this_level = [edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_level() == edge_level]
    all_positive_variables = list()
    for edge in all_edges_in_R_2_at_this_level: all_positive_variables += edge.get_join_variables()
    new_variables_for_this_edge = list()
    for var_type in [var.get_type() for var in R_2.get_variables()]:
        pos_vars_of_this_type = [var for var in all_positive_variables if var.get_type() == var_type]
        new_variables_for_this_edge.append(deepcopy(randomness.random_choice(pos_vars_of_this_type)))
    # Create edge
    new_edge = Edge(start=R_2, end=R_2, charge="+ve", level=edge_level)
    new_edge.set_join_variables(new_variables_for_this_edge)
    R_2.add_outgoing_rule_edge(new_edge)
    R_2.add_incoming_rule_edge(new_edge)
    new_edge.set_tranformed_flag_to_true()
    if full_logs: logging.add_log_text(full_log_text)
    logging.add_log_text("\t[CON_ADD_SELF_EDGE]: Added a self edge at an existing level for node: " + R_2.get_name())
    stats.increment_transformation_count("CON_ADD_SELF_EDGE")
