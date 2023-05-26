from dlsmith.runners.base_runner import BaseRunner
import subprocess
from termcolor import colored
import os

class SouffleRunner(BaseRunner):

    def generate_command(self):
        command = "timeout -s SIGKILL " + str(self.params["timeout"]) + "s "
        command += self.path_to_engine
        command += " --fact-dir=" + self.program.get_program_path()
        command += " --output-dir=" + self.program.get_program_path()
        command += " " + self.program.get_program_file_path()
        return command    

    def generate_auto_schedule_command(self, engine_options, orig):
        command = "timeout -s SIGKILL " + str(self.params["timeout"]) + "s "
        command += self.path_to_engine + " -w "
        engine_options = engine_options.replace("-p", "")
        command += engine_options 
        if engine_options.find("-c") != -1:
            command += " --generate=" + self.program.get_program_path() + "/file.cpp"
        command += " --fact-dir=" + self.program.get_program_path()
        command += " --output-dir=" + self.program.get_program_path()
        command += " " + self.program.get_program_file_path()
        if orig:
            command += " --auto-schedule=" + self.program.get_program_path() + "/orig_profile -o " + self.program.get_program_path() + "/orig_binary"
            command += " && " + self.program.get_program_path() + "/orig_binary"
        else:
            command += " --auto-schedule=" + self.program.get_program_path() + "/trans_profile -o " + self.program.get_program_path() + "/trans_binary"
            command += " && " + self.program.get_program_path() + "/trans_binary"
        return command


    def executor(self, command):
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # TODO: Assign it to a CPU?
        #os.system("taskset -p -c " + str(self.core) + " " + str(p.pid))
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        err_signal = self.process_standard_error(standard_error)
        self.process_standard_output(standard_output)
        if err_signal == 1: return 1
        if err_signal == 2: return 2
        return 0



    def run_original(self, program, engine_options, logger):
        self.program = program
        self.path_to_engine = self.params["path_to_souffle"]
        self.command_line_options = "-w" + " " + engine_options
        if engine_options.find("-p") != -1:
            self.command_line_options += " " + self.program.get_program_path() + "/orig_profile --emit-statistics"

        # Compiler mode
        if engine_options.find("-c") != -1:
            self.command_line_options += " --generate=" + self.program.get_program_path() + "/file.cpp"
        command = self.generate_command() + " " + self.command_line_options
        logger.add_log_text("[Souffle Runner] Orig command: " + command)
        
        err_signal = self.executor(command)
        if err_signal == 1: return 1
        if err_signal == 2: return 2
        

        # In case auto-scheduling is selected, run the second command here.
        if engine_options.find("-p") != -1:
            auto_schedule_command = self.generate_auto_schedule_command(engine_options=engine_options, orig=True)
            logger.add_log_text("[Souffle Runner]\u2757\u2757\u2757 Executing the auto-scheduling-command: " + auto_schedule_command)
            err_signal = self.executor(auto_schedule_command) # Run the auto-scheduling command
            if err_signal == 1: return 1
            if err_signal == 2: return 2


        # Check if output file produced or not
        output_file_path = os.path.join(program.get_program_path(), program.get_output_rule_name() + ".csv")
        if not os.path.exists(output_file_path):
            print(colored("output file not produced for the original program", "red", attrs=["bold"]))
            return 1 
        # Rename original file to orig.csv
        new_output_file_path = output_file_path.replace(self.program.get_output_rule_name()+".csv", "orig.facts")
        os.rename(output_file_path, new_output_file_path)
        self.program.set_output_result_path(new_output_file_path)
        self.runTimeInfo.import_run_time_data()
        return 0


    def run_transformed(self, program, engine_options, logger):
        self.program = program
        self.path_to_engine = self.params["path_to_souffle"]
        self.command_line_options = "-w" + " " + engine_options
        if engine_options.find("-p") != -1:
            self.command_line_options += " " + self.program.get_program_path() + "/trans_profile --emit-statistics"
        if engine_options.find("-c") != -1:
            self.command_line_options += " --generate=" + self.program.get_program_path() + "/file.cpp"
        command = self.generate_command() + " " + self.command_line_options
        logger.add_log_text("[Souffle Runner] Transformed command: " + command)
        
        err_signal = self.executor(command)
        if err_signal == 1: return 1
        if err_signal == 2: return 2
        

         # In case auto-scheduling is selected, run the second command here.
        if engine_options.find("-p") != -1:
            auto_schedule_command = self.generate_auto_schedule_command(engine_options=engine_options, orig=False)
            logger.add_log_text("[Souffle Runner]\u2757\u2757\u2757 Executing the auto-scheduling-command: " + auto_schedule_command)
            err_signal = self.executor(auto_schedule_command) # Run the auto-scheduling command
            if err_signal == 1: return 1
            if err_signal == 2: return 2
        
        # Check if output file produced or not
        output_file_path = os.path.join(program.get_program_path(), program.get_output_rule_name() + ".csv")
        if not os.path.exists(output_file_path):
            print(colored("output file not produced for the transformed program", "red", attrs=["bold"]))
            print(colored(output_file_path, "red", attrs=["bold"]))
            return 1 
        # Rename transformed file to orig.csv
        new_output_file_path = output_file_path.replace(self.program.get_output_rule_name()+".csv", "transformed.facts")
        os.rename(output_file_path, new_output_file_path)
        self.program.set_output_result_path(new_output_file_path)
        return 0


    def process_standard_output(self, std_output):
        pass


    def process_standard_error(self, std_err):
        """
            Output signals: 
                0: OK
                1: FATAL ERROR: This can burn everything
                2: Local ERROR: We will record this error but we can recover from this
                3: Don't care: We will just ignore this error
        """

        if std_err.find("Killed") != -1:
            print(colored(std_err, "red", attrs=["bold"]))
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            return 2

        if std_err.find("/home/numair/souffle_installations/souffle/src/ast2ram/seminaive/ValueTranslator.cpp:47") != -1:
            return 2
        
        if std_err.find("src/include/souffle/utility/MiscUtil.h:217") != -1:
            return 2

        if std_err.find("src/ast2ram/utility/SipsMetric.cpp:134") != -1:
            return 2

        if std_err.find("src/include/souffle/profile/Reader.h:437") != -1:
            return 2

        if std_err.find("Segmentation fault") != -1 or std_err.find("segmentation fault") != -1:
            print(colored(std_err, "red", attrs=["bold"]))
            print(colored("SEGFAULT", "red", attrs=["bold"]))
            return 1
        
        if std_err.find("assertion") != -1 or std_err.find("Assertion") != -1:
            print(colored(std_err, "red", attrs=["bold"]))
            print(colored("Assertion Failure", "red", attrs=["bold"]))
            return 1

        if std_err.find("syntax error") != -1:
            print(colored(std_err, "red", attrs=["bold"]))
            print(colored("Syntax Error", "red", attrs=["bold"]))
            return 1

        if std_err.find("Error: Ungrounded variable") != -1:
            print(colored(std_err, "red", attrs=["bold"]))
            print(colored("Ungrounded varibales", "red", attrs=["bold"]))
            return 1

        if std_err.find("Error") != -1:
            print(colored(std_err, "red", attrs=["bold"]))
            return 1