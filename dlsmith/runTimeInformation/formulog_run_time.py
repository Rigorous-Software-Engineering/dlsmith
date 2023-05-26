from dlsmith.dataDependencyGraph.factNode import FactNode
from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.runTimeInformation.base_run_time import RunTimeBase, node_data

class FormulogRunTime(RunTimeBase):


    def import_run_time_data(self, standard_output):
        """
            Import run time data.
        """
        self.logger.add_log_text("\n[FormulogRunTime] Importing run time data for Formulog...")
        lines = standard_output.split("\n")
        for line in lines:
            for node in [node for node in self.dependencyGraph.get_all_rule_nodes() if node is not self.dependencyGraph.get_output_node()]:
                if line[0:len(node.get_name())+1] == node.get_name() + "(":
                    data_line = line.replace(node.get_name(), "")
                    data_line = data_line[1:-1]
                    data_line = data_line.replace(" ", "")
                    data_line = data_line.replace('"', '')
                    data_list = data_line.split(",") # Data list
                    self.run_time_data.append(node_data(node, data_list))
        self.run_time_information_available = True
        self.compute_nodes_with_non_empty_output()
        self.logger.add_log_text("\n[FormulogRunTime] Successfully imported run time data!")


    def generate_facts_from_output(self, node):
        """
            From the imported data, generate facts for the node for Formulog
            Returns: Number of facts inlined
        """
        data = list()
        for i in self.run_time_data:
            if i.get_node().get_name() == node.get_name():
                data.append(i.get_data())
        self.logger.add_log_text("\n[FormulogRunTime] Generating facts from data for node: " + node.get_name())
        for row in data: 
            variables = list()
            for i, type in enumerate([var.get_type() for var in node.get_variables()]):
                variables.append(Variable(None, type, row[i]))
            fact_node = FactNode(None, variables, node.get_name(), True)
            node.append_fact_node(fact_node)

        return len(data)
