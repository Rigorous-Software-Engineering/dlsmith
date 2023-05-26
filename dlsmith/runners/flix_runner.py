import subprocess
from dlsmith.runners.base_runner import BaseRunner
from termcolor import colored
import os

from dlsmith.utils.file_operations import create_fact_file_with_data

class FlixRunner(BaseRunner):

    def generate_command(self, init):
        # First run init
        command = "cd " + self.program.get_program_path()
        if init:
            # In case we are running the transformed program, we don't need this
            command += " && " + self.path_to_engine + " init "
        
        # Then copy file path to src and call it Main.flix
        command += " && rm src/Main.flix"
        command += " && cp " + self.program.get_program_file_path() + " src/Main.flix "
        
        # Now run "run"
        command += " && " + self.path_to_engine + " run"
        return command


    def run_original(self, program, engine_options, logger):
        self.program = program
        self.path_to_engine = self.params["path_to_flix_compiler"]
        self.command_line_options = engine_options 
        command = self.generate_command(init=True) + " " + self.command_line_options
        logger.add_log_text("[Flix Runner] Orig command: " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        
        logger.add_log_text("\n[Flix Runner - run_original]: Standard output after running the original program:")
        logger.add_log_text("===============================================================================================================")
        logger.add_log_text(standard_output)
        logger.add_log_text("===============================================================================================================")
        
        signal = self.process_standard_output(standard_output)
        if signal == 1: return 1
        if signal == 2: return 2
        signal = self.process_standard_error(standard_error)
        if signal == 1: return 1
        if signal == 2: return 2
        # Check if an output file is produced.
        signal = self.process_output(standard_output, True, logger)
        return signal

    def run_transformed(self, program, engine_options, logger):
        self.program = program
        self.command_line_options = engine_options
        command = self.generate_command(init=False) + " " + self.command_line_options
        logger.add_log_text("[Flix Runner] Orig command: " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_output(standard_output)
        if signal == 1: return 1
        if signal == 2: return 2
        signal = self.process_standard_error(standard_error)
        if signal == 1: return 1
        if signal == 2: return 2
        logger.add_log_text("\n[FLIX Runner - run_transformedd]: Standard output after running the transformed program:")
        logger.add_log_text("===============================================================================================================")
        logger.add_log_text(standard_output)
        logger.add_log_text("===============================================================================================================")
        signal = self.process_output(standard_output, False, logger)
        return signal

    def process_standard_output(self, std_output):
        if std_output.find("missing instance") != -1:
            print(colored("Missing instance error. Ignore", "yellow", attrs=["bold"]))
            return 2


        if std_output.find("Error") != -1:
            print(colored("CRITICAL UNKNOWN ERROR", "red", attrs=["bold"]))
            print(colored(std_output, "red", attrs=["bold"]))
            return 1
    
    def process_standard_error(self, std_err):
        if std_err.find("Error") != -1:
            print(colored("CRITICAL UNKNOWN ERROR", "red", attrs=["bold"]))
            print(colored(std_err, "red", attrs=["bold"]))
            return 1

    def process_output(self, std_output, orig, logger):
        """
            Parse standard output to get results
        """
        def parse_standard_output(stdOut):
            """
                [(5, 26), (17, 17), (29, 29), (43, 11), (87, 87)]
                [lu]
                [(3, sm), (3, ze), (7, lf), (8, dp), (20, ze), (28, kz), (30, fj), (45, gv), (81, wb), (99, ql)]
            """
            stdOut = stdOut.splitlines()[0].replace(" ", "")
            lines = stdOut[1:-1]
            clean_data = list()
            if len(lines) == 0: return clean_data
            if lines[0] == "(":
                lines = lines.replace("(", "").replace(" ", "").split("),")
            else:
                lines = lines.replace(" ", "").split(",")
            for line in lines: 
                dataline = line.split(",")
                data_row = "".join(i + "\t" for i in dataline).replace(")", "")
                clean_data.append(data_row) 
            return clean_data

        std_output = std_output.replace("Main exited with status code 0.", "").replace("\r", "").replace("\n", "")
        parsed_result = parse_standard_output(std_output)
        
        if self.debug:
            for i in parsed_result: print(colored(i, "yellow", attrs=["bold"]))
            print("")

        if orig:
            results_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_path = os.path.join(self.program.get_program_path(), "transformed.facts")

        create_fact_file_with_data(parsed_result, results_file_path)
        if not os.path.exists(results_file_path):
            return 1
        self.program.set_output_result_path(results_file_path)
        return 0
