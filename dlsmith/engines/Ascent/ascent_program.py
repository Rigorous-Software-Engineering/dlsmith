from dlsmith.dataDependencyGraph.graphUtils import has_rule_parent
from dlsmith.datalog.base_program import BaseProgram
import os
from dlsmith.engines.Ascent.ascent_rule import AscentRule
from dlsmith.utils.file_operations import create_file

class AscentProgram(BaseProgram):

    def export_program_string(self, program_number, core_path, file_name):
        self.program_path = os.path.join(core_path, "program_" + str(program_number))
        self.program_file_path = os.path.join(self.program_path, file_name + ".rs")
        self.logging.set_log_file_path(self.program_path)
        if not os.path.exists(self.program_path): os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)

    def generate_rules(self):
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            if not has_rule_parent(rule_node): continue
            if len(rule_node.get_all_levelled_variable_objects()) == 0: continue
            for level in range(1, rule_node.get_max_edge_level() + 1):
                ascent_rule = AscentRule(randomness=self.randomness, level=level, rule_node=rule_node)
                ascent_rule.generate_head()
                ascent_rule.generate_body_subgoals()
                ascent_rule.generate_rule_string()
                self.all_rules.append(ascent_rule)
        
        # Set output rule name
        self.output_rule_name = self.dependencyGraph.get_output_node().get_name()
        
    def generate_declarations(self):
        for rule_node in self.dependencyGraph.get_all_rule_nodes():
            decl_string = "\trelation " + rule_node.get_name() + "("
            for var in rule_node.get_variables():
                var_type = ""
                if var.get_type() == "integer": var_type = "i32"
                decl_string += var_type + ", "
            
            if len(rule_node.get_variables()) == 0: 
                decl_string += ")"
            else:
                decl_string = decl_string[:-2] + ");"
            self.declarations.append(decl_string)


    def generate_program_string(self):
        
        # Ascent 
        self.program_string += "\nuse ascent::ascent;"
        self.program_string += "\nascent!{\n"
        
        # Declarations 
        for decl in self.declarations:
            self.program_string += decl + "\n"
        self.program_string += "\n\n"

        # Rules go here...
        for rule in self.all_rules:
            self.program_string += "\t" +rule.get_rule_string() + "\n"

        # Close ascent
        self.program_string += "\n}"

        # Main function 
        self.program_string += "\n\nfn main() {"
        self.program_string += "\n\tlet mut prog = AscentProgram::default();\n"
        
        # Facts go here
        # For example:  prog.edge = vec![(1, 2), (2, 3)];
        for node in self.dependencyGraph.get_all_rule_nodes():
            if len(node.get_fact_nodes()) == 0: continue
            fact_string = "prog." + node.get_name() + " = vec!["
            for fact_node in node.get_fact_nodes():
                fact_value_string = fact_node.get_value_string()
                if len(node.get_variables()) == 1: fact_value_string += ","
                fact_string += "(" + fact_value_string + "), "
            fact_string = fact_string[:-2] + "];"
            self.program_string += "\t" + fact_string + "\n"
        self.program_string += "\n\tprog.run();"

        # Print the output
        self.program_string += '\n\tprintln!("{:?}", prog.' + self.dependencyGraph.get_output_node().get_name() + ');'
        self.program_string += "\n}\n\n"
