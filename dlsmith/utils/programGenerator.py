from random import random
from dlsmith.engines.Ascent.ascent_program import AscentProgram
from dlsmith.engines.DDlog.ddlog_program import DDlogProgram
from dlsmith.engines.Flix.flix_program import FlixProgram, add_fact_nodes
from dlsmith.engines.Formulog.formulog_program import FormulogProgram
from dlsmith.engines.Scallop.scallop_program import ScallopProgram
from dlsmith.engines.Souffle.souffle_program import SouffleProgram
from dlsmith.runTimeInformation.ascent_run_time_info import AscentRunTime
from dlsmith.runTimeInformation.ddlog_run_time import DDlogRunTime
from dlsmith.runTimeInformation.flix_run_time_info import FlixRunTime
from dlsmith.runTimeInformation.formulog_run_time import FormulogRunTime
from dlsmith.runTimeInformation.scallop_run_time_info import ScallopRunTime
from dlsmith.runTimeInformation.souffle_run_time import SouffleRunTime
from termcolor import colored
from dlsmith.runners.ascent_runner import AscentRunner
from dlsmith.runners.ddlog_runner import DDlogRunner
from dlsmith.runners.flix_runner import FlixRunner
from dlsmith.runners.formulog_runner import FormulogRunner
from dlsmith.runners.scallop_compiler_runner import ScallopCompilerRunner
from dlsmith.runners.scallop_runner import ScallopRunner

from dlsmith.runners.souffle_runner import SouffleRunner

def generateProgram(PARAMS,
                    ENGINE,
                    randomness,
                    dependencyGraph,
                    parsedGraph,
                    orig_logging,
                    DEBUG,
                    core,
                    program, 
                    runner, 
                    runTimeinfo, 
                    engine_options):
    """
        Given a data dependency graph, generate the following objects depending on the engine:
            runTimeInfo
            runner
            program

        returns: 
            program, runTimeInfo, runner, engine_options
    """

    if ENGINE == "souffle":
        runTimeInfo = SouffleRunTime(dependencyGraph=dependencyGraph, logger=orig_logging)
        runner = SouffleRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        program= SouffleProgram(
                                    dependencyGraph=dependencyGraph,
                                    params=PARAMS,
                                    randomness=randomness,
                                    logging=orig_logging,
                                    parsedProgramText=parsedGraph.get_parsed_program_text()
        )
        program.generate_program_string()
        engine_options = randomness.random_choice(PARAMS["souffle_options"])
        orig_logging.add_log_text("[main] Souffle Program Generated")
        orig_logging.add_log_text("[main] Selected Souffle options -> " + engine_options)
    elif ENGINE == "ddlog": 
        runTimeInfo = DDlogRunTime(dependencyGraph=dependencyGraph, logger=orig_logging)
        runner = DDlogRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        dependencyGraph.append_R()
        program= DDlogProgram(
                                    dependencyGraph=dependencyGraph,
                                    params=PARAMS,
                                    randomness=randomness,
                                    logging=orig_logging,
                                    parsedProgramText=parsedGraph.get_parsed_program_text()
        )
        program.generate_program_string()
        engine_options = randomness.random_choice(PARAMS["ddlog_options"])
        orig_logging.add_log_text("[main] DDlog Program Generated")
        orig_logging.add_log_text("[main] Selected DDlog options -> " + engine_options)
    elif ENGINE == "formulog":
        runTimeInfo = FormulogRunTime(dependencyGraph=dependencyGraph, logger=orig_logging)
        runner = FormulogRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        program= FormulogProgram(
                                    dependencyGraph=dependencyGraph,
                                    params=PARAMS,
                                    randomness=randomness,
                                    logging=orig_logging,
                                    parsedProgramText=parsedGraph.get_parsed_program_text()
        )
        program.generate_program_string()
        engine_options = randomness.random_choice(PARAMS["formulog_options"])
        orig_logging.add_log_text("[main] Formulog Program Generated")
        orig_logging.add_log_text("[main] Selected Formulog options -> " + engine_options)
    elif ENGINE == "flix": 
        runTimeInfo = FlixRunTime(dependencyGraph=dependencyGraph, logger=orig_logging)
        add_fact_nodes(dependencyGraph)
        runner = FlixRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        program= FlixProgram(
                                dependencyGraph=dependencyGraph,
                                params=PARAMS,
                                randomness=randomness,
                                logging=orig_logging,
                                parsedProgramText=parsedGraph.get_parsed_program_text()
        )
        program.generate_program_string()
        engine_options = randomness.random_choice(PARAMS["flix_options"])
        orig_logging.add_log_text("[main] Flix Program Generated")
        orig_logging.add_log_text("[main] Selected Flix options -> " + engine_options)
    elif ENGINE == "ascent":
        runTimeInfo = AscentRunTime(dependencyGraph=dependencyGraph, logger=orig_logging)
        runner = AscentRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        program = AscentProgram(
                                    dependencyGraph=dependencyGraph,
                                    params=PARAMS,
                                    randomness=randomness,
                                    logging=orig_logging,
                                    parsedProgramText=parsedGraph.get_parsed_program_text()
        )
        program.generate_program_string()
        engine_options = randomness.random_choice(PARAMS["ascent_options"])
        orig_logging.add_log_text("[main] Ascent Program Generated")
        orig_logging.add_log_text("[main] Selected Ascent options -> " + engine_options)
    elif ENGINE == "scallop" or ENGINE == "scallop_compiler":
        runTimeInfo = ScallopRunTime(dependencyGraph=dependencyGraph, logger=orig_logging)
        if ENGINE == "scallop":
            runner = ScallopRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        else: 
            runner = ScallopCompilerRunner(params=PARAMS, stats=None, core=core, debug=DEBUG, runTimeInfo=runTimeInfo)
        program = ScallopProgram(
                                    dependencyGraph=dependencyGraph,
                                    params=PARAMS,
                                    randomness=randomness,
                                    logging=orig_logging,
                                    parsedProgramText=parsedGraph.get_parsed_program_text()
        )
        program.generate_program_string()
        engine_options = randomness.random_choice(PARAMS["scallop_options"])
        orig_logging.add_log_text("[main] Scallop Program Generated")
        orig_logging.add_log_text("[main] Selected Scallop options -> " + engine_options)
    else:
        print(colored("Engine not found", "red", attrs=["bold"]))
        return None, None, None, None


    return program, runTimeInfo, runner, engine_options
