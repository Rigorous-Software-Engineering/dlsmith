from copy import deepcopy
import os
from dlsmith.utils.file_operations import create_file
from dlsmith.dataDependencyGraph.ruleNode import RuleNode
from termcolor import colored

def export_graph_as_dot(dependencyGraph, graph_type, path, transformation_number=0):
    """
        graph_type: original or tranformed (needed for the file_name)
    """
    # All rules nodes should be there
    text_to_export = "digraph {\n"

    # Add rule nodes:
    for rule_node in dependencyGraph.get_all_rule_nodes():
        if rule_node.get_name() == dependencyGraph.get_output_node().get_name():
            text_to_export += "\t" + rule_node.get_name()  + "[color=red];\n"
        elif rule_node.get_transformed_flag():
            text_to_export += "\t" + rule_node.get_name() + "[color=blue];\n"
        else:
            text_to_export += "\t" + rule_node.get_name() + ";\n"
        
    # Add edges: 
    for rule_node in dependencyGraph.get_all_rule_nodes():
        for incoming_edge in rule_node.get_all_incoming_rule_edges():
            text_to_export += "\t" + incoming_edge.get_start_node().get_name() + " -> " + incoming_edge.get_end_node().get_name()
            if incoming_edge.get_charge() == "-ve": text_to_export += '[color=red, penwidth=1.5, label="<' + str(incoming_edge.get_level()) + ', ' + incoming_edge.get_charge() + '>"];\n'
            elif incoming_edge.get_transformed_flag(): text_to_export += '[color=blue, penwidth=1.5, label="<' + str(incoming_edge.get_level()) + ', ' + incoming_edge.get_charge() + '>"];\n'
            else: text_to_export += '[penwidth=1.5, label="<' + str(incoming_edge.get_level()) + ', ' + incoming_edge.get_charge() +'>"];\n'

    full_program = "" + text_to_export
    # Add facts:
    """
    for rule_node in dependencyGraph.get_all_rule_nodes():
        for fact_node in rule_node.get_fact_nodes():
            if fact_node.get_transformed_flag():
                full_program += '\t"' + fact_node.get_value_string() + '" -> ' + rule_node.get_name() + '[color=blue];\n'
                full_program += '\t"' + fact_node.get_value_string() + '"[color=blue];\n'
            else:
                full_program += '\t"' + fact_node.get_value_string() + '" -> ' + rule_node.get_name() + '[color=green];\n'
                full_program += '\t"' + fact_node.get_value_string() + '"[color=green];\n'
    """

    text_to_export += "}"
    full_program += "}"
    program_path = ""
    full_program_path = ""
    if graph_type == "orig": 
        program_path = os.path.join(path, "original_program.dot")
        full_program_path = os.path.join(path, "full_original_program.dot")
    if graph_type == "trans": 
        program_path = os.path.join(path, "transformed_program_" + str(transformation_number) + ".dot")
        full_program_path = os.path.join(path, "full_transformed_program_" + str(transformation_number) + ".dot")

    #create_file(text_to_export, program_path)
    create_file(full_program, full_program_path)
    dependencyGraph.set_path_to_dot_file(full_program_path)

"""
    Does this rule node has a rule node parent?
"""
def has_rule_parent(rule_node):
    for incoming_edge in rule_node.get_all_incoming_rule_edges():
        if isinstance(incoming_edge.get_start_node(), RuleNode):
            return True
    return False


"""
    Given a start node, find all the rule nodes from which, data flows into this node.
    DFS traversal
    Should take care of cycles as well
"""
def find_all_rule_ancestors(start_node, explored_nodes):
    incoming_edges = start_node.get_all_incoming_rule_edges()
    nodes_to_explore = [edge.get_start_node() for edge in incoming_edges if edge.get_start_node() not in explored_nodes]
    explored_nodes.append(start_node)   
    for node in nodes_to_explore:
        find_all_rule_ancestors(node, explored_nodes)
    return explored_nodes

"""
    Returns rule nodes that are not in the ancestory of start_node
"""
def find_all_rules_not_in_ancestors(start_node, dependencyGraph):
    return [node for node in dependencyGraph.get_all_rule_nodes() if node not in find_all_rule_ancestors(start_node, [])]


"""
    Return all positive descendants of start_node in a cyclic data dependency graph
"""
def find_all_positive_descendants(start_node, explored_nodes, pos_des):
    explored_nodes.append(start_node)
    if start_node not in pos_des: pos_des.append(start_node)
    outgoing_edges = [edge for edge in start_node.get_all_outgoing_rule_edges() if edge.get_charge() == "+ve"]
    nodes_to_explore = [edge.get_end_node() for edge in outgoing_edges if edge.get_end_node() not in explored_nodes]
    for node in nodes_to_explore:
        find_all_positive_descendants(node, explored_nodes, pos_des)
    explored_nodes.pop()


"""
    Return all descendants of start_node in a cyclic data dependency graph
"""
def find_all_descendants(start_node, explored_nodes, des):
    explored_nodes.append(start_node)
    if start_node not in des: des.append(start_node)
    outgoing_edges = [edge for edge in start_node.get_all_outgoing_rule_edges()]
    nodes_to_explore = [edge.get_end_node() for edge in outgoing_edges if edge.get_end_node() not in explored_nodes]
    for node in nodes_to_explore:
        find_all_descendants(node, explored_nodes, des)
    explored_nodes.pop()

""" 
    Given an output node, compute the value for each property key for each node in the dependency graph DFS.
    CAUTION: Only call this for an acyclic dependencyGraph. This method might not terminate for cyclic graphs.

def compute_property_values_wrt_output(output_node):
    def compute_charge(current_node_charge, edge_charge, parent_node_charge):
        if parent_node_charge == "UNKNOWN": return "UNKNOWN"
        if current_node_charge == "UNKNOWN": return "UNKNOWN"
        charge_being_propogate_up = ""
        if current_node_charge == "-ve" and edge_charge == "-ve": charge_being_propogate_up = "+ve"
        if current_node_charge == "-ve" and edge_charge == "+ve": charge_being_propogate_up = "-ve"
        if current_node_charge == "+ve" and edge_charge == "-ve": charge_being_propogate_up = "-ve"
        if current_node_charge == "+ve" and edge_charge == "+ve": charge_being_propogate_up = "+ve"
        if parent_node_charge == "NONE" and charge_being_propogate_up == "+ve": return "+ve"
        if parent_node_charge == "NONE" and charge_being_propogate_up == "-ve": return "-ve"
        if parent_node_charge == "+ve" and charge_being_propogate_up == "+ve": return "+ve"
        if parent_node_charge == "+ve" and charge_being_propogate_up == "-ve": return "UNKNOWN"
        if parent_node_charge == "-ve" and charge_being_propogate_up == "+ve": return "UNKNOWN"
        if parent_node_charge == "-ve" and charge_being_propogate_up == "-ve": return "-ve"


    incoming_edges = output_node.get_all_incoming_rule_edges()
    for edge in incoming_edges:
        parent_node = edge.get_start_node()
        # Compute ancestry for the parent
        parent_node.set_ancestry( compute_charge(output_node.get_ancestry(), edge.get_charge(), parent_node.get_ancestry()) )
        compute_property_values_wrt_output(parent_node)
"""



"""
    Given an output node, compute the charge property value for each node in the dependency graph
    Depth first search
    Cycles should not be a problem
"""
def compute_node_charge_property_value(start_node, explored_nodes):
    def compute_charge(current_node_charge, edge_charge, parent_node_charge):
        if parent_node_charge == "UNKNOWN": return "UNKNOWN"
        if current_node_charge == "UNKNOWN": return "UNKNOWN"
        charge_being_propogate_up = ""
        if current_node_charge == "-ve" and edge_charge == "-ve": charge_being_propogate_up = "+ve"
        if current_node_charge == "-ve" and edge_charge == "+ve": charge_being_propogate_up = "-ve"
        if current_node_charge == "+ve" and edge_charge == "-ve": charge_being_propogate_up = "-ve"
        if current_node_charge == "+ve" and edge_charge == "+ve": charge_being_propogate_up = "+ve"
        if parent_node_charge == "NONE" and charge_being_propogate_up == "+ve": return "+ve"
        if parent_node_charge == "NONE" and charge_being_propogate_up == "-ve": return "-ve"
        if parent_node_charge == "+ve" and charge_being_propogate_up == "+ve": return "+ve"
        if parent_node_charge == "+ve" and charge_being_propogate_up == "-ve": return "UNKNOWN"
        if parent_node_charge == "-ve" and charge_being_propogate_up == "+ve": return "UNKNOWN"
        if parent_node_charge == "-ve" and charge_being_propogate_up == "-ve": return "-ve"

    explored_nodes.append(start_node)
    incoming_edges = start_node.get_all_incoming_rule_edges()
    for edge in incoming_edges:
        parent_node = edge.get_start_node()
        if parent_node == start_node: continue
        if parent_node in explored_nodes: continue
        parent_node.set_ancestry( compute_charge(start_node.get_ancestry(), edge.get_charge(), parent_node.get_ancestry()) )
        compute_node_charge_property_value(parent_node, explored_nodes)
    explored_nodes.pop()
    


"""
    DFS: Computes stratum property values directly on the graph. 

    Some important notes: 
    We will never have an edge from a node of a higher straum to a node with an lower stratum. 
    It is therefore ok if we keep a list of explored_nodes. If we reach back to a node which is in 
    explored_nodes, we can skip this node.

    Algo: 
    Between two nodes get all the edges. If there is a negative edge, then increase the 

"""
def compute_strata_property_values(start_node, explored_nodes):
    direct_parents = start_node.get_direct_parents()
    explored_nodes.append(start_node)
    for node in direct_parents: 
        if node == start_node: continue
        if node in explored_nodes: continue
        # Get all edges between start_node and node. 
        all_edges = [edge for edge in start_node.get_all_incoming_rule_edges() if edge.get_start_node() == node]
        contains_negative_edge=False
        for edge in all_edges:
            if edge.get_charge() == "-ve": 
                contains_negative_edge = True
                break
        if node.get_stratum() != "NONE" and node.get_stratum() > start_node.get_stratum(): continue
        if contains_negative_edge: node.set_stratum(start_node.get_stratum() + 1) # -ve edge
        else: node.set_stratum(start_node.get_stratum()) # +ve edge
        compute_strata_property_values(node, explored_nodes)
    explored_nodes.pop()

"""
    Same algorithm as compute_strata_property_values() but for desendants.
"""
def compute_strata_property_values_for_descendants(start_node, explored_nodes):
    direct_children = start_node.get_direct_children()
    explored_nodes.append(start_node)
    for node in direct_children: 
        if node == start_node: continue
        if node in explored_nodes: continue
        # Get all edges between start_node and node. 
        all_edges = [edge for edge in start_node.get_all_outgoing_rule_edges() if edge.get_end_node() == node]
        contains_negative_edge=False
        for edge in all_edges:
            if edge.get_charge() == "-ve": 
                contains_negative_edge = True
                break
        if node.get_stratum() != "NONE" and node.get_stratum() < start_node.get_stratum(): continue
        if contains_negative_edge: node.set_stratum(start_node.get_stratum() - 1) # -ve edge
        else: node.set_stratum(start_node.get_stratum()) # +ve edge
        compute_strata_property_values_for_descendants(node, explored_nodes)
    explored_nodes.pop()


"""
    Return all paths from start_node till end_node.
"""
def return_all_paths(start_node, end_node):
    class TreeNode(object):
        def __init__(self, rule_node):
            self.rule_node = rule_node
            self.children = []
            self.ancestry = []  # a bunch of rule nodes
        def add_child(self, child):
            self.children.append(child)
        def get_rule_node(self):
            return self.rule_node
        def get_children(self):
            return self.children
        def get_ancestry(self):
            return self.ancestry
        def set_ancestry(self, ancestry):
            self.ancestry = ancestry

    def generate_tree(tree_node):
        #print("node:  " + tree_node.get_rule_node().get_name() + "     Children: " + str([i.get_name() for i in tree_node.get_rule_node().get_direct_children()]))
        for child in tree_node.get_rule_node().get_direct_children():
            #print("\tExpoloring child: " + child.get_name())
            if child == start_node:
                continue
            if child in tree_node.get_ancestry():
                continue
            new_child_tree_node = TreeNode(child)
            new_child_tree_node.set_ancestry( tree_node.get_ancestry() + [tree_node.get_rule_node()])
            tree_node.add_child(new_child_tree_node)
            if child != end_node:
                generate_tree(new_child_tree_node)

    def search_tree(start_tree_node, path_so_far):    
        path_so_far_cpy = deepcopy(path_so_far)
        path_so_far_cpy.append(start_tree_node.get_rule_node())
        for tree_node in start_tree_node.get_children():
            if tree_node.get_rule_node() == end_node:
                all_paths.append(path_so_far_cpy + [end_node])
            else:
                search_tree(tree_node, path_so_far_cpy)

    tree_root_node = TreeNode(start_node)
    generate_tree(tree_root_node)
    all_paths = []
    search_tree(tree_root_node, [])
    return all_paths



"""
    WARNING: This will only work if outgoing edges are properly added 
    If the start_node is not in the ancestry of the end_node then no cycle will be introduced by adding an edge from start_node -> end_node. 
"""
def introduces_a_cycle_with_every_node_inlined(start_node, end_node):
    if start_node == end_node: 
        if start_node.get_inline_flag():
            return True
        return False

    #print("")
    # First check if you can reach start_node from end_node. 
    #print("Ancestors of node " + end_node.get_name() + " = " + str([i.get_name() for i in find_all_rule_ancestors(end_node, [])]))
    if start_node not in find_all_rule_ancestors(end_node, []):
        return False
    else:
        # Find all paths between start_node and end_node
        all_paths = return_all_paths(start_node, end_node)
        #print("Number of paths from " + start_node.get_name() + " to " + end_node.get_name() + " = " + str(len(all_paths)))
        for path in all_paths:
            #print("")
            #print("Checking the path: " + str([i.get_name() for i in path]))
            inline_values = [i.get_inline_flag() for i in path]
            #print(str(inline_values))
            if False not in inline_values: return True

    return False


