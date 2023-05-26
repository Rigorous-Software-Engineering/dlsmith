
from copy import deepcopy
import multiprocessing
import shutil
import time
import pyfiglet
import argparse
import os
from termcolor import colored
from dlsmith.dataDependencyGraph.dependencyGraph import DataDependencyGraph
from dlsmith.dataDependencyGraph.parsedGraph import ParsedGraph
from dlsmith.utils.argument_parser import MainArgumentParser
from dlsmith.home import get_home
from dlsmith.utils.file_operations import copy_fact_files, create_core_directory, create_server_directory, delete_all_csv_files, export_errored_out_instance, generate_ddlog_facts_file, load_parameters
from dlsmith.utils.logging import Logging
from dlsmith.utils.programGenerator import generateProgram
from dlsmith.utils.randomness import Randomness
from dlsmith.utils.stats import Stats
from dlsmith.transformations.manager import TransformationManager

from dlsmith.engines.Ascent.ascent_program import AscentProgram

from dlsmith.engines.DDlog.ddlog_program import DDlogProgram
from dlsmith.engines.Flix.flix_program import FlixProgram, add_fact_nodes
from dlsmith.engines.Formulog.formulog_program import FormulogProgram
from dlsmith.engines.Scallop.scallop_program import ScallopProgram
from dlsmith.engines.Souffle.souffle_program import SouffleProgram



def run(core, local_seed, wait):
    print("Staring the run procedure")
    print("local seed = " + str(local_seed))
    time.sleep(wait)
    core_dir_path = create_core_directory(os.path.join(HOME, "temp"), SERVER, core) # Create the core directory
    randomness = Randomness(local_seed)
    stats = Stats(core_dir_path)
    stats.dump_transformation_stats_as_json()
    for i in range(PARAMS["number_of_programs"]):
        # Create a dependency graph
        orig_logging = Logging()
        if ENGINE == "ascent": PARAMS["general_types"] = PARAMS["ascent_types"]
        if ENGINE == "scallop" or ENGINE == "scallop_compiler": PARAMS["general_types"] = PARAMS["scallop_types"]
        parsedGraph = ParsedGraph(randomness=randomness, engine=ENGINE, path_to_home=HOME, logger=orig_logging, params=PARAMS, debug=DEBUG)
        dependencyGraph = DataDependencyGraph(PARAMS, randomness, orig_logging, parsedGraph, FULL_LOGS)
        print("[main] {" + colored(str(i), "yellow", attrs=["bold"]) + "}  Generating a dependency graph. Seed file used: " + str(parsedGraph.get_seed_folder_path()))
        dependencyGraph.generateACyclicGraph()

        # Create a Datalog/Prolog program based on the data dependency graph.
        program = None
        runner = None
        runTimeInfo = None
        engine_options = None
        program, runTimeInfo, runner, engine_options = generateProgram(
                        PARAMS, 
                        ENGINE,
                        randomness,
                        dependencyGraph,
                        parsedGraph,
                        orig_logging,
                        DEBUG,
                        core,
                        program,
                        runner,
                        runTimeInfo,
                        engine_options
        )

        # ****** Export the program ******
        program.export_program_string(program_number=i, core_path=core_dir_path, file_name="orig_rules")
        
    
        if parsedGraph.get_seed_folder_path() is not None: 
            copy_fact_files(program.get_program_path(), parsedGraph.get_seed_folder_path()) # Copy fact files from the seed folder.
        if ENGINE == "ddlog": generate_ddlog_facts_file(program=program, output_node=dependencyGraph.get_output_node())
        os.system("clear")
        print(colored(" xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", "yellow", attrs=["bold"]))
        print(colored(" xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ORIGINAL PROGRAM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", "yellow", attrs=["bold"]))
        print(colored(" xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", "yellow", attrs=["bold"]))
        print(colored(program.get_program_string(), "cyan", attrs=["bold"]))
        orig_logging.dump_log_file()
        runTimeInfo.set_path_to_program(program.get_program_path())

        transfromationManager = TransformationManager(randomness=randomness, 
                                                        dependencyGraph=dependencyGraph, 
                                                        params=PARAMS,
                                                        runTimeInformation = runTimeInfo,
                                                        engine=ENGINE, 
                                                        full_logs=FULL_LOGS, 
                                                        stats = stats
                                                    )
        for j in range(PARAMS["number_of_transformations"]):
            orig_logging.dump_log_file()
            transfr_logging = deepcopy(orig_logging)
            transfr_logging.add_log_text("[main] Transformation number: " + str(j))
            transformedGraph = transfromationManager.generate_a_new_transformation(logging=transfr_logging)
            transformation_sequence = transfromationManager.get_transformation_sequence()
            # Generate a new program based on the transformed program
            transformedProgram = None
            if ENGINE == "souffle":
                transfr_logging.add_log_text("[Main] Generating transformed a transformed Souffle program")
                transformedProgram= SouffleProgram(
                                        dependencyGraph=transformedGraph,
                                        params=PARAMS,
                                        randomness=randomness,
                                        logging=transfr_logging,
                                        parsedProgramText=parsedGraph.get_parsed_program_text()
                )
                transformedProgram.generate_program_string()
            elif ENGINE == "ddlog":
                transfr_logging.add_log_text("[Main] Generating transformed a transformed DDLOG program")
                transformedGraph.append_R()
                transformedProgram= DDlogProgram(
                                        dependencyGraph=transformedGraph,
                                        params=PARAMS,
                                        randomness=randomness,
                                        logging=transfr_logging,
                                        parsedProgramText=parsedGraph.get_parsed_program_text()
                )
                transformedProgram.generate_program_string()
            elif ENGINE == "formulog": 
                transfr_logging.add_log_text("[Main] Generating transformed a transformed Formulog program")
                transformedProgram= FormulogProgram(
                                        dependencyGraph=transformedGraph,
                                        params=PARAMS,
                                        randomness=randomness,
                                        logging=transfr_logging,
                                        parsedProgramText=parsedGraph.get_parsed_program_text()
                )
                transformedProgram.generate_program_string()
            elif ENGINE == "flix": 
                transfr_logging.add_log_text("[Main] Generating transformed a transformed Flix program")
                transformedProgram= FlixProgram(
                                        dependencyGraph=transformedGraph,
                                        params=PARAMS,
                                        randomness=randomness,
                                        logging=transfr_logging,
                                        parsedProgramText=parsedGraph.get_parsed_program_text()
                )
                transformedProgram.generate_program_string()
            elif ENGINE == "ascent":
                transfr_logging.add_log_text("[Main] Generating transformed a transformed Ascent program")
                transformedProgram= AscentProgram(
                                        dependencyGraph=transformedGraph,
                                        params=PARAMS,
                                        randomness=randomness,
                                        logging=transfr_logging,
                                        parsedProgramText=parsedGraph.get_parsed_program_text()
                )
                transformedProgram.generate_program_string()
            elif ENGINE == "scallop" or ENGINE == "scallop_compiler":
                transfr_logging.add_log_text("[Main] Generating transformed a transformed Scallop program")
                transformedProgram= ScallopProgram(
                                        dependencyGraph=transformedGraph,
                                        params=PARAMS,
                                        randomness=randomness,
                                        logging=transfr_logging,
                                        parsedProgramText=parsedGraph.get_parsed_program_text()
                )
                transformedProgram.generate_program_string()
            else:
                print(colored("Engine not found", "red", attrs=["bold"]))

            transfr_logging.add_log_text("[Main] Transformed program string successfully generated")
            transformedProgram.export_program_string(program_number=i, core_path=core_dir_path, file_name="transformed_rules_" + str(j))
            transfr_logging.add_log_text("\n")
            transfr_logging.dump_log_file()
            # Refresh stats file dump
            stats.dump_transformation_stats_as_json()

            
            print(colored(" xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", "yellow", attrs=["bold"]))
            print(colored(" xxxxxxxxxxxxxxxxxxxxxxxxxxxx TRANSFORMED PROGRAM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", "yellow", attrs=["bold"]))
            print(colored(" xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ", "yellow", attrs=["bold"]))
            print(colored(transformedProgram.get_program_string(), "cyan", attrs=["bold"]))




        

def main():
    global HOME                 # DlSmith home (imported from a json file somewhere. dont know where yet)
    global SEED                 # Randomness seed for the run() instance
    global SERVER               # Name of the machine, in case you are running on multiple machines with a shared file system
    global DEBUG                # Run in debug mode. 
    global ENGINE               # Enbgine
    global CORES                # Number of cores to run in parallel
    global PARAMS               # Tunable parameters
    global FULL_LOGS             # Generate full logs
    global STATS                # Display stats
    # Parse arguments 
    arguments = MainArgumentParser()
    arguments.parse_arguments(argparse.ArgumentParser())
    parsedArguments = arguments.get_arguments()

    # Values for global variables
    HOME = get_home()
    SEED = parsedArguments["seed"]
    SERVER = parsedArguments["server"]
    DEBUG = parsedArguments["debug"]
    ENGINE = parsedArguments["engine"]
    CORES = parsedArguments["cores"]
    FULL_LOGS = parsedArguments["fulllog"]
    STATS = parsedArguments["stats"]
    PARAMS = load_parameters(HOME)
    #os.system("clear")
    initial_text = pyfiglet.figlet_format("dlsmith")
    print(colored(initial_text , "yellow", attrs=["bold"]))

    # START FUZZING -------------
    print("\nGlobal Variables:")
    print(colored("\tHOME = ", attrs=["bold"]) + colored(HOME, "cyan", attrs=["bold"]))
    print(colored("\tGLOBAL SEED = ", attrs=["bold"]) + colored(SEED, "cyan", attrs=["bold"]))
    print(colored("\tSERVER = ", attrs=["bold"]) + colored(SERVER, "cyan", attrs=["bold"]))
    print(colored("\tCORES = ", attrs=["bold"]) + colored(CORES, "cyan", attrs=["bold"]))
    print(colored("\tENGINE = ", attrs=["bold"]) + colored(ENGINE, "cyan", attrs=["bold"]))
    print(colored("\tDEBUG = ", attrs=["bold"]) + colored(DEBUG, "cyan", attrs=["bold"]))

    create_server_directory(os.path.join(HOME, "temp"), SERVER) # Create server directory in temp
    run(core=1, local_seed=SEED, wait=1)

if __name__ == '__main__':
    signal = main()