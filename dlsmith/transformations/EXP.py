"""
EXPANDING Transformations on the Data Dependency Graph. 
"""


from termcolor import colored
from dlsmith.dataDependencyGraph.edge import Edge
from dlsmith.dataDependencyGraph.graphUtils import compute_node_charge_property_value, compute_strata_property_values, compute_strata_property_values_for_descendants, find_all_positive_descendants, find_all_rule_ancestors, introduces_a_cycle_with_every_node_inlined
from dlsmith.dataDependencyGraph.ruleNode import LeveledVariables
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.variableGenerator import VariableGenerator
from copy import deepcopy

def EXP_NODE_ADD(dependencyGraph, randomness, logging, params, engine, stats):
    """
        For an output node O, a fact node can be added anywhere in the DDG if
        the corresponding Rule node R for that fact is in the ancestory of O AND 
        the path from R to O contains an even number of negative edges. 
    """

    # **** Fact node *****
    if len(dependencyGraph.get_positive_ancestry()) == 0: return 1
    chosen_rule_node = randomness.random_choice(dependencyGraph.get_positive_ancestry())
    # We only add a fact node if all the types are base types
    non_general_variable_types = [var.get_type() for var in chosen_rule_node.get_variables() if var.get_type() not in params["general_types"]]
    if len(non_general_variable_types) != 0 or len(chosen_rule_node.get_variables()) == 0: return 1
    new_fact_node = chosen_rule_node.generate_a_singular_fact_node()
    new_fact_node.set_tranformed_flag_to_true()
    logging.add_log_text("\t[EXP_NODE_ADD]: Added a fact node to the rule node " + chosen_rule_node.get_name())
    stats.increment_transformation_count("EXP_NODE_ADD")


def EXP_NODE_REM(dependencyGraph, randomness, logging, engine, stats):
    """
        For an output node O, removing a fact node from a rule node R will expand the result in O, 
        if R is in the negative ancestry of O.
    """

    if len(dependencyGraph.get_negative_ancestry()) == 0: return 1
    chosen_rule_node = randomness.random_choice(dependencyGraph.get_negative_ancestry())
    chosen_rule_node.remove_a_fact_node()
    logging.add_log_text("\t[EXP_NODE_REM]: Removed a fact node from the rule node " + chosen_rule_node.get_name())
    stats.increment_transformation_count("EXP_NODE_REM")


def EXP_EDGE_ADD(dependencyGraph, randomness, logging, engine, full_logs, stats):
    """
        For an output node, adding an edge with a label <n+1, +ve> from a rule node R_1 to a rule node R_2 will 
        expand the results in O, if R_2 is in the positive ancestry of O and 
        n = max([edge.get_level() for edge in R_2.get_all_incoming_edges()])
        (Adding a disjunction)

        1) R_2 is a node in the positive ancestry of O.
        2) R_1 is not in the ancestry of R_2 [SET_1]  
        3) R_1 is in the same stratum as R_2 [SET_2]
        4) R_1 is in the positive descendants of R_2 [SET_3]

            {SET_1 ∩ SET_3} U SET_2

    """

    full_logging_text = ""

    if len(dependencyGraph.get_positive_ancestry()) == 0: return 1
    nodes_in_positive_ancestory_with_incoming_edges = [node for node in dependencyGraph.get_positive_ancestry() if len(node.get_all_incoming_rule_edges()) != 0]
    # We dont want complex or empty nodes as end nodes.
    nodes_in_positive_ancestory_with_incoming_edges = [i for i in nodes_in_positive_ancestory_with_incoming_edges if i not in dependencyGraph.get_complex_nodes() + dependencyGraph.get_empty_nodes()]
    if len(nodes_in_positive_ancestory_with_incoming_edges) == 0: return 1
    # Pick an R_2 which is in the positive ancestory of O
    R_2 = randomness.random_choice(nodes_in_positive_ancestory_with_incoming_edges)
    
    full_logging_text += "\n\t\t[exp_edge_add]: Chosen end node: [" + R_2.get_name() + "]"
    # Set of nodes not in the ancestry of R_2 [SET_1]
    ancestry_of_R_2 = find_all_rule_ancestors(R_2, [])
    SET_1 = [node for node in dependencyGraph.get_all_rule_nodes() if node not in ancestry_of_R_2]
    
    # Set of nodes in the same stratum as R_2 [SET_2]
    for node in dependencyGraph.get_all_rule_nodes(): node.set_stratum("NONE") # Refresh stratum info in the graph if any
    R_2.set_stratum(0)
    compute_strata_property_values(R_2, [])    
    SET_2 = [node for node in dependencyGraph.get_all_rule_nodes() if node.get_stratum() == 0]

    # Set of nodes that are in positive descendants of R_2
    for node in dependencyGraph.get_all_rule_nodes(): node.set_stratum("NONE") # Refresh stratum info in the graph if any
    R_2.set_stratum(0)
    compute_strata_property_values_for_descendants(R_2, [])
    SET_3 = [node for node in dependencyGraph.get_all_rule_nodes() if node.get_stratum() == 0]
    
    accpetble_values_for_R_1 = [node for node in SET_1 if node in SET_3] + SET_2
    full_logging_text += "\n\t\t[exp_edge_add]: acceptable values as start node for this expanding edge: " + str([i.get_name() for i in accpetble_values_for_R_1])
    R_1 = randomness.random_choice(accpetble_values_for_R_1)

    if engine == "souffle":
        if introduces_a_cycle_with_every_node_inlined(R_2, R_1): 
            return 1

    max_level_in_R_2 = R_2.get_max_edge_level()
    edge = Edge(start=R_1, end=R_2, charge="+ve", level=max_level_in_R_2+1)
    # ****** Add join variables for the edge ******
    var_types_in_R_2 = [var.get_type() for var in R_2.get_variables()]
    var_types_in_R_1 = [var.get_type() for var in R_1.get_variables()]
    for var in var_types_in_R_2: 
        if var not in var_types_in_R_1: return 1

    edge_join_variables = list()
    new_variables_for_R_2 = list()
    temp_variable_generator = VariableGenerator()
    
    for var in R_1.get_variables():
        new_variable = Variable(name=temp_variable_generator.generate_new_lower_case_variabe(), vtype=var.get_type(), value=None)
        edge_join_variables.append(new_variable)
    edge.set_join_variables(edge_join_variables)
    
    for var in R_2.get_variables():
        var_choices = [v for v in edge_join_variables if v.get_type() == var.get_type()]
        chosen_var = deepcopy(randomness.random_choice(var_choices))
        new_variables_for_R_2.append(chosen_var)
    R_2.levelled_variable_objects.append(LeveledVariables(level=max_level_in_R_2+1, vars=new_variables_for_R_2))
    

    # **** Add an edge from R_1 to R_2 ****
    R_1.add_outgoing_rule_edge(edge)
    R_2.add_incoming_rule_edge(edge)
    edge.set_tranformed_flag_to_true()

    # **** Add R_1 to the positve ancestry to O.
    if R_1 in dependencyGraph.get_not_ancestry():
        for i,node in enumerate(dependencyGraph.get_not_ancestry()):
            if node == R_1: dependencyGraph.get_not_ancestry().pop(i) 
        dependencyGraph.append_positive_ancestry(R_1)
    if R_1 in dependencyGraph.get_negative_ancestry():
        for i,node in enumerate(dependencyGraph.get_negative_ancestry()):
            if node == R_1: dependencyGraph.get_negative_ancestry().pop(i) 
        dependencyGraph.append_unknown_ancestry(R_1)

    if full_logs: logging.add_log_text(full_logging_text)
    logging.add_log_text("\t[EXP_EDGE_ADD]: Added an edge from  " + R_1.get_name()  + " to " + R_2.get_name()) 
    stats.increment_transformation_count("EXP_EDGE_ADD")


def EXP_EDGE_REM(dependencyGraph, randomness, logging, engine, stats):
    """ 
        For an output node O, removing a positive edge from a rule node R_1 to 
        a rule node R_2 will expand the result in O if R_2 is in the positive 
        ancestory of O.
    """
    if len(dependencyGraph.get_positive_ancestry()) == 0: return 1
    nodes_in_positive_ancestory_with_incoming_edges = [node for node in dependencyGraph.get_positive_ancestry() if len(node.get_all_incoming_rule_edges()) != 0]
    if len(nodes_in_positive_ancestory_with_incoming_edges) == 0: return 1
    # Pick an R_2 which is in the positive ancestory of O
    R_2 = randomness.random_choice(nodes_in_positive_ancestory_with_incoming_edges)
    R_1 = randomness.random_choice(R_2.get_all_incoming_rule_edges()).get_start_node()
    edge = randomness.random_choice([edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_start_node() == R_1])

    # ******* Check if this edge can be safely removed
    if not edge.check_edge_removal_safety(): return 1 # Edge not safe to remove

    

    # ****** Update R_1 *******
    for e, i in enumerate(R_1.get_all_outgoing_rule_edges()): 
        if e == edge: R_1.get_all_outgoing_rule_edges().pop(i)

    # ****** Update R_2 *******
    for e, i in enumerate(R_2.get_all_incoming_rule_edges()): 
        if e == edge: R_2.get_all_incoming_rule_edges().pop(i)

    # ****** Update ancestry *******
    # We have no option but to recompute the ancestry
    compute_node_charge_property_value(dependencyGraph.get_output_node(), [])
    dependencyGraph.retrieve_ancestry_information()

    logging.add_log_text("\t[EXP_EDGE_REM]: Removed an edge from  " + R_1.get_name()  + " to " + R_2.get_name())
    stats.increment_transformation_count("EXP_EDGE_REM")

