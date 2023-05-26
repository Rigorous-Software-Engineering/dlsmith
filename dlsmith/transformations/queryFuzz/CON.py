

from copy import deepcopy
from termcolor import colored


def ADD_CON():
    """
        Contracts the results of the original query by adding a new sub-goal.
        When we add a new subgoal, we make sure that there is a containment map from Q_orig to 
        Q_trans. Intuitively, ADD_CON adds a new subgoal to Q_orig which introduces new joins.

        In dlsmith's framework this is already implemented as CON_EDGE_ADD.

    """
    # No need to implement
    pass





def MOD_CON(dependencyGraph, randomness, logging, engine, full_logs, stats):
    """
        Contracts the result of Q_orig by modifying 'all occurrances' of a single variable in Q_orig. 
        If there is only one variable of a particular type in the body, then we cannot do anything and we just return.
        Otherwise we pick a random variable and replace it with another variable. 

        R_2 should be either in the postive or not in the ancestry of O. 

        rel 0.9::complex_c(b) = empty_a(a, b) /\ (empty_a(a, c) /\ empty_a(d, b))

        Chosen variable: b
        Replacement variable: c

    """
    full_logging_text = ""

    node_level_info = dict()
    # Set of nodes in the positive ancestry.
    positive_ancestry = dependencyGraph.get_positive_ancestry()
    # Set of nodes not in the ancestry.
    not_in_ancestry = dependencyGraph.get_not_ancestry()
    allowed_nodes = positive_ancestry + not_in_ancestry

    # Pick a node with a level containing atleast 2 edges.
    for node in allowed_nodes:
        for level in range(1, node.get_max_edge_level() + 1):
            if len([edge for edge in node.get_all_incoming_rule_edges() if edge.get_level() == level]) >= 2: 
                if node.get_name() in node_level_info.keys(): node_level_info[node].append(level)
                else: node_level_info[node] = [level]
    if len(node_level_info.keys()) == 0: return 1
    chosen_node = randomness.random_choice(list(node_level_info.keys()))
    chosen_level = randomness.random_choice(node_level_info[chosen_node])

    full_logging_text += "\t\t[queryFuzz_mod_con]: Chosen node: [" + chosen_node.get_name() + "]\n\t\t[queryFuzz_mod_con]: Chosen level: " + str(chosen_level)

    # Now check if at the chosen level, there is a type with 2 distinct variables.
    # Pick a variable and check if there is another variable with the same type but different name. if not then quit. if yes then good.
    
    all_distinct_variables = list()
    for i in [edge for edge in chosen_node.get_all_incoming_rule_edges() if edge.get_level() == chosen_level]:
        for var in i.get_join_variables():
            if var.get_name() not in all_distinct_variables: all_distinct_variables.append(var)
    
    #Bug Fix: All ccurances of variable "_" cannot be replaced by a single variable. This creates type errors.
    all_distinct_variables = [i for i in all_distinct_variables if i.get_name() != "_"]
    if len(all_distinct_variables) == 0: return 1
    
    # Pick a variable and replace all of its occurings with an existing variable of the same type.
    chosen_variable = deepcopy(randomness.random_choice(all_distinct_variables))
    other_variable_options = [i for i in all_distinct_variables if i.get_type() == chosen_variable.get_type() and i.get_name() != chosen_variable.get_name()]
    other_variable_options = [i for i in other_variable_options if i.get_name() != "_"]
    full_logging_text += "\n\t\t[queryFuzz_mod_con]: Chosen variable: " + chosen_variable.get_name()
    full_logging_text += "\n\t\t[queryFuzz_mod_con]: Other variable options: " + str([i.get_name() for i in other_variable_options])
    if len(other_variable_options) == 0: return 1
    replacement_variable = deepcopy(randomness.random_choice(other_variable_options))
    full_logging_text += "\n\t\t[queryFuzz_mod_con]: Replacement variable: " + replacement_variable.get_name()
    full_logging_text += "\n\t\t[queryFuzz_mod_con]: [" + chosen_node.get_name() + "] has " + str(len(chosen_node.get_all_incoming_rule_edges())) + " incoming edges" 

    # Replace all occurrances
    for edge in [i for i in chosen_node.get_all_incoming_rule_edges() if i.get_level() == chosen_level]:
        for var in edge.get_join_variables():
            if var.get_name() == chosen_variable.get_name(): var.set_name(replacement_variable.get_name())

    # Also update the variable name in the head
    levelled_variable_object = chosen_node.get_levelled_variable_objects(chosen_level)
    for var in levelled_variable_object.get_vars():
        if var.get_name() == chosen_variable.get_name(): var.set_name(replacement_variable.get_name())

    if full_logs: logging.add_log_text(full_logging_text)
    logging.add_log_text("\t[QUERYFUZZ_MOD_CON]: Replaced all occurances of the variable " + chosen_variable.get_name() + " with the variable " + replacement_variable.get_name())
    stats.increment_transformation_count("MOD_CON")
