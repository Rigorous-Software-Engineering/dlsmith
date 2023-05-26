
from dlsmith.runners.base_runner import BaseRunner
import subprocess
from termcolor import colored
import os

from dlsmith.utils.file_operations import create_fact_file_with_data


class FormulogRunner(BaseRunner):
    
    def generate_command(self):
        command = "timeout -s SIGKILL " + str(self.params["timeout"]) + "s "
        command += self.path_to_engine
        command += " " + self.program.get_program_file_path()
        return command
    
    def run_original(self, program, engine_options, logger):
        self.program = program
        if self.debug: print(colored("  >> Running the original program", "magenta", attrs=["bold"]))
        logger.add_log_text(" ================== ")
        logger.add_log_text("  Running Original ")
        logger.add_log_text(" ================== ")
        
        self.path_to_engine = self.params["path_to_formulog"]
        self.command_line_options = engine_options
        command = self.generate_command() + " " + self.command_line_options
        logger.add_log_text("[Formulog Runner] Orig Command: " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        
        logger.add_log_text("\n[Formulog Runner - run_original]: Standard output after running the original program:")
        logger.add_log_text("===============================================================================================================")
        logger.add_log_text(standard_output)
        logger.add_log_text("===============================================================================================================")
        err_signal = self.process_standard_error(standard_error)
        if err_signal == 1: return 1
        if err_signal == 2: return 2
        signal = self.process_output(standard_output, True, logger)
        self.runTimeInfo.import_run_time_data(standard_output)
        return signal 

    def run_transformed(self, program, engine_options, logger):
        self.program = program
        if self.debug: print(colored("  >> Running the transformed program", "magenta", attrs=["bold"]))
        logger.add_log_text(" ================== ")
        logger.add_log_text("  Running Transformed ")
        logger.add_log_text(" ================== ")

        command = self.generate_command() + " " + self.command_line_options
        logger.add_log_text("[Formulog Runner] Trns Command: " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        logger.add_log_text("\n[Formulog Runner - run_transformedd]: Standard output after running the transformed program:")
        logger.add_log_text("===============================================================================================================")
        logger.add_log_text(standard_output)
        logger.add_log_text("===============================================================================================================")
        err_signal = self.process_standard_error(standard_error)
        if err_signal == 1: return 1
        if err_signal == 2: return 2
        signal = self.process_output(standard_output, False, logger)
        return signal 


    def process_output(self, std_output, orig, logger):
        def parse_standard_output(std_output):
            """
                Parsing...
                Finished parsing (0.216s)
                Type checking...
                Finished type checking (0.023s)
                Rewriting and validating...
                Finished rewriting and validating (0.203s)
                Evaluating...
                Finished evaluating (0.025s)
                Intensional database:
                greeting("Hello, Alice")
                greeting("Hello, Bob")
                greeting("Hello, World")
                greeting("Numair")
                test("Numair")
            """
            output_rule = self.program.get_output_rule_name()
            lines = std_output.split("\n")
            clean_data = list()
            if self.debug: print(colored("   >>> Searching for output rule name: " + output_rule, "magenta", attrs=["bold"]))
            for line in lines:
                if line[0:len(output_rule)+1] == output_rule + "(":
                    data_line = line.replace(output_rule, "")
                    data_line = data_line[1:-1]
                    data_row = data_line.split(",")
                    row_string = "".join(i + "\t" for i in data_row)
                    clean_data.append(row_string)
            return clean_data

        if self.debug: print(colored(std_output, "yellow", attrs=["bold"]))
        if std_output.find("Rule cannot be evaluated given the supplied order.") != -1:
            print(colored("order probelm", "red", attrs=["bold"]))
            return 2
        if std_output.find("Error") != -1 or std_output.find("error") != -1:
            print(colored("An unknown error has occured", "red", attrs=["bold"]))
            return 1

        if std_output.find("Exception") != -1:
            print(colored("An unknown exception has occured", "red", attrs=["bold"]))
            return 1

        if self.debug: print(colored("   >> Begin parsing output", "magenta", attrs=["bold"]))
        parsed_result = parse_standard_output(std_output)
        logger.add_log_text("[Formulog Runner - process output]: Number of entries computed for the output node " + self.program.get_output_rule_name() + " : " + str(len(parsed_result)))
        if self.debug: print(colored(parsed_result, "green", attrs=["bold"]))
        if orig:
            results_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_path = os.path.join(self.program.get_program_path(), "transformed.facts")
        create_fact_file_with_data(parsed_result, results_file_path)
        if not os.path.exists(results_file_path):
            print(colored("output file not produced for some reason. This is a problem in formulog_runner.FormulogRunner.process_output()", "red", attrs=["bold"]))
            return 1
        self.program.set_output_result_path(results_file_path)
        return 0


    def process_standard_error(self, std_err):
        print(colored(std_err, "red", attrs=["bold"]))
        if std_err.find("Exception") != -1:
            print(colored("An unknown exception has occured", "red", attrs=["bold"]))
            return 1
        if std_err.find("Error") != -1 or std_err.find("error") != -1:
            print(colored("An unknown error has occured", "red", attrs=["bold"]))
            return 1
        
        if std_err.find("no viable alternative ") != -1:
            print(colored("No Viable alternative error", "red", attrs=["bold"]))
            return 2
