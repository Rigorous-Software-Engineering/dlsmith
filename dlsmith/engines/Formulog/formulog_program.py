
from dlsmith.dataDependencyGraph.graphUtils import has_rule_parent
from dlsmith.datalog.base_program import BaseProgram
import os
from dlsmith.engines.Formulog.formulog_rule import FormulogRule
from dlsmith.utils.file_operations import create_file, read_file



class FormulogProgram(BaseProgram):
    
    
    def export_program_string(self, program_number, core_path, file_name):
        self.program_path = os.path.join(core_path, "program_" + str(program_number))
        self.program_file_path = os.path.join(self.program_path, file_name + ".flg")
        self.logging.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path): os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
    
    def generate_rules(self):
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            if not has_rule_parent(rule_node): continue
            if len(rule_node.get_all_levelled_variable_objects()) == 0: continue
            for level in range(1, rule_node.get_max_edge_level() + 1):
                ddlog_rule = FormulogRule(randomness=self.randomness, level=level, rule_node=rule_node)
                ddlog_rule.generate_head()
                ddlog_rule.generate_body_subgoals()
                ddlog_rule.generate_rule_string()
                self.all_rules.append(ddlog_rule)

        # Set output rule name
        self.output_rule_name = self.dependencyGraph.get_output_node().get_name()


    def generate_declarations(self):
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            decl_string = "output "

            if len(rule_node.get_variables()) == 0:
                decl_string += rule_node.get_name()    
            else:
                decl_string += rule_node.get_name() + "("                
                for var in rule_node.get_variables():
                    var_type = ""
                    if var.get_type() == "string": var_type = "string"
                    elif var.get_type() == "integer": var_type = "i32"
                    else: var_type = var.get_type() # User defined type
                    decl_string += var_type + ", "
                decl_string = decl_string[:-2] + ")"

            if self.dependencyGraph.get_output_node() == rule_node:
                decl_string += "   (* ------------ Output node ------------ *)" 

            self.declarations.append(decl_string)

    def generate_program_string(self):
        # Parsed Program text
        self.program_string += "\n(* ----------- Parsed program text begin ----------- *) \n\n"
        self.program_string += self.parsed_program_text
        self.program_string += "\n(* ----------- Parsed program text ends ----------- *)\n\n"

        # Declarations (this includes the declarations for output nodes)
        for decl in self.declarations:
            self.program_string += decl + "\n"
        self.program_string += "\n\n"

        # Facts
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            for fact_node in rule_node.get_fact_nodes():
                fact_string = fact_node.get_name() + "("
                for var in fact_node.get_variables():
                    if var.get_type() == "string":
                        fact_string += '"' + var.get_value() + '", '
                    if var.get_type() == "integer" or var.get_type() == "i32": 
                        fact_string += str(var.get_value()) + ", "
                fact_string = fact_string[:-2] + ")."
                self.program_string += fact_string + "\n"

        self.program_string += "\n\n"

        # Rules
        for rule in self.all_rules:
            self.program_string += rule.get_rule_string() + "\n"