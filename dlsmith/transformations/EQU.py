
"""
EQUIVALENT Transformations on the Data Dependency Graph. 
"""
from copy import deepcopy
from random import random
from unittest.signals import removeHandler
from termcolor import colored
from dlsmith.dataDependencyGraph.edge import Edge
from dlsmith.dataDependencyGraph.graphUtils import compute_strata_property_values, find_all_descendants, find_all_rule_ancestors, introduces_a_cycle_with_every_node_inlined
from dlsmith.dataDependencyGraph.ruleNode import LeveledVariables, RuleNode
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.variableGenerator import generate_var_not_in_list
from dlsmith.utils.variableGenerator import VariableGenerator

def EQU_NODE_ADD(dependencyGraph, randomness, logging, params, engine, full_logs, stats):
    """
        For an output node O, a fact node can be added anywhere in the DDG if the corresponding 
        Rule node for that fact node is not in the ancestory of O. 
        
        We can also add a Rule node, but ofcourse when we add it, it will be completey
        disconnected with the rest of the graph. Subsequent EDGE transformations should
        connect this node with the rest of the graph. 
    """

    if randomness.flip_a_coin():
        # FACT NODE
        if len(dependencyGraph.get_not_ancestry()) == 0: return 1
        chosen_rule_node = randomness.random_choice(dependencyGraph.get_not_ancestry())
        # We only add a fact node if all the types are base types
        non_general_variable_types = [var.get_type() for var in chosen_rule_node.get_variables() if var.get_type() not in params["general_types"]]
        if len(non_general_variable_types) != 0 or len(chosen_rule_node.get_variables()) == 0: return 1
        new_fact_node = chosen_rule_node.generate_a_singular_fact_node()
        new_fact_node.set_tranformed_flag_to_true()
        logging.add_log_text("\t[EQU_NODE_ADD]: Added a new fact node to [" + chosen_rule_node.get_name() + "]")
    else:
        # RULE NODE
        new_rule_node = dependencyGraph.generate_a_singular_rule_node()
        dependencyGraph.append_not_in_ancestry(new_rule_node)
        new_rule_node.set_tranformed_flag_to_true()

        logging.add_log_text("\t[EQU_NODE_ADD]: Added a new relation [" + new_rule_node.get_name() + "]")
        stats.increment_transformation_count("EQU_NODE_ADD")



def EQU_NODE_REM(dependencyGraph, randomness, logging, engine, params, full_logs, stats):
    """
        FactNode:
        For an output node O, a fact node can be removed anywhere in the DDG if the corresponding 
        Rule node for that fact node is not in the ancestory of O.

        RuleNode: 
        Pick a rule node that is not in the ancestory of the output node
        Get all edges that are incoming into the node. remove them 
        Get all the children of this node. Update the join information in the children?
        WARNING: Removing a node can unground variables in the children!! So we need to check this before we can safely remove a rule node.
                 If removing a rule node can unground variables in some child node then the transformation failed and we move on. 
    """

    if len(dependencyGraph.get_not_ancestry()) == 0: return 1
    chosen_rule_node = randomness.random_choice(dependencyGraph.get_not_ancestry())
    if full_logs: logging.add_log_text("\t\t [equ_node_rem]: Chosen rule node: " + chosen_rule_node.get_name())
    if randomness.flip_a_coin():
        # ********** Remove a Fact Node ************
        if len(chosen_rule_node.get_fact_nodes()) <= int(params["min_number_of_fact_nodes"]): 
            if full_logs: logging.add_log_text("\t\t [equ_node_rem]: Transformation failed! \u274c")
            return 1
        chosen_rule_node.remove_a_fact_node()
        logging.add_log_text("\t[EQU_NODE_REM]: Removed a fact node from the node [" + chosen_rule_node.get_name() + "]")
    else:
        # ********** Remove a Rule Node ************
        # ********** Check if it is safe to remove this Node *******
        direct_children = chosen_rule_node.get_direct_children()
        for child in direct_children:
            if full_logs: logging.add_log_text("\t\t [equ_node_rem]: Checking the direct child " + child.get_name())
            for level in range(1, child.get_max_edge_level()+1):
                all_vars = list()
                for edge in [edge for edge in child.get_all_incoming_rule_edges() if edge.get_level() == level]:
                    all_vars += [var.get_name() for var in edge.get_join_variables()]
                all_edges = [edge for edge in chosen_rule_node.get_all_outgoing_rule_edges() if edge.get_end_node() == child and edge.get_level() == level]
                vars_in_these_edges = list()
                for edge in all_edges: 
                    vars_in_these_edges += [var.get_name() for var in edge.get_join_variables()]
                for var in vars_in_these_edges:
                    for i, var2 in enumerate(all_vars):
                        if var == var2:
                            all_vars.pop(i)

                # Check if head node is grounded. 
                for var in [i.get_name() for i in child.get_levelled_variable_objects(level).get_vars()]:
                    if var not in all_vars: 
                        if full_logs: logging.add_log_text("\t\t [equ_node_rem]: Transformation failed! \u274c")
                        return 1    # Not safe to remove

                # Check if variables in negative subgoals is grounded.
                all_negative_edges = [edge for edge in child.get_all_incoming_rule_edges() if edge.get_level() == level and edge.get_charge() == "-ve"]
                all_negative_variables = list()
                for edge in all_negative_edges:
                    all_negative_variables += edge.get_join_variables()
                all_negative_variables = [var.get_name() for var in all_negative_variables]
                for var in all_negative_edges: 
                    if var not in all_vars:
                        if full_logs: logging.add_log_text("\t\t [equ_node_rem]: Transformation failed! \u274c")
                        return 1  # Not safe to remove

        # ******** Update graph elements *********
        # Update parentNodes
        for parent_node in [edge.get_start_node() for edge in chosen_rule_node.get_all_incoming_rule_edges()]:
            index = 0
            while(index < len(parent_node.get_all_outgoing_rule_edges())):
                if parent_node.get_all_outgoing_rule_edges()[index].get_end_node().get_name() == chosen_rule_node.get_name():
                    parent_node.get_all_outgoing_rule_edges().pop(index)
                    continue
                index+=1

        # Update childNodes
        for child_node in [edge.get_end_node() for edge in chosen_rule_node.get_all_outgoing_rule_edges()]:
            index = 0
            while(index < len(child_node.get_all_incoming_rule_edges())):
                if child_node.get_all_incoming_rule_edges()[index].get_start_node().get_name() == chosen_rule_node.get_name():
                    child_node.get_all_incoming_rule_edges().pop(index)
                    continue
                index+=1

        # Update dependencyGraph *************
        # If the node was a rule node
        for i, node in enumerate(dependencyGraph.get_all_rule_nodes()):
            if node.get_name() == chosen_rule_node.get_name(): 
                dependencyGraph.get_all_rule_nodes().pop(i)
        # If the node was an empty node
        for i, node in enumerate(dependencyGraph.get_empty_nodes()):
            if node.get_name() == chosen_rule_node.get_name(): 
                dependencyGraph.get_empty_nodes().pop(i)
        # If the node was a complex node
        for i, node in enumerate(dependencyGraph.get_complex_nodes()):
            if node.get_name() == chosen_rule_node.get_name(): 
                dependencyGraph.get_complex_nodes().pop(i)


        # Update ancestry information ************* 
        dependencyGraph.remove_node_from_not_ancestry(chosen_rule_node)

        logging.add_log_text("\t[EQU_NODE_REM]: Removed a rule node [" + chosen_rule_node.get_name() + "]")
        stats.increment_transformation_count("EQU_NODE_REM")


def EQU_EDGE_ADD(dependencyGraph, randomness, params, logging, engine, full_logs, stats):
    """
        For an output node O, an edge can be added at any level L_n from rule node R_1 to rule node R_2 if 
        0) R_1 is any random node in the graph.
        1) R_2 is not in the ancestry of O.  SET 1
        2) R_2 is either at the same stratum as R_1  SET 2 OR not in the ancestry of R_1    SET_3:    
            -> SET_1 ∩ {SET_2 U SET_3}
        TODO: At the moment we can only add positive edges. Negative edges might not be so simple. i am not in the mood right now.
    """
    if len(dependencyGraph.get_not_ancestry()) == 0: return 1

    R_1 = randomness.random_choice(dependencyGraph.get_all_rule_nodes() + dependencyGraph.get_parsed_graph().get_parsed_nodes() + dependencyGraph.get_empty_nodes() + dependencyGraph.get_complex_nodes())
    # Set of nodes not in the ancestry of O [SET 1]
    SET_1 = dependencyGraph.get_not_ancestry()
    # Set of nodes not in the ancestry of R_1 [SET 2]
    ancestry_of_R_1 = find_all_rule_ancestors(R_1, [])
    SET_2 = [node for node in dependencyGraph.get_all_rule_nodes() if node not in ancestry_of_R_1]
    # Set of nodes at the same stratum as R_1 [SET 3]
    for node in dependencyGraph.get_all_rule_nodes(): node.set_stratum("NONE") # Refresh stratum info in the graph if any
    R_1.set_stratum(0)
    compute_strata_property_values(R_1, [])    
    SET_3 = [node for node in dependencyGraph.get_all_rule_nodes() if node.get_stratum() == 0]
    accpetble_values_for_R_2 = [node for node in SET_3 + SET_2 if node in SET_1]
    if len(accpetble_values_for_R_2) == 0: return 1
    R_2 = randomness.random_choice(accpetble_values_for_R_2)
    
    # Check if adding and edge from R_1 to R_2 will not violate any of inlining laws in souffle.
    if engine == "souffle":
        if introduces_a_cycle_with_every_node_inlined(R_2, R_1): 
            return 1
        
    # Determine level of the new edge. 
    level = randomness.get_random_integer(1, R_2.get_max_edge_level())
    new_edge = Edge(start=R_1, end=R_2, charge="+ve", level=level)

    # ***** Adding an edge from R1 to a node which did not have an incoming edge before
    if len(R_2.get_all_incoming_rule_edges()) == 0:
        # Check if all the types of R_2 are present in R_1. 
        var_types_in_R_2 = [var.get_type() for var in R_2.get_variables()]
        var_types_in_R_1 = [var.get_type() for var in R_1.get_variables()]
        for var in var_types_in_R_2: 
            if var not in var_types_in_R_1: return 1
        R_1.add_outgoing_rule_edge(new_edge)
        R_2.add_incoming_rule_edge(new_edge)
        new_edge.set_tranformed_flag_to_true()
        R_2.generate_joins()
        return 0

    # **** Add an edge from R_1 to R_2 ****
    R_1.add_outgoing_rule_edge(new_edge)
    R_2.add_incoming_rule_edge(new_edge)
    new_edge.set_tranformed_flag_to_true()

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
    logging.add_log_text("\t[EQU_EDGE_ADD]: Added an edge from " + R_1.get_name() + " to " + R_2.get_name())
    stats.increment_transformation_count("EQU_EDGE_ADD")


def EQU_EDGE_REM(dependencyGraph, randomness, logging, engine, full_logs, stats):
    """
        This can modfiy complex nodes. R_2 should not be a complex node. 
    """

    if full_logs: logging.add_log_text("\n\t\t >>> [equ_edge_rem]: Nodes not in ancestry of the output node " + str([i.get_name() for i in dependencyGraph.get_not_ancestry()]))
    if len(dependencyGraph.get_not_ancestry()) == 0: return 1
    
    # R_2 should not be a complex node
    nodes_not_in_ancestory_with_incoming_edges = [node for node in dependencyGraph.get_not_ancestry() if len(node.get_all_incoming_rule_edges()) != 0 and node not in dependencyGraph.get_complex_nodes()]
    if len(nodes_not_in_ancestory_with_incoming_edges) == 0: return 1
    # Pick an R_2 which is not in the ancestory of O and not a complex node
    R_2 = randomness.random_choice(nodes_not_in_ancestory_with_incoming_edges)
    R_1 = randomness.random_choice([edge for edge in R_2.get_all_incoming_rule_edges()]).get_start_node()
    edge = randomness.random_choice([edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_start_node() == R_1])

    if full_logs: logging.add_log_text("\t\t >>> [equ_edge_rem]: Trying to remove an edge from " + R_1.get_name() + " to " + R_2.get_name())
    if full_logs: logging.add_log_text("\t\t >>> [equ_edge_rem]: Join variables of the edge we are trying to remove: " + str([i.get_name() for i in edge.get_join_variables()]))

    # ****** Check if this edge can be safely removed *******
    if not edge.check_edge_removal_safety(): return 1 # Edge not safe to remove

    if full_logs: logging.add_log_text("\t\t >>> [equ_edge_rem]: Edge is safe to remove")
    # ****** Update R_1 *******
    for i, e in enumerate(R_1.get_all_outgoing_rule_edges()): 
        if e == edge: R_1.get_all_outgoing_rule_edges().pop(i)

    if full_logs: logging.add_log_text("\t\t >>> [equ_edge_rem]: Number of incoming rule edges for the node " + R_2.get_name() + " = " + str(len(R_2.get_all_incoming_rule_edges())))
    
    # ****** Update R_2 *******
    for i, e in enumerate(R_2.get_all_incoming_rule_edges()): 
        if e == edge: R_2.get_all_incoming_rule_edges().pop(i)

    if full_logs: logging.add_log_text("\t\t >>> [equ_edge_rem]: Number of incoming rule edges for the node " + R_2.get_name() + " = " + str(len(R_2.get_all_incoming_rule_edges())))
    logging.add_log_text("\t[EQU_EDGE_REM]: Removed an edge from " + R_1.get_name() + " to " + R_2.get_name())
    stats.increment_transformation_count("EQU_EDGE_REM")


def EQU_LEVEL_ADD(dependencyGraph, randomness, logging, engine, full_logs, stats):
    """
        Adding complimentary edges
        Add a level without changing the result
        A(a) :- B(a).
            |
            |
            |
            V
        A(a) :- B(a).
        A(a) :- C(a), !C(a).
        A should not be in the ancestry of C.
    """

    # Pick any node in the graph.
    R_2 = randomness.random_choice(dependencyGraph.get_all_rule_nodes())    
    # Pick a node in R_1, such that R_1 is not a desendant of R_2.
    descendants_of_R_2 = list()
    find_all_descendants(R_2, [], descendants_of_R_2)
    all_nodes = dependencyGraph.get_all_rule_nodes() + dependencyGraph.get_parsed_graph().get_parsed_nodes() + dependencyGraph.get_empty_nodes() + dependencyGraph.get_complex_nodes()
    options_for_R_1 = [i for i in all_nodes if i not in descendants_of_R_2]
    if len(options_for_R_1) == 0: return
    R_1 = randomness.random_choice(options_for_R_1)

    if engine == "souffle":
        if introduces_a_cycle_with_every_node_inlined(R_2, R_1): 
            return 1
        if R_1.get_inline_flag():
            return 1


    # Determine level of the new edge.
    edge_level = 1
    if len(R_2.get_all_incoming_rule_edges()) == 0: pass
    else: edge_level = R_2.get_max_edge_level() + 1
    
    # Check if this rule makes sense or not
    var_types_in_R_2 = [var.get_type() for var in R_2.get_variables()]
    var_types_in_R_1 = [var.get_type() for var in R_1.get_variables()]
    for var in var_types_in_R_2: 
        if var not in var_types_in_R_1: return 1

    # Compute join variables for edge_1 and edge_2.
    edge_join_variables = list()
    new_variables_for_R_2 = list()
    var_generator = VariableGenerator()
    edge_1 = Edge(start=R_1, end=R_2, charge="+ve", level=edge_level)
    edge_2 = Edge(start=R_1, end=R_2, charge="-ve", level=edge_level)
    for var in R_1.get_variables(): 
        new_variable = Variable(name=var_generator.generate_new_lower_case_variabe(), vtype=var.get_type(), value=None)
        edge_join_variables.append(new_variable)
    edge_1.set_join_variables(edge_join_variables)
    edge_2.set_join_variables(edge_join_variables)

    for var in R_2.get_variables():
        var_choices = [v for v in edge_join_variables if v.get_type() == var.get_type()]
        chosen_var = deepcopy(randomness.random_choice(var_choices))
        new_variables_for_R_2.append(chosen_var)
    R_2.levelled_variable_objects.append(LeveledVariables(level=edge_level, vars=new_variables_for_R_2))

    R_1.add_outgoing_rule_edge(edge_1)
    R_1.add_outgoing_rule_edge(edge_2)
    R_2.add_incoming_rule_edge(edge_1)
    R_2.add_incoming_rule_edge(edge_2)

    edge_1.set_tranformed_flag_to_true()
    edge_2.set_tranformed_flag_to_true()

    # If R_2 is in the ancestry of the outpue node, R_1 is now in the unknown ancestry.
    # In this case, remove R_1 from the not acnestry 
    if R_2 in dependencyGraph.get_positive_ancestry() + dependencyGraph.get_negative_ancestry() + dependencyGraph.get_unknown_ancestry():
        if full_logs: dependencyGraph.log_graph_stats(logging)
        if full_logs: logging.add_log_text("\t\t [equ_level_add]: Moving " + R_1.get_name() + " to UNKNOWN ancestry " + R_2.get_name() + " is in the ancestry")
        dependencyGraph.append_unknown_ancestry(R_1)
        dependencyGraph.remove_node_from_not_ancestry(R_1) # Remove R_1 from the not_ancestry set
        dependencyGraph.remove_node_from_positive_ancestry(R_1)  # Remove R_1 from the positive ancestry set
        dependencyGraph.remove_node_from_negative_ancestry(R_1)  # Remove R_1 from the negative ancestry set
        if full_logs: dependencyGraph.log_graph_stats(logging)

    logging.add_log_text("\t[EQU_LEVEL_ADD]: Added a new level in the relation [" + R_2.get_name() + "] by adding complimentarty edges from [" + R_1.get_name() + "]")
    stats.increment_transformation_count("EQU_LEVEL_ADD")


def EQU_LEVEL_ADD_2(dependencyGraph, randomness, logging, engine, full_logs, stats):
    """
        Adding a self edge
        A(a) :- B(a).
            |
            |
            |
            V
        A(a) :- B(a).
        A(a) :- A(a).
    """
    R_2 = randomness.random_choice(dependencyGraph.get_all_rule_nodes() + dependencyGraph.get_parsed_graph().get_parsed_nodes() + dependencyGraph.get_empty_nodes() + dependencyGraph.get_complex_nodes())
    edge_level = 1
    if len(R_2.get_all_incoming_rule_edges()) == 0: pass 
    else: edge_level = R_2.get_max_edge_level() + 1

    if engine == "souffle":
        if introduces_a_cycle_with_every_node_inlined(R_2, R_2): 
            return 1

    # Compute join variables for edge.
    edge_join_variables = list()
    var_generator = VariableGenerator()
    edge = Edge(start=R_2, end=R_2, charge="+ve", level=edge_level)
    for var in R_2.get_variables(): 
        new_variable = Variable(name=var_generator.generate_new_lower_case_variabe(), vtype=var.get_type(), value=None)
        edge_join_variables.append(new_variable)
    edge.set_join_variables(edge_join_variables)
    R_2.levelled_variable_objects.append(LeveledVariables(level=edge_level, vars=edge_join_variables))
    R_2.add_outgoing_rule_edge(edge)
    R_2.add_incoming_rule_edge(edge)
    edge.set_tranformed_flag_to_true()
    logging.add_log_text("\t[EQU_LEVEL_ADD_2]: Added a self edge at a different level for [" + R_2.get_name() + "]")
    stats.increment_transformation_count("EQU_LEVEL_ADD_2")


def EQU_COLLAPSE_EDGE(dependencyGraph, randomness, logging, engine, full_logs, stats):
    """
        Collapses an edge. Basically substitutes a rule where it is being used.

        C(a) :- A(a), B(a).
        D(a) :- Q(b), C(a).
             |
             |
             V
        C(a) :- A(a), B(a).
        D(c) :- Q(b), A(c), B(c).


        There are 2 things we need to be careful about here. 
            -> R_1 can only have one level. It is not yet clear how we can handle more than 1 level.
            -> We only substitute on edge from R_1 to R_2
            -> We need to carefully substitute the rule in R_2. By correctly mapping the variables.


        -----------------------------------
        ****** Interesting problem: ******
        -----------------------------------

        Consider the following program:
            a__(99, 65).
            a__(3, 57).
            a__(5, 74).
            b__("er").
            b__("ta").
            b__("kx").
            c__(93).
            c__(80).
            c__(48).
            e__(53, "ws").
            e__(86, "bi").


            c__(a) :- a__(d, b), a__(c, a).
            e__(b, a) :- b__(a), c__(b).

        If we substitute c__ in the last rule to get: 
            c__(a) :- a__(d, b), a__(c, a).
            e__(b, a) :- b__(a), a__(_, _), a__(_, b).

        The result changes. 
        c__ already has some extra elements in it that are not just computed with the rule " a__(d, b), a__(c, a)." 
        These extra elements are given as facts.
        A simple workaround to avoid this situation is to choose an R_1 that has no incoming facts nodes. That should work fine. 

        PROBLEM: This transformation is not playing well with contracting and expanding transformations. Specifically when we first use CON_ADD_SELF_EDGE and then contract.
    """

    # Pick a node with only level and no incoming fact nodes
    nodes_with_one_level = [node for node in dependencyGraph.get_all_rule_nodes() if node.get_max_edge_level() == 1 and len(node.get_fact_nodes()) == 0]
    if len(nodes_with_one_level) == 0: return 1
    R_1 = randomness.random_choice(nodes_with_one_level)
    logging.add_log_text("\t[EQU_COLLAPSE_EDGE]: Picking R1: " + R_1.get_name())
    logging.add_log_text("              R1 has " + str(len(R_1.get_all_incoming_rule_edges())) + " subgoals in its body at this point")
    logging.dump_log_file()
    if len(R_1.get_all_incoming_rule_edges()) == 0: 
        logging.add_log_text("              Transformation failed \u274c")
        logging.dump_log_file()
        return 1
    # Pick one positive child of R_1. We call it R_2 TODO: What about negative?
    positive_child_edges = [edge for edge in R_1.get_all_outgoing_rule_edges() if edge.get_charge() == "+ve"]
    if len(positive_child_edges) == 0: 
        logging.add_log_text("              Transformation failed \u274c")
        logging.dump_log_file()
        return 1
    postive_edge = randomness.random_choice(positive_child_edges)
    positive_child = postive_edge.get_end_node()
    if positive_child == R_1: 
        logging.add_log_text("              Chosen edge is a self edge.")
        logging.add_log_text("              Transformation failed \u274c")
        logging.dump_log_file()
        return 1
    logging.add_log_text("              Picked positive child " + positive_child.get_name())
    logging.dump_log_file()
    # Variable mapping
    variable_domain = deepcopy(R_1.get_levelled_variable_objects(level=1).get_vars()) # A list of variable objects. 
    variable_range = deepcopy(postive_edge.get_join_variables())       # A list of variable objects
    mapping = dict()
    for i, var in enumerate([i.get_name() for i in variable_domain]):
        if var in mapping.keys(): return 1 # We can't map an already mapped variable to another thing. 
        mapping[var] = variable_range[i].get_name()
    # Copy incoming edges of R_1 to R_2.
    random_string = randomness.get_random_alpha_string(4)
    for edge in R_1.get_all_incoming_rule_edges():
        new_edge = Edge(edge.get_start_node(), positive_child, edge.get_charge(), postive_edge.get_level()) # This edge should have level 1
        new_edge.set_tranformed_flag_to_true()
        new_vars = list()
        for var in edge.get_join_variables():
            if var.get_name() in mapping.keys():
                new_vars.append(Variable(mapping[var.get_name()], var.get_type(), None))
            else:
                if var.get_name() == "_":
                    new_var_name = "_"
                else:
                    new_var_name = var.get_name() + random_string
                new_vars.append(Variable(new_var_name, var.get_type(), None))
        new_edge.set_join_variables(new_vars)
        # Update the dependency graph. Add the new edges from the parents of R_1 to positive_child
        edge.get_start_node().add_outgoing_rule_edge(new_edge)
        positive_child.add_incoming_rule_edge(new_edge)
    logging.add_log_text("              Incoming edges in " + positive_child.get_name() + " BEFORE removing = " + str(len(positive_child.get_all_incoming_rule_edges())))
    # Udate the data dependency graph.  
    # > Delete the edge from R_1 to positive_child
    for i, e in enumerate(R_1.get_all_outgoing_rule_edges()):
        if e == postive_edge: R_1.get_all_outgoing_rule_edges().pop(i)
    for i, e in enumerate(positive_child.get_all_incoming_rule_edges()):
        if e == postive_edge: positive_child.get_all_incoming_rule_edges().pop(i)
    logging.add_log_text("              Incoming edges in " + positive_child.get_name() + " AFTER removing = " + str(len(positive_child.get_all_incoming_rule_edges())))
    logging.add_log_text("              Transformation successful  \u2705")
    stats.increment_transformation_count("EQU_COLLAPSE_EDGE")


def EQU_FACT_INLINE(dependencyGraph, randomness, logging, runTimeInfo, engine, full_logs, stats):
    
    full_log_text = ""

    def node_with_only_primitive_type(node):
        for var in node.get_variables():
            if var.get_type() != "integer" and var.get_type() != "string" and var.get_type() != "i32" and var.get_type() != "String":
                return False
        return True


    allowed_nodes = list()
    all_nodes = dependencyGraph.get_all_rule_nodes() + dependencyGraph.get_parsed_graph().get_parsed_nodes() + dependencyGraph.get_empty_nodes() + dependencyGraph.get_complex_nodes()
    nodes_with_non_empty_output = [i for i in all_nodes if i.get_name() in [j.get_name() for j in runTimeInfo.get_nodes_with_non_empty_output()]]
    nodes_with_artiy_greater_than_zero = [i for i in nodes_with_non_empty_output if len(i.get_variables()) > 0]
    nodes_that_are_already_not_inlined = [i for i in nodes_with_artiy_greater_than_zero if not i.return_factInlined_status()]
    full_log_text += "\n\t\t[equ_fact_inline]: Number of nodes with non-empty output: " + str(len(nodes_with_non_empty_output))
    full_log_text += "\n\t\t[equ_fact_inline]: Number of non-empty nodes with artiy greater than zero: " + str(len(nodes_with_artiy_greater_than_zero))
    full_log_text += "\n\t\t[equ_fact_inline]: Number of non-empty nodes with artiy greater than zero that are already not inlined: " + str(len(nodes_that_are_already_not_inlined))
    # All the variables in the node should be of primitive types
    for node in nodes_that_are_already_not_inlined:
        if node_with_only_primitive_type(node):
            allowed_nodes.append(node)    
    if len(allowed_nodes) == 0: 
        full_log_text += "\n\t\t[equ_fact_inline]: No nodes available to inline. Transformation failed \u274c"
        if full_logs: logging.add_log_text(full_log_text)
        return 1
    chosen_rule_node = randomness.random_choice(allowed_nodes)
    number_of_facts_inlined = runTimeInfo.generate_facts_from_output(chosen_rule_node)
    chosen_rule_node.set_factInlined_to_True()
    logging.add_log_text("\t[EQU_FACT_INLINE]: Inlined " + str(number_of_facts_inlined)  + " number facts for the relation [" + chosen_rule_node.get_name() + "]")
    
    # ********* Remove all the edges in the node **************
    for edge in chosen_rule_node.get_all_incoming_rule_edges():
        for i, e in enumerate(edge.get_start_node().get_all_outgoing_rule_edges()):
            if e == edge: 
                edge.get_start_node().get_all_outgoing_rule_edges().pop(i)
                break
        del edge

    # Remove all incoming rule edges
    chosen_rule_node.get_all_incoming_rule_edges().clear()
    # Remove all levelled variable objects
    chosen_rule_node.get_all_levelled_variable_objects().clear()
    stats.increment_transformation_count("EQU_FACT_INLINE")
