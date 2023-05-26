
from dlsmith.runners.base_runner import BaseRunner
from termcolor import colored
import subprocess
import os
from dlsmith.utils.file_operations import create_fact_file_with_data


class ScallopRunner(BaseRunner):


    def run_original(self, program, engine_options, logger):
        self.program = program
        if self.debug: print(colored("  >> Running the original program", "magenta", attrs=["bold"]))
        command = "timeout -s SIGKILL " + str(self.params["timeout"]) + "s " + self.params["path_to_scallop"] + " " + self.program.get_program_file_path()
        logger.add_log_text("[Scallop runner] Running the command: " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        
        err_signal = self.process_standard_error(standard_error, logger)
        if err_signal == 1: return 1
        if err_signal == 2: return 2 
        signal = self.process_standard_output(standard_output, logger)
        if signal == 1: return 1
        if signal == 2: return 2 
        signal = self.process_output(standard_output, True)
        self.runTimeInfo.import_run_time_data(standard_output)
        return signal


    def run_transformed(self, program, engine_options, logger):
        self.program = program
        if self.debug: print(colored("  >> Running the transformed program", "magenta", attrs=["bold"]))
        command = "timeout -s SIGKILL " + str(self.params["timeout"]) + "s " + self.params["path_to_scallop"] + " " + self.program.get_program_file_path()
        logger.add_log_text("[Scallop runner] Running the command: " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        
        err_signal = self.process_standard_error(standard_error, logger)
        if err_signal == 1: return 1
        if err_signal == 2: return 2 
        signal = self.process_standard_output(standard_output, logger)
        if signal == 1: return 1
        if signal == 2: return 2 
        signal = self.process_output(standard_output, False)
        return signal    
    



    def process_output(self, standard_output, orig):
        """
            o__: {(34, "eh", "ho"), (63, "db", "uh"), (85, "jg", "ib")}
            l__: {(7, "mv"), (10, "db"), (12, "fw"), (14, "ry"), (23, "yl"), (55, "he"), (80, "xa"), (83, "yq"), (84, "vc")}
            m__: {(8), (24), (44), (51), (77)}
            p__: {("bn", "cw"), ("db", "uh"), ("eh", "ho"), ("ip", "db"), ("jg", "ib"), ("ka", "ew"), ("uh", "ew")}
        """
        output_rule = self.program.get_output_rule_name()
        parsed_result = list() # Only the result for the output node
        if self.debug: print(colored("   >>> Searching for output rule name: " + output_rule, "magenta", attrs=["bold"]))
        lines = standard_output.split("\n")
        for line in lines:
            if line[0:len(output_rule)+1] == output_rule + ":":
                output = line[line.find("{(") :]
                output = output.replace("{", "").replace("}", "").replace(" ", "")
                splitted_output = output.split("),")
                for data_val in splitted_output:
                    data_val = data_val.replace("(", "").replace(")", "")
                    data_val = data_val.replace("\n", "")
                    data_val = data_val.split(",")
                    data_row = ""
                    for i in data_val: data_row += '"' + i.replace('"', "") + '"\t'
                    if self.debug: print("->   " + colored(data_row, "yellow", attrs=["bold"]))
                    if data_row != '""\t': parsed_result.append(data_row)
        if orig:
            results_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_path = os.path.join(self.program.get_program_path(), "transformed.facts")
        
        create_fact_file_with_data(parsed_result, results_file_path)
        if not os.path.exists(results_file_path):
            return 1
        self.program.set_output_result_path(results_file_path)
        return 0


    def process_standard_error(self, std_err, logger):

        if std_err.find("Killed") != -1:
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            logger.add_log_text(std_err)
            logger.dump_log_file()
            return 2
        
        if std_err.find("Argument of the head of a rule is unbounded") != -1:
            logger.add_log_text(std_err)
            logger.dump_log_file()
            return 1

        if std_err.find("thread 'main' panicked at") != -1:
            return 2
        
        if std_err.find("Cannot stratify program:") != -1:
            return 2
        
        if std_err.find("error") != -1 or std_err.find("Error") != -1: 
            logger.add_log_text(std_err)
            logger.dump_log_file()
            return 1
        return 0


    def process_standard_output(self, std_output, logger): 

        if std_output.find("Killed") != -1:
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            logger.add_log_text(std_output)
            logger.dump_log_file()
            return 2

        if std_output.find("Argument of the head of a rule is unbounded") != -1:
            logger.add_log_text(std_output)
            logger.dump_log_file()
            return 1

        if std_output.find("thread 'main' panicked at") != -1:
            return 2

        if std_output.find("Cannot stratify program:") != -1:
            return 2

        if std_output.find("error") != -1 or std_output.find("Error") != -1: 
            logger.add_log_text(std_output)
            logger.dump_log_file()
            return 1
        return 0
    