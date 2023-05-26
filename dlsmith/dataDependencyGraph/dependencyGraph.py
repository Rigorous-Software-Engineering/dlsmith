
from termcolor import colored
from dlsmith.dataDependencyGraph.graphUtils import compute_node_charge_property_value
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.utils.variableGenerator import VariableGenerator
from dlsmith.utils.constantGenerator import ConstantGenerator
from dlsmith.dataDependencyGraph.ruleNode import RuleNode
from dlsmith.dataDependencyGraph.edge import Edge
from copy import deepcopy


class DataDependencyGraph(object):

    def __init__(self, params, randomness, logging, parsed_graph, full_logs):
        self.params = params
        self.randomness = randomness
        self.logging = logging
        self.parsed_graph = parsed_graph
        self.full_logs = full_logs
        self.all_rule_nodes = list()    # List of type RuleNode
        self.all_fact_nodes = list()    # List of type FactNode
        self.output_node = None     # Type: RuleNode
        self.root_nodes = list()    # A list of nodes. We might not always have these
        self.path_to_dot_file = None
        self.empty_nodes = list()
        self.complex_nodes = list()

        # External Parameters
        self.number_of_layers = self.randomness.get_random_integer(1, self.params["max_number_of_layers_in_the_graph"])

        # Utils
        self.variableGenerator = VariableGenerator()
        self.constantGenerator = ConstantGenerator(param=self.params, randomness=self.randomness)

        # Graph properties
        self.positive_ancestry = list()
        self.negative_ancestry = list()
        self.not_in_ancestry = list()
        self.unknown_ancestry = list()

    def clear_ancestry_information(self):
        self.positive_ancestry.clear()
        self.negative_ancestry.clear()
        self.not_in_ancestry.clear()
        self.unknown_ancestry.clear()

    def append_positive_ancestry(self, node):
        self.positive_ancestry.append(node)
    def append_negative_ancestry(self, node):
        self.negative_ancestry.append(node)
    def append_not_in_ancestry(self, node):
        self.not_in_ancestry.append(node)
    def append_unknown_ancestry(self, node):
        self.unknown_ancestry.append(node)

    def append_empty_nodes(self, node):
        self.empty_nodes.append(node)
    def get_empty_nodes(self):
        return self.empty_nodes
    def append_complex_node(self, node):
        self.complex_nodes.append(node)
    def get_complex_nodes(self):
        return self.complex_nodes
    def get_not_ancestry(self):
        return self.not_in_ancestry
    def get_positive_ancestry(self):
        return self.positive_ancestry
    def get_negative_ancestry(self):
        return self.negative_ancestry
    def get_unknown_ancestry(self):
        return self.unknown_ancestry

    def remove_node_from_not_ancestry(self, node_to_remove):
        self.not_in_ancestry = [i for i in self.not_in_ancestry if i != node_to_remove]

    def remove_node_from_positive_ancestry(self, node_to_remove):
        self.positive_ancestry = [i for i in self.positive_ancestry if i != node_to_remove]

    def remove_node_from_negative_ancestry(self, node_to_remove):
        self.negative_ancestry = [i for i in self.negative_ancestry if i != node_to_remove]

    def retrieve_ancestry_information(self):
        for node in self.all_rule_nodes + self.empty_nodes + self.complex_nodes:
            if node.get_ancestry() == "+ve": self.positive_ancestry.append(node)
            if node.get_ancestry() == "-ve": self.negative_ancestry.append(node)
            if node.get_ancestry() == "NONE": self.not_in_ancestry.append(node)
            if node.get_ancestry() == "UNKNOWN": self.unknown_ancestry.append(node)


    def get_all_rule_nodes(self):
        return self.all_rule_nodes
    def get_all_fact_nodes(self):
        return self.all_fact_nodes
    def get_output_node(self):
        return self.output_node
    def set_path_to_dot_file(self, new_path):
        self.path_to_dot_file = new_path
    def get_path_to_dot_file(self):
        return self.path_to_dot_file
    def get_parsed_graph(self):
        return self.parsed_graph
    
    def append_R(self):
        """
            DDlog kay nakhray. This is a bit hacky :/
        """
        for node in self.all_rule_nodes:
            if not node.get_R_appended():
                node.set_name("R" + node.get_name())
                node.set_R_appended()

    def generate_a_singular_rule_node(self):
        """
            Adds a rule nodes. Does not connect it with anything. 
            Always add it in layer 0.
        """
        rule_node = RuleNode(
                                name=self.variableGenerator.generate_new_lower_case_variabe(self.parsed_graph.get_parsed_node_names()) + "__", 
                                depth=0,
                                params=self.params,
                                randomness=self.randomness,
                                constantGenerator=self.constantGenerator,
                            )
        rule_node.generate_node_variables()
        self.all_rule_nodes.append(rule_node)
        return rule_node


    def generateACyclicGraph(self):
        """
            Generate an acyclic random graph. We use a layered approach to ensure there are no cycles in the graph.
        """
        self.logging.add_log_text("[generateACyclicGraph] Commence graph generation")
        for layer in range(self.number_of_layers):
            number_of_nodes = self.randomness.get_random_integer(1, self.params["max_number_of_nodes_in_each_layer"])
            # Generate a couple of rule nodes
            for node in range(number_of_nodes):
                # Generate a rule node
                rule_node = RuleNode(
                                        name=self.variableGenerator.generate_new_lower_case_variabe(self.parsed_graph.get_parsed_node_names()) + "__",
                                        depth=layer,
                                        params=self.params,
                                        randomness=self.randomness,
                                        constantGenerator=self.constantGenerator,
                                    )

                self.all_rule_nodes.append(rule_node)

        # Introduce edges between the nodes
        for node in self.all_rule_nodes:
            number_of_out_going_edges = self.randomness.get_random_integer(0, self.params["max_number_of_outgoing_edges"])
            nodes_of_lower_depth = [i for i in self.all_rule_nodes if i.get_depth() > node.get_depth()]
            if len(nodes_of_lower_depth) == 0: continue
            for edge in range(number_of_out_going_edges):
                start_node = node
                end_node = self.randomness.random_choice(nodes_of_lower_depth)
                charge = "+ve"
                level = 1
                new_edge = Edge(start=start_node, end=end_node, charge=charge, level=level)
                end_node.add_incoming_rule_edge(new_edge)
                start_node.add_outgoing_rule_edge(new_edge)

        # Introduce edges from parsed nodes to rule nodes
        for node in self.parsed_graph.get_parsed_nodes():
            rule_node = self.randomness.random_choice(self.all_rule_nodes)
            new_edge = Edge(start=node, end=rule_node, charge="+ve", level=1)
            node.add_outgoing_rule_edge(new_edge)
            rule_node.add_incoming_rule_edge(new_edge)


        # Recursively generate variables for each rule node.
        # This should happen while respecting the types that are flowing into a rule node.
        # Variable generation is with a depth first search.
        for node in self.all_rule_nodes:
            if len(node.get_variables()) == 0 and node in self.all_rule_nodes:
                node.generate_node_variables()

        # Now we can safely add some more edges on a different level 
        for i in range(self.params["max_number_of_higher_level_edges"]):
            R_1 = self.randomness.random_choice(self.all_rule_nodes)
            nodes_of_lower_depth = [i for i in self.all_rule_nodes if i.get_depth() > R_1.get_depth()]
            if len(nodes_of_lower_depth) == 0: continue
            R_2 = self.randomness.random_choice(nodes_of_lower_depth)
            charge = "+ve"
            level = R_2.get_max_edge_level()
            if len([edge for edge in R_2.get_all_incoming_rule_edges() if edge.get_level() == level]) > self.params["max_number_of_outgoing_edges"]: 
                level += 1
            
            # Restrict the maximum allowed level to "max_edge_level".
            if level > self.params["max_edge_level"]: continue
            
            # We should ensure only type safe edges are allowed to move ahead.
            types_in_R_1 = [var.get_type() for var in R_1.get_variables()]
            types_in_R_2 = [var.get_type() for var in R_2.get_variables()]
            type_safe=True
            for type in types_in_R_2:
                if type not in types_in_R_1: 
                    type_safe = False
                    break
            if type_safe:
                edge = Edge(start=R_1, end=R_2, charge=charge, level=level)
                R_2.add_incoming_rule_edge(edge)
                R_1.add_outgoing_rule_edge(edge)

        # Generate fact nodes for rule nodes - we will only add fact nodes for a rule node if all variable types are base types
        for rule_node in self.all_rule_nodes:
            non_general_variable_types = [var.get_type() for var in rule_node.get_variables() if var.get_type() not in self.params["general_types"]]
            if len(non_general_variable_types) != 0 or len(rule_node.get_variables()) == 0:
                # This rule node contains some non-basic types or no variables at all
                continue
            rule_node.generate_fact_nodes()
            self.all_fact_nodes += rule_node.get_fact_nodes()

        # Choose a RuleNode as the output node for this graph
        self.output_node = self.randomness.random_choice([node for node in self.all_rule_nodes if node.get_depth() == self.number_of_layers-1])
        self.output_node.set_generate_output_to_true()
        self.output_node.set_ancestry("+ve")
        self.append_positive_ancestry(self.output_node)
        self.output_node.set_as_output_node()


        # Generate joins in the graph at run time and save this information in the graph
        for rule_node in self.all_rule_nodes:
            rule_node.generate_joins()

        # Introduce negative edges
        for i in range(self.params["max_number_of_negative_edges"]):
            R_2 = self.randomness.random_choice(self.all_rule_nodes)
            edge = self.randomness.random_choice(R_2.get_all_incoming_rule_edges()) if len(R_2.get_all_incoming_rule_edges()) != 0 else None
            if edge is None: continue
            if edge.get_charge() == "-ve": continue
            if edge.check_if_safe_to_assign_neg_sign(): edge.set_charge("-ve")

        # Compute ancestry w.r.t the output node
        compute_node_charge_property_value(self.output_node, [])
        self.retrieve_ancestry_information()
        self.logging.add_log_text("[generateACyclicGraph] Graph generation finished successfully")
        if self.full_logs: 
            self.logging.add_log_text("[generateACyclicGraph] Some graph stats: ")
            self.logging.add_log_text("    >>> Number of nodes in positive ancestry: " + str(len(self.get_positive_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_positive_ancestry()]))
            self.logging.add_log_text("    >>> Number of nodes in negative ancestry: " + str(len(self.get_negative_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_negative_ancestry()]))
            self.logging.add_log_text("    >>> Number of nodes in unknown ancestry: " + str(len(self.get_unknown_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_unknown_ancestry()]))
            self.logging.add_log_text("    >>> Number of nodes not in ancestry: " + str(len(self.get_not_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_not_ancestry()]))

    def log_graph_stats(self, logger):
            logger.add_log_text("\t\tSome graph stats: ")
            logger.add_log_text("\t\t    >>> Number of nodes in positive ancestry: " + str(len(self.get_positive_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_positive_ancestry()]))
            logger.add_log_text("\t\t    >>> Number of nodes in negative ancestry: " + str(len(self.get_negative_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_negative_ancestry()]))
            logger.add_log_text("\t\t    >>> Number of nodes in unknown ancestry: " + str(len(self.get_unknown_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_unknown_ancestry()]))
            logger.add_log_text("\t\t    >>> Number of nodes not in ancestry: " + str(len(self.get_not_ancestry()))  + "  ->  " + str([i.get_name() for i in self.get_not_ancestry()]))
