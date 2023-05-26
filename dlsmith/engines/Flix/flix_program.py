from dlsmith.dataDependencyGraph.graphUtils import has_rule_parent
from dlsmith.datalog.base_program import BaseProgram
from dlsmith.engines.Flix.flix_rule import FlixRule
from dlsmith.utils.file_operations import create_file
import os
from termcolor import colored

def add_fact_nodes(dependencyGraph):
    # ***********************************************************************************************
    # Rule nodes without any incoming edges cause a 'missing instance' erorr in flix
    # ***********************************************************************************************
    for ruleNode in dependencyGraph.get_all_rule_nodes():
        ruleNode.generate_a_singular_fact_node()


class FlixProgram(BaseProgram):
    
    
    def export_program_string(self, program_number, core_path, file_name):
        self.program_path = os.path.join(core_path, "program_" + str(program_number))
        self.program_file_path = os.path.join(self.program_path, file_name + ".flix")
        self.logging.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path): os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)


    def generate_rules(self):

        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            if rule_node.get_name()[0:4] != "Rule": 
                rule_node.set_name("Rule_" + rule_node.get_name())

        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            if not has_rule_parent(rule_node): continue
            if len(rule_node.get_all_levelled_variable_objects()) == 0: continue
            for level in range(1, rule_node.get_max_edge_level() + 1):
                flix_rule = FlixRule(randomness=self.randomness, level=level, rule_node=rule_node)
                flix_rule.generate_head()
                flix_rule.generate_body_subgoals()
                flix_rule.generate_rule_string()
                self.all_rules.append(flix_rule)
        
        # Set output rule name 
        self.output_rule_name = self.dependencyGraph.get_output_node().get_name()


    def generate_program_string(self):
        # Parsed program string. 
        # >>> There is no parsed program for now


        # Initial text
        self.program_string += "\n/// Output relation is " + self.dependencyGraph.get_output_node().get_name() + "\n"
        self.program_string += "def main(_: Array[String]): Int32 & Impure =  \n"
        self.program_string += "\tlet rules = #{\n"

        # Facts
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            for fact_node in rule_node.get_fact_nodes():
                fact_string = rule_node.get_name() + "("
                for var in fact_node.get_variables():
                    if var.get_type() == "string":
                        fact_string += '"' + var.get_value() + '", '
                    if var.get_type() == "integer": 
                        fact_string += str(var.get_value()) + ", "
                fact_string = fact_string[:-2] + ")."
                self.program_string += "\t\t" + fact_string + "\n"

        self.program_string += "\n\n"

        # Rules
        for rule in self.all_rules:
            self.program_string += "\t\t" + rule.get_rule_string() + "\n"

        # End text
        self.program_string += "};\n"

        # Construct the query here. 
        # query rules select (title) from Movie(title) |> println;
        self.program_string += "\tquery rules select ("
        for var in self.dependencyGraph.get_output_node().get_variables(): self.program_string += var.get_name() + ", "
        self.program_string = self.program_string[:-2] + ") from " + self.dependencyGraph.get_output_node().get_name() + "("
        for var in self.dependencyGraph.get_output_node().get_variables(): self.program_string += var.get_name() + ", "
        self.program_string = self.program_string[:-2] + ") |> println;\n\t0\n"
