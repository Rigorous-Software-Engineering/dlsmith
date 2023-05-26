import enum
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.runTimeInformation.base_run_time import RunTimeBase, node_data
from termcolor import colored
from dlsmith.utils.constantGenerator import ConstantGenerator
from dlsmith.utils.file_operations import read_souffle_output_data
import os
from dlsmith.dataDependencyGraph.factNode import FactNode

class SouffleRunTime(RunTimeBase):
    
    def import_run_time_data(self):
        """
            Import run time data
        """
        self.logger.add_log_text("\n[SouffleRunTime] Importing run time data for Souffle..")
        for node in [i for i in self.dependencyGraph.get_all_rule_nodes() if i.get_generate_output_flag()]:
            if node.get_generate_output_flag() and node is not self.dependencyGraph.get_output_node():
                # Skip the output node
                data_file_path = os.path.join(self.path_to_program, node.get_name() + ".csv")
                self.logger.add_log_text("[SouffleRunTime] Importing data for node " + node.get_name() + " from file: " + data_file_path)
                data = read_souffle_output_data(data_file_path)
                for d in data:
                    self.run_time_data.append(node_data(node, d))
        # At this point we have extracted all the data
        self.run_time_information_available = True
        # Compute which nodes actually have non empty outputs
        self.compute_nodes_with_non_empty_output()


    def generate_facts_from_output(self, node):
        """
            From the imported data, generate facts for the node for Souffle
            Returns: Number of facts inlined
        """
        data = list()
        for i in self.run_time_data: 
            if i.get_node().get_name() == node.get_name():
                data.append(i.get_data())

        self.logger.add_log_text("\n[SouffleRunTime] Generating facts from data for node: " + node.get_name())
        for row in data: 
            variables = list()
            for i, type in enumerate([var.get_type() for var in node.get_variables()]):
                variables.append(Variable(None, type, row[i]))
            fact_node = FactNode(None, variables, node.get_name(), True)
            node.append_fact_node(fact_node)

        return len(data)
