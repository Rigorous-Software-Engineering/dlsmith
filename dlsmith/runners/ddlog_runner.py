from dlsmith.runners.base_runner import BaseRunner
import shutil
import os
import subprocess
from termcolor import colored

from dlsmith.utils.file_operations import create_fact_file_with_data

class DDlogRunner(BaseRunner):

    
    def compile_datalog_into_rust(self, logger):
        """
            create a copy of self.program.get_program_file_path() -> rules.dl 
        """
        TIMEOUT = 1000
        if self.debug: TIMEOUT = 300
        # Copy orig_rule.dl -> rules.dl
        if self.debug: print(colored("Copying " + self.program.get_program_file_path() + " into " + self.program.get_program_path() + "/rules.dl", "yellow", attrs=["bold"]))
        copy_command = "cp " + self.program.get_program_file_path() + " " + self.program.get_program_path() + "/rules.dl"
        os.system(copy_command)
        if self.debug: colored("success", "green", attrs=["bold"])
        command = "ulimit -v 100000000 && export DDLOG_HOME=" + self.params["path_to_ddlog_home_dir"] + " && "
        command += "timeout -s SIGKILL " + str(TIMEOUT) + "s " + self.path_to_engine + " -i " + self.program.get_program_path() + "/rules.dl"
        logger.add_log_text("\tCommand: " + command)
        logger.dump_log_file()
        if self.debug: print(colored("\tDDLOG -> RUST   COMMAND = ", "magenta", attrs=["bold"]) + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_error(standard_error=standard_error, file_type="")
        return signal


    def compile_rust_into_an_executable(self, logger):
        command = 'ulimit -v 100000000 && cd ' + self.program.get_program_path() + '/rules_ddlog && export CARGO_PROFILE_RELEASE_OPT_LEVEL="z" && timeout -s SIGKILL 1500s cargo build'
        logger.add_log_text("\tCommand: " + command)
        logger.dump_log_file()
        if self.debug: print(colored("\tRUST -> EXE   COMMAND = ", "magenta", attrs=["bold"]) + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        logger.add_log_text("\nSTANDARD ERROR: " + standard_error)
        logger.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        logger.dump_log_file()
        signal = self.process_standard_error(standard_error=standard_error, file_type="")
        return signal


    def run_ddlog_program(self, orig):
        TIMEOUT = 1000
        if self.debug: TIMEOUT = 300
        command = "ulimit -v 100000000 && timeout -s SIGKILL " + str(TIMEOUT) + "s " + self.program.get_program_path() + "/rules_ddlog/target/debug/rules_cli < " + self.program.get_program_path() + "/facts.dat"
        if self.debug: colored(command, "green", attrs=["bold"])
        #print("RUN command -> " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_error(standard_error, "")
        
        if signal != 0: return signal
        
        #print(colored(standard_output, "green", attrs=["bold"]))
        #print("")
        #print(colored(standard_error, "red", attrs=["bold"]))
        #print("")
        signal = self.process_output(standard_output=standard_output, orig=orig)
        return signal


    def run_original(self, program, engine_options, logger):
        self.program = program
        if self.debug: print(colored("  >> Running the original program", "magenta", attrs=["bold"]))
        logger.add_log_text(" ================== ")
        logger.add_log_text("  Running Original ")
        logger.add_log_text(" ================== ")

        self.path_to_engine = self.params["path_to_ddlog"]
        signal = self.compile_datalog_into_rust(logger)
        if signal != 0: return signal
        signal = self.compile_rust_into_an_executable(logger)
        if signal != 0: return signal
        signal = self.run_ddlog_program(orig=True)
        if signal != 0: return signal
        return 0


    def run_transformed(self, program, engine_options, logger):
        self.program = program
        #print("Running the original program")
        logger.add_log_text(" ================== ")
        logger.add_log_text("  Running Transformed ")
        logger.add_log_text(" ================== ")
        signal = self.compile_datalog_into_rust(logger)
        if signal != 0: return signal
        signal = self.compile_rust_into_an_executable(logger)
        if signal != 0: return signal
        signal = self.run_ddlog_program(orig=False)
        if signal != 0: return signal
        return 0


    def process_output(self, standard_output, orig):
        def parse_ddlog_standard_output(std_output):
            """
                JTKG{.a = "4Dumgdnpgi", .b = "1e3PUPow3z", .c = "4Dumgdnpgi"}
                JTKG{.a = "4Dumgdnpgi", .b = "o54nS4Dumg", .c = "4Dumgdnpgi"}
                JTKG{.a = "Pow3z", .b = "1e3PUPow3z", .c = "Pow3z"}
                JTKG{.a = "Pow3z", .b = "o54nS4Dumg", .c = "Pow3z"}
                YJXZ{.a = "lm1xdGq3R0", .b = "lm1xdGq3R0", .c = "C75fA"}
                OAZM{.a = "vOYyDVIa2Z", .b = "vOYyDVIa2Z"}
                UKVN{.a = "390742D3SH", .b = "5OZ6H"}
                UKVN{.a = "390742D3SH", .b = "KVIP8Q2UP7"}
                UKVN{.a = "A90vPkOAKF", .b = "5OZ6H"}
                UKVN{.a = "A90vPkOAKF", .b = "KVIP8Q2UP7"}
                UKVN{.a = "tRtCTj7Ygx", .b = "5OZ6H"}
                UKVN{.a = "tRtCTj7Ygx", .b = "KVIP8Q2UP7"}
                KVRW{.a = "KDhAk"}
                KVRW{.a = "eQZOpBTRBT"}
            """
            lines = std_output.split("\n")
            clean_data = list()
            for line in lines:
                if line.find("{") == -1: continue # This is not a data row. Ignore this
                data_line = line.replace("\t", "")
                data_line = data_line.replace(" ", "")
                
                # *******************************************************************************************
                # Check if this is the result of the output node. Because we have many output relations now. 
                # If it isn't then we ignore this row. 
                output_relation_name = data_line[0:data_line.find("{")]
                if output_relation_name != self.program.get_output_rule_name(): continue
                # *******************************************************************************************

                data_line = data_line[data_line.find("{") + 1:data_line.find("}")]
                data_row = data_line.split(",")
                for i in range(len(data_row)):
                    data_row[i] = data_row[i][data_row[i].find("=") + 1:]
                row_string = "".join(i + "\t" for i in data_row)
                clean_data.append(row_string)
            #for i in clean_data:
            #    print(colored(i, "green", attrs=["bold"]))
            #print(colored("length of rows = " + str(len(clean_data)), "yellow", attrs=["bold"]))
            return clean_data
        parsed_result = parse_ddlog_standard_output(standard_output)
        if orig:
            results_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_path = os.path.join(self.program.get_program_path(), "transformed.facts")
        #print("####### Exporting (as .facts) ddlog's stdout result to : ", end="")
        #print(colored(results_file_path, "blue", attrs=["bold"]))
        create_fact_file_with_data(parsed_result, results_file_path)
        if not os.path.exists(results_file_path):
            #print(colored("output file not produced for some reason. This is a problem", "red", attrs=["bold"]))
            return 1
        self.program.set_output_result_path(results_file_path)
        return 0

    
    def process_standard_error(self, standard_error, file_type):
        if standard_error.find("is both declared and used inside relational atom") != -1:
            # We are tolerating this for now
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 2

        if standard_error.find("spurious network error") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 2

        if standard_error.find("Bus error") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 2

        if standard_error.find("unexpected reserved word") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 2

        if standard_error.find("Unknown variable") != -1:
            return 2

        if standard_error.find("panicked") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 2

        if standard_error.find("Failed to parse input file") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("No such file or directory") != -1 or standard_error.find("failed to run command") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("Unknown constructor") != -1:
            #print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("ddlog: Module ddlog_rt imported by") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            print(colored("RUN: export DDLOG_HOME=/home/numair/differential-datalog/", "red", attrs=["bold"]))
            return 1

        if standard_error.find("Killed") != -1:
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            return 2

        if standard_error.find("Error") != -1 or standard_error.find("error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1
        return 0