from abc import ABC, abstractmethod

class BaseRunner(object):

    def __init__(self, params, stats, core, debug, runTimeInfo):
        self.params = params
        self.path_to_engine = None
        self.path_to_db = None
        self.program = None
        self.stats = stats
        self.core = core
        self.debug = debug
        self.runTimeInfo = runTimeInfo
        self.clean_data = ""
        self.program_name = None
        self.command_line_options = ""


    @abstractmethod
    def run_original(self, program, engine_options, logger):
        pass
    
    @abstractmethod
    def generate_command(self):
        pass

    @abstractmethod
    def run_transformed(self, program, engine_options, logger):
        pass

    @abstractmethod
    def process_output(self, std_output, orig, transformation_number):
        pass

    @abstractmethod
    def process_standard_error(self, std_err):
        pass

    @abstractmethod
    def process_standard_output(self, std_output):
        pass


    @abstractmethod
    def compile_datalog_into_rust(self, logger):
        pass

    @abstractmethod
    def compile_rust_into_an_executable(self, logger):
        pass

    @abstractmethod
    def run_ddlog_program(self, orig, transformation_number):
        pass
