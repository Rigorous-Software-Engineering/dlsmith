
from termcolor import colored
from dlsmith.dataDependencyGraph.edge import Edge
from dlsmith.dataDependencyGraph.graphUtils import find_all_descendants
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.variableGenerator import VariableGenerator, generate_var_not_in_list


def ADD_EQU(dependencyGraph, randomness, logging, engine, stats):
    """
        Preserves the results of the original query while adding a new sub-goal
        The key idea behind this transformation is the following:
        When we add a new sub_goal (new_sub) to Q_orig, we make sure that there is
        a containment map from Q_trans to Q_orig. We know that in case of ADD, a
        containment map always exist from Q_orig to Q_trans. So just constructing
        a containment map from Q_trans to Q_orig will make the two queries equivalent.

        In dlsmith's framework, ADD_EQU adds an edge from R_1 to R_2 where R_2 can be any node in the graph. 
        Where as in EQU_EDGE_ADD(), R_2 must not be in the ancestry of R_1.
    """

    R_2 = randomness.random_choice( dependencyGraph.get_all_rule_nodes() )
    incoming_edges = [edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_charge() == "+ve"]
    if len(incoming_edges) == 0: return 1
    incoming_edge = randomness.random_choice(incoming_edges)
    R_1 = incoming_edge.get_start_node()
    all_body_vars = R_2.get_all_join_variables_at_a_level(level=incoming_edge.get_level())
    all_body_var_names = [var.get_name() for var in all_body_vars] 
    new_variables = list()
    for var in incoming_edge.get_join_variables():
        new_var_name = var.get_name()
        if randomness.flip_a_coin(): 
            new_var_name = generate_var_not_in_list(all_body_var_names)
            all_body_var_names.append(new_var_name)
        new_variable = Variable(name=new_var_name, vtype=var.get_type(), value=None)    
        new_variables.append(new_variable)
    new_edge = Edge(start=R_1, end=R_2, charge="+ve", level=incoming_edge.get_level())
    new_edge.set_join_variables(new_variables)
    R_1.add_outgoing_rule_edge(new_edge)
    R_2.add_incoming_rule_edge(new_edge)
    logging.add_log_text("\t[QUERYFUZZ_ADD_EQU]: Added an edge from  " + R_1.get_name() + " to " + R_2.get_name())
    stats.increment_transformation_count("ADD_EQU")

def MOD_EQU():
    # Super lame. No need to implement.
    pass



def exits_containment(edge, R_2, level):
    """
        Returns True if an edge can be removed while ensuring that the containment mapping will be respected by both sides.

        A variable can only be mapped to "_" if there is no other occuracnces of that variable in that rule.
    """
    # If there is not other edge from R_1 to R_2 at this level then we quit.
    
    all_edges = [ed for ed in R_2.get_all_incoming_rule_edges() if ed.get_level() == level and ed.get_charge() == "+ve"]
    other_similar_edges = [ed for ed in R_2.get_all_incoming_rule_edges() if ed.get_level() == level and ed != edge and ed.get_charge() == "+ve" and ed.get_start_node() == edge.get_start_node()]
    other_edges = [ed for ed in R_2.get_all_incoming_rule_edges() if ed.get_level() == level and ed != edge and ed.get_charge() == "+ve"]
    edge_variables = [i.get_name() for i in edge.get_join_variables()]
    if len(other_similar_edges) == 0:
        return False
    # Non-removed variables
    other_variables = list()
    for ed in other_edges: other_variables += [i.get_name() for i in ed.get_join_variables()]
    # Also add the head variables
    other_variables += [i.get_name() for i in R_2.get_levelled_variable_objects(level).get_vars()]
    for other_edge in other_similar_edges:
        local_map = dict()
        local_map_found = True
        global_map_found = True
        for i, var in enumerate([i.get_name() for i in edge.get_join_variables()]):
            if var not in local_map.keys():
                # Added to the local map
                local_map[var] = [j.get_name() for j in other_edge.get_join_variables()][i]
                continue
            if local_map[var] == "_":
                # A variable can only be mapped to "_" if there is no other occuracnces of that variable in that rule.
                local_map_found = False
                break
            if local_map[var] != [j.get_name() for j in other_edge.get_join_variables()][i]:
                # Contradiction here. No local map possible for this subgoal
                local_map_found = False
                break        
        if not local_map_found: continue
        # Check if this map is also global
        # For variables that are mapped to something else, check that there is no variable of that name 
        for var in list(local_map.keys()):
            if local_map[var] != var and var in other_variables:
                global_map_found = False
                break
        if global_map_found: 
            return True
    return False




def REM_EQU(dependencyGraph, randomness, logging, engine, stats):
    """
        Preserve the result of the original query while removing a sub-goal and making sure that there is a containment map 
        from the orignial query to the transformed query.

        In dlsmith's framework, REM_EQU removes an edge from R_1 to R_2 where R_2 can be any node in the graph. 
    """
    def get_parent_with_2_edges(R_2):
        for level in range(1, R_2.get_max_edge_level() + 1):
            seen_parents = list()
            for edge in [i for i in R_2.get_all_incoming_rule_edges() if i.get_level() == level and i.get_charge() == "+ve"]:
                if edge.get_start_node() in seen_parents: 
                    return edge, edge.get_start_node(), level
                seen_parents.append(edge.get_start_node())
        return None, None, None 
    
    R_2 = randomness.random_choice(dependencyGraph.get_all_rule_nodes())
    edge, R_1, level = get_parent_with_2_edges(R_2)
    if edge is None: 
        return 1
    # Check the existance of a containment mapping from R_1 to R_2. 
    if not exits_containment(edge, R_2, level): return 1

    if not edge.check_edge_removal_safety(): 
        return 1 # Edge not safe to remove
    # Safe to remove
    # ******** Update R_1 ***************
    for i, e in enumerate(R_1.get_all_outgoing_rule_edges()): 
        if e == edge: R_1.get_all_outgoing_rule_edges().pop(i)
    # ******** Update R_2 ***************
    for i, e in enumerate(R_2.get_all_incoming_rule_edges()): 
        if e == edge: R_2.get_all_incoming_rule_edges().pop(i)

    logging.add_log_text("\t[QUERYFUZZ_REM_EQU]: Removed an edge from " + R_1.get_name() + " to " + R_2.get_name() + " at level " + str(level) + " with variables " + str([i.get_name() for i in edge.get_join_variables()]))
    stats.increment_transformation_count("REM_EQU")