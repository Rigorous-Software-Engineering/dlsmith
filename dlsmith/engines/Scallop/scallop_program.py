from dlsmith.dataDependencyGraph.graphUtils import has_rule_parent
from dlsmith.datalog.base_program import BaseProgram
import os
from dlsmith.engines.Scallop.scallop_rule import ScallopRule
from dlsmith.utils.file_operations import create_file

class ScallopProgram(BaseProgram):


    def export_program_string(self, program_number, core_path, file_name):
        self.set_program_file_name(file_name)
        self.program_path = os.path.join(core_path, "program_" + str(program_number))
        self.program_file_path = os.path.join(self.program_path, file_name + ".scl")
        self.logging.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path): os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        if os.path.exists(self.program_file_path):
            self.logging.add_log_text("[ScallopProgram] Program successfully exported at: " + self.program_path)
        else:
            self.logging.add_log_text("[ScallopProgram] ERROR: Failed to export program")

    def generate_complex_rules(self):
        for node in self.dependencyGraph.get_complex_nodes():
            if not has_rule_parent(node): continue
            if len(node.get_all_levelled_variable_objects()) == 0: continue
            for level in range(1, node.get_max_edge_level() + 1):
                scallop_rule = ScallopRule(randomness=self.randomness, level=level, rule_node=node)
                scallop_rule.generate_head()
                scallop_rule.generate_body_subgoals()
                scallop_rule.generate_complex_rule_string()
                self.all_rules.append(scallop_rule)


    def generate_rules(self):
        self.generate_complex_rules()
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            if not has_rule_parent(rule_node): continue
            if len(rule_node.get_all_levelled_variable_objects()) == 0: continue
            for level in range(1, rule_node.get_max_edge_level() + 1):
                 # If there are no incoming edges at this level, then continue
                if rule_node.get_incoming_edges_at_a_level(level) == 0: continue
                scallop_rule = ScallopRule(randomness=self.randomness, level=level, rule_node=rule_node)
                scallop_rule.generate_head()
                scallop_rule.generate_body_subgoals()
                scallop_rule.generate_rule_string()
                self.all_rules.append(scallop_rule)

        # Set output rule name
        self.output_rule_name = self.dependencyGraph.get_output_node().get_name()

    def generate_declarations(self):
        for rule_node in self.dependencyGraph.get_all_rule_nodes() + self.dependencyGraph.get_empty_nodes() + self.dependencyGraph.get_complex_nodes():
            decl_string = ""
            decl_string += "type " + rule_node.get_name() + "("
            for var in rule_node.get_variables():
                var_type = ""
                if var.get_type() == "integer": var_type = "i32"
                elif var.get_type() == "string": var_type = "String"
                else: var_type = var.get_type()    # Type imported form the seed file
                decl_string += var_type + ", "
            if len(rule_node.get_variables()) == 0: decl_string += ")"
            else: decl_string = decl_string[:-2] + ")"
            self.declarations.append(decl_string)


    def generate_program_string(self):
        # Parsed program text
        self.program_string += "\n// ************ Parsed program text begin\n\n"
        self.program_string += self.parsed_program_text
        self.program_string += "\n// ************ Parsed program text end\n\n"

        # Declaration
        for decl in self.declarations: self.program_string += decl + "\n"
        self.program_string += "\n\n"


        # Generate facts
        for node in self.dependencyGraph.get_all_rule_nodes() + self.dependencyGraph.get_empty_nodes() + self.dependencyGraph.get_complex_nodes():
            #assert len(node.get_fact_nodes()) != 0
            if len(node.get_fact_nodes()) == 0: continue
            fact_string = "rel " + node.get_name() + " = { "
            if node.get_is_output_node():
                fact_string += "      // Output node"
            fact_string += "\n"
            for fact_node in node.get_fact_nodes():
                if fact_node.get_probability() is not None: fact_string += "\t" + fact_node.get_probability() + "::("
                else: fact_string += "\t("
                for var in fact_node.get_variables():
                    if var.get_type() == "String":
                        fact_string += '"' + var.get_value() + '", '
                    if var.get_type() == "i32":
                        fact_string += str(var.get_value()) + ", "
                fact_string = fact_string[:-2] + "),\n"
            fact_string += "}\n"
            self.program_string += fact_string
        
        self.program_string += "\n"
        # Rules 
        for rule in self.all_rules:
            self.program_string += rule.get_rule_string() + "\n"
        

        # Output
        output_node = self.dependencyGraph.get_output_node()
        for node in self.dependencyGraph.get_all_rule_nodes() + self.dependencyGraph.get_complex_nodes():
            self.program_string += "\n\nquery " + node.get_name()

        
        # Done
        self.program_string += "\n\n"

