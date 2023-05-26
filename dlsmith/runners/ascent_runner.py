from dlsmith.runners.base_runner import BaseRunner
import subprocess
from termcolor import colored
import os
import shutil

from dlsmith.utils.file_operations import create_fact_file_with_data

class AscentRunner(BaseRunner):

    def generate_command(self):
        pass
    
    def create_a_new_rust_project(self):
        command = "cd " + self.program.get_program_path() + " && cargo new ascent_project"
        subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        source = self.program.get_program_file_path()
        destination = os.path.join(self.program.get_program_path(), "ascent_project", "src", "main.rs")
        toml_file = os.path.join(self.program.get_program_path(), "ascent_project", "Cargo.toml")
        shutil.copy(source, destination)
        git_link = '{git = "https://github.com/s-arash/ascent", rev="' + self.params["ascent_commit"] + '"}'
        text_to_echo = "echo 'ascent = " +  git_link + "'"
        command = text_to_echo + " >> " + toml_file
        os.system(command)


    def run_original(self, program, engine_options, logger):
        self.program = program 
        if self.debug: print(colored("  >> Running the original program", "magenta", attrs=["bold"]))
        logger.add_log_text(" ================== ")
        logger.add_log_text("  Running Original ")
        logger.add_log_text(" ================== ")
        self.create_a_new_rust_project()
        
        project_path = os.path.join(self.program.get_program_path(), "ascent_project")
        command = "cd " + project_path + " && " + " cargo run"
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        #print(standard_error)
        #print(standard_output)

        err_signal = self.process_standard_error(standard_error, logger)
        if err_signal == 1: return 1
        if err_signal == 2: return 2 

        signal = self.process_output(standard_output, True)
        return signal


    def run_transformed(self, program, engine_options, logger):
        if self.debug: print(colored("  >> Running the TRANSFORMED program", "magenta", attrs=["bold"]))
        self.program = program
        
        # Copy the transformed program file to src/main.rs
        source = self.program.get_program_file_path()
        destination = os.path.join(self.program.get_program_path(), "ascent_project", "src", "main.rs")
        shutil.copy(source, destination)
        project_path = os.path.join(self.program.get_program_path(), "ascent_project")
        command = "cd " + project_path + " && " + " cargo run"  
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        err_signal = self.process_standard_error(standard_error, logger)
        if err_signal == 1: return 1
        if err_signal == 2: return 2 
        
        signal = self.process_output(standard_output, False)
        return signal

    def process_output(self, standard_output, orig):
        """
            [(34,), (26,), (7,), (30,), (5,)]
        """
        parsed_result = list()
        splitted_output = standard_output.split("),")
        for i in splitted_output:
            row = i.replace("(", "").replace("[", "").replace("]", "").replace(" ", "").replace(")","").replace("\n", "")
            if len(self.program.get_data_dependency_graph().get_output_node().get_variables()) == 1:
                row = row.replace(",", "")
            row = row.replace(",", "\t") # Save as tsv
            if row!= "": parsed_result.append(row)
        if orig: 
            results_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_path = os.path.join(self.program.get_program_path(), "transformed.facts")
        create_fact_file_with_data(parsed_result, results_file_path)
        if not os.path.exists(results_file_path):
            #print(colored("output file not produced for some reason. This is a problem", "red", attrs=["bold"]))
            return 1
        self.program.set_output_result_path(results_file_path)
        return 0


    def process_standard_error(self, std_err, logger):
        if std_err.find("error") != -1:
            logger.add_log_text(std_err)
            logger.dump_log_file()
            return 1
        return 0
    
    def process_standard_output(self, std_output):
        pass