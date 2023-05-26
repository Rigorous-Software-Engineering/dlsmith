from dlsmith.datalog.base_program import BaseProgram
from dlsmith.engines.Souffle.souffle_rule import SouffleRule
from dlsmith.dataDependencyGraph.graphUtils import has_rule_parent
from dlsmith.utils.file_operations import create_file, read_file
import os


class SouffleProgram(BaseProgram):


    def export_program_string(self, program_number, core_path, file_name):
        self.program_path = os.path.join(core_path, "program_" + str(program_number))
        self.program_file_path = os.path.join(self.program_path, file_name + ".dl")
        self.logging.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path): os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)

    def generate_rules(self):
        for node in self.dependencyGraph.get_complex_nodes() + self.dependencyGraph.get_all_rule_nodes():
            if not has_rule_parent(node): continue
            if len(node.get_all_levelled_variable_objects()) == 0: continue
            for level in range(1, node.get_max_edge_level() + 1):
                # If there are no incoming edges at this level, then continue
                if node.get_incoming_edges_at_a_level(level) == 0: continue
                souffle_rule = SouffleRule(randomness=self.randomness, level=level, rule_node=node)
                souffle_rule.generate_head()
                souffle_rule.generate_body_subgoals()
                souffle_rule.generate_rule_string()
                self.all_rules.append(souffle_rule)

        # Set output rule name
        self.output_rule_name = self.dependencyGraph.get_output_node().get_name()


    def generate_declarations(self):
        for node in self.dependencyGraph.get_complex_nodes() + self.dependencyGraph.get_all_rule_nodes():
            decl_string = ".decl " + node.get_name() + "("
            for var in node.get_variables():
                var_type = ""
                if var.get_type() == "integer": var_type = "number"
                elif var.get_type() == "string": var_type = "symbol"
                else: var_type = var.get_type() # User defined type
                decl_string += var.get_name() + ":" + var_type + ", "
            
            if len(node.get_variables()) == 0: 
                decl_string += ")"
            else:
                decl_string = decl_string[:-2] + ")"
            
            if node.get_inline_flag(): decl_string += " inline" 
            decl_string += " " + node.get_data_structure()
            self.declarations.append(decl_string)


    def generate_program_string(self):
        # Parsed program text
        self.program_string += "\n// ************ Parsed program text begin\n\n"
        self.program_string += self.parsed_program_text
        self.program_string += "\n// ************ Parsed program text end\n\n"

        # Declarations
        for decl in self.declarations:
            self.program_string += decl + "\n"
        self.program_string += "\n\n"

        # output node
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            if rule_node.get_generate_output_flag():
                if self.dependencyGraph.get_output_node() == rule_node: 
                    self.program_string += ".output " + rule_node.get_name() + " // Output node\n" 
                else:
                    self.program_string += ".output " + rule_node.get_name() + "\n" 

        self.program_string += "\n\n"        
        # Facts
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            for fact_node in rule_node.get_fact_nodes():
                fact_string = fact_node.get_name() + "("
                for var in fact_node.get_variables():
                    if var.get_type() == "string" or var.get_type() == "symbol" or var.get_type() == "String":
                        fact_string += '"' + var.get_value() + '", '
                    if var.get_type() == "integer" or var.get_type() == "number": 
                        fact_string += str(var.get_value()) + ", "
                fact_string = fact_string[:-2] + ")."
                self.program_string += fact_string + "\n"
        
        self.program_string += "\n"
        
        self.program_string += "\n"
        # Rules
        for rule in self.all_rules:
            self.program_string += rule.get_rule_string() + "\n"


