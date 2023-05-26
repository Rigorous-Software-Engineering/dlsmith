from termcolor import colored
from dlsmith.utils.variableGenerator import generate_var_not_in_list


def MOD_EXP(dependencyGraph, randomness, logging, engine, stats):
    """
            Expands the results of Q_orig by modifying 'a single' subgoal in Q_orig.
            The modification is renaming a variable in a subgoal.
            The varialble should appear more than once in the body of the rule.
            When this variable is replaced with a fresh variable, we will have a mapping 
            from Q_trans to Q_orig but no mapping from Q_orig to Q_trans. Thus expanding the result.
    """
    # Set of nodes in the positive ancestry.
    positive_ancestry = dependencyGraph.get_positive_ancestry()
    # Set of nodes not in the ancestry.
    not_in_ancestry = dependencyGraph.get_not_ancestry()
    allowed_nodes = positive_ancestry + not_in_ancestry

    allowed_nodes = [i for i in allowed_nodes if len(i.get_all_incoming_rule_edges()) >= 2]
    if len (allowed_nodes) == 0: return 1
    chosen_node = randomness.random_choice(allowed_nodes)
    chosen_level = randomness.get_random_integer(1, chosen_node.get_max_edge_level())
    seen_vars = list()
    duplicate_vars = list()
    for edge in [i for i in chosen_node.get_all_incoming_rule_edges() if i.get_level() == chosen_level and i.get_charge() == "+ve"]:
        for var in edge.get_join_variables():
            if var.get_name() in [i.get_name() for i in seen_vars]: duplicate_vars.append(var)
            else: seen_vars.append(var)
    if len(duplicate_vars) == 0: return 1
    chosen_variable = randomness.random_choice(duplicate_vars)
    new_variable_name = generate_var_not_in_list([i.get_name() for i in seen_vars])
    for var in seen_vars:
        if var.get_name() == chosen_variable.get_name(): var.set_name(new_variable_name)

    logging.add_log_text("\t[QUERYFUZZ_MOD_EXP]: Modified the variable " + chosen_variable.get_name() + " in node " + chosen_node.get_name() + " at level " + str(chosen_level) + " with a new variable name -> " + new_variable_name)
    stats.increment_transformation_count("MOD_EXP")

def REM_EXP():
    """
            Expands the result of Q_orig by removing a subgoal. When we remove a subgoal, there is
            always a containment map from Q_trans to Q_orig but not necessarily in the other directions. 
            The absence of a containment map in the other direction expands the result.

            In dlsmith's framework, REM_EXP is already implemented as EXP_EDGE_REM.
    """ 
    # No need to implement. Already implemented as another transformation
    pass