from dlsmith.dataDependencyGraph.variable import Variable
from dlsmith.dataDependencyGraph.factNode import FactNode
from dlsmith.runTimeInformation.base_run_time import RunTimeBase, node_data


class ScallopRunTime(RunTimeBase):


    def import_run_time_data(self, standard_output):
        """
            Import run time data
        """
        self.logger.add_log_text("[ScallopRunTime] Importing run time data for Scallop...")
        lines = standard_output.split("\n")
        for line in lines:
            for node in [node for node in self.dependencyGraph.get_all_rule_nodes() + self.dependencyGraph.get_complex_nodes() if node is not self.dependencyGraph.get_output_node()]:
                if line[0:len(node.get_name())+1] == node.get_name() + ":":
                    #print("\t\t\tDataline: " + line)
                    data_line = line[line.find("{(") :]
                    data_line = data_line.replace("{", "").replace("}", "").replace(" ", "")
                    if data_line == "": continue
                    data_list = data_line.split("),") # Data list
                    #print("\t\t\tDataList: " + str(data_list))
                    for data_val in data_list:
                        data_val = data_val.replace("(", "").replace(")", "")
                        data_val = data_val.replace('"', "")
                        data_val_list = data_val.split(",")
                        #print("\t\t\t" + node.get_name() + " : " + str(data_val_list))
                        self.run_time_data.append(node_data(node, data_val_list))
                    self.logger.add_log_text("[ScallopRunTime] Imported " + str(len(self.run_time_data)) + " number of data rows for the node " + node.get_name())
        self.run_time_information_available = True
        self.compute_nodes_with_non_empty_output()
        self.logger.add_log_text("[ScallopRunTime] Successfully imported run time data!")

    def generate_facts_from_output(self, node):
        """
            From the imported data, generate fact nodes for 'node'
            Returns: Number of facts inlined
        """
        data = list()
        for i in self.run_time_data:
            if i.get_node().get_name() == node.get_name():
                data.append(i.get_data())

        for row in data: 
            variables = list()
            for i, type in enumerate([var.get_type() for var in node.get_variables()]):
                variables.append(Variable(None, type, row[i]))
            fact_node = FactNode(None, variables, node.get_name(), True)
            node.append_fact_node(fact_node)

        return len(data)
