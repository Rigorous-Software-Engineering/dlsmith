from termcolor import colored
from copy import deepcopy
from dlsmith.dataDependencyGraph.graphUtils import find_all_rules_not_in_ancestors, find_all_rule_ancestors

from dlsmith.transformations.EQU import EQU_COLLAPSE_EDGE, EQU_EDGE_ADD, EQU_EDGE_REM, EQU_FACT_INLINE, EQU_LEVEL_ADD, EQU_LEVEL_ADD_2, EQU_NODE_ADD, EQU_NODE_REM
from dlsmith.transformations.EXP import EXP_EDGE_ADD, EXP_EDGE_REM, EXP_NODE_ADD, EXP_NODE_REM
from dlsmith.transformations.CON import CON_ADD_SELF_EDGE, CON_EDGE_ADD, CON_EDGE_REM, CON_NODE_ADD, CON_NODE_REM
from dlsmith.transformations.queryFuzz.CON import ADD_CON, MOD_CON
from dlsmith.transformations.queryFuzz.EQU import ADD_EQU, MOD_EQU, REM_EQU
from dlsmith.transformations.queryFuzz.EXP import MOD_EXP, REM_EXP



class TransformationManager(object):
    def __init__(self, randomness, dependencyGraph, params, runTimeInformation, engine, full_logs, stats):
        """
            In the settings file: 
                
                For only graph transformations: 
                        "disable_queryfuzz" : true
                        "only_queryfuzz" : false
                
                For only queryFuzz transformations: 
                        "disable_queryfuzz" : false
                        "only_queryfuzz" : true
                
                For both graph + queryFuzz transformations: 
                        "disable_queryfuzz" : false
                        "only_queryfuzz" : false    
        """
        self.randomness = randomness
        self.engine = engine
        self.dependencyGraph = dependencyGraph
        self.params = params
        self.runTimeInfo = runTimeInformation
        self.logging = None
        self.full_logs = full_logs
        self.transformed_graph = None
        self.transformation_types = ["EXP", "CON", "EQU"]
        self.successful_number_of_transformations = 0
        self.stats = stats


        # Equivalent transformations
        self.EQUIVALENT = ["EQU_NODE_ADD", "EQU_NODE_REM", "EQU_EDGE_ADD", "EQU_EDGE_REM", "EQU_LEVEL_ADD", "EQU_LEVEL_ADD_2", "EQU_COLLAPSE_EDGE", "EQU_FACT_INLINE"]  # Equivalent Graph transformations
        self.EXPAND = ["EQU_NODE_ADD", "EQU_NODE_REM", "EQU_EDGE_ADD", "EQU_EDGE_REM", "EQU_LEVEL_ADD", "EQU_LEVEL_ADD_2", "EQU_FACT_INLINE"]                           # Equivalent Graph transformations
        self.CONTRACT = ["EQU_NODE_ADD", "EQU_NODE_REM", "EQU_EDGE_ADD", "EQU_EDGE_REM", "EQU_LEVEL_ADD", "EQU_LEVEL_ADD_2", "EQU_FACT_INLINE"]                         # Equivalent Graph transformations
        
        self.EQUIVALENT += ["ADD_EQU", "MOD_EQU", "REM_EQU"]    # Equivalent QueryFuzz transformation
        self.EXPAND += ["ADD_EQU", "MOD_EQU", "REM_EQU"]        # Equivalent QueryFuzz transformation
        self.CONTRACT += ["ADD_EQU", "MOD_EQU", "REM_EQU"]      # Equivalent QueryFuzz transformation


        # Contracting transformations
        self.CONTRACT += ["CON_EDGE_ADD", "CON_EDGE_REM", "CON_NODE_ADD", "CON_NODE_REM", "CON_ADD_SELF_EDGE"]  # Contracting Graph transformations
        self.CONTRACT += ["MOD_CON"]                                                                            # Contracting QueryFuzz transformation

        # Exanding transformations
        self.EXPAND += ["EXP_EDGE_ADD", "EXP_EDGE_REM", "EXP_NODE_ADD", "EXP_NODE_REM"] # Expanding Graph transformations
        self.EXPAND += ["MOD_EXP"]                                                      # Expanding QueryFuzz transformation



        self.chosen_transformation_type = None
        self.transformation_sequence = list()

        # Common Graph properties that can be shared across transformations
        self.not_ancestory = list() # Nodes in the graph that are not in the ancestory of the output node. 
        self.GraphProperties = None


    def get_oracle(self):
        return self.chosen_transformation_type
    def get_transformation_sequence(self):
        return self.transformation_sequence

    def generate_transformation_sequence(self):
        sequence_length = self.randomness.get_random_integer(1, self.params["max_transformation_sequence"])
        if self.chosen_transformation_type == "EXP":
            return [self.randomness.random_choice(self.EXPAND) for i in range(sequence_length)] 
        if self.chosen_transformation_type == "EQU":
            return [self.randomness.random_choice(self.EQUIVALENT) for i in range(sequence_length)]
        if self.chosen_transformation_type == "CON":
            return [self.randomness.random_choice(self.CONTRACT) for i in range(sequence_length)]


    def generate_a_new_transformation(self, logging):
        self.logging = logging
        self.transformed_graph = deepcopy(self.dependencyGraph)
        self.chosen_transformation_type = self.randomness.random_choice(self.transformation_types)
        self.logging.add_log_text("[TransformationManager] Oracle: " + self.chosen_transformation_type)
        self.transformation_sequence = self.generate_transformation_sequence()
        self.apply_transformations_on_the_graph()
        return self.transformed_graph


    def apply_transformations_on_the_graph(self):
        self.logging.add_log_text("[TransformationManager] Trying to apply " + str(len(self.transformation_sequence)) + " transformations")
        self.logging.add_log_text("[TransformationManager] Applying the following transformations\n")
        for transformation in self.transformation_sequence:

            # Don't apply the disabled transformations
            if transformation in self.params["disable_transformation"]: 
                continue

            # Equivalent transformations
            if transformation == "EQU_NODE_ADD" and not self.params["only_queryfuzz"]:
                EQU_NODE_ADD(self.transformed_graph, self.randomness, self.logging, self.params, self.engine, self.full_logs, self.stats)
            if transformation == "EQU_NODE_REM" and not self.params["only_queryfuzz"]:
                EQU_NODE_REM(self.transformed_graph, self.randomness, self.logging, self.engine, self.params, self.full_logs, self.stats)
            if transformation == "EQU_EDGE_ADD" and not self.params["only_queryfuzz"]:
                EQU_EDGE_ADD(self.transformed_graph, self.randomness, self.params, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "EQU_EDGE_REM" and not self.params["only_queryfuzz"]:
                EQU_EDGE_REM(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "EQU_LEVEL_ADD" and not self.params["only_queryfuzz"]:
                EQU_LEVEL_ADD(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "EQU_LEVEL_ADD_2" and not self.params["only_queryfuzz"]:
                EQU_LEVEL_ADD_2(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "EQU_COLLAPSE_EDGE" and not self.params["only_queryfuzz"]:
                EQU_COLLAPSE_EDGE(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "EQU_FACT_INLINE" and not self.params["only_queryfuzz"]:
                EQU_FACT_INLINE(self.transformed_graph, self.randomness, self.logging, self.runTimeInfo, self.engine, self.full_logs, self.stats)
            if transformation == "ADD_EQU" and not self.params["disable_queryfuzz"]:
                ADD_EQU(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)
            if transformation == "MOD_EQU" and not self.params["disable_queryfuzz"]:
                MOD_EQU()
            if transformation == "REM_EQU" and not self.params["disable_queryfuzz"]:
                REM_EQU(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)


            # Expanding transformations
            if transformation == "EXP_EDGE_ADD" and not self.params["only_queryfuzz"]:
                EXP_EDGE_ADD(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "EXP_EDGE_REM" and not self.params["only_queryfuzz"]:
                EXP_EDGE_REM(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)
            if transformation == "EXP_NODE_ADD" and not self.params["only_queryfuzz"]:
                EXP_NODE_ADD(self.transformed_graph, self.randomness, self.logging, self.params, self.engine, self.stats)
            if transformation == "EXP_NODE_REM" and not self.params["only_queryfuzz"]:
                EXP_NODE_REM(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)
            if transformation == "MOD_EXP" and not self.params["disable_queryfuzz"]:
                MOD_EXP(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)

            # Contracting transformations
            if transformation == "CON_EDGE_ADD" and not self.params["only_queryfuzz"]:
                CON_EDGE_ADD(self.transformed_graph, self.randomness, self.params, self.logging, self.engine, self.stats)
            if transformation == "CON_EDGE_REM" and not self.params["only_queryfuzz"]:
                CON_EDGE_REM(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)
            if transformation == "CON_NODE_ADD" and not self.params["only_queryfuzz"]:
                CON_NODE_ADD(self.transformed_graph, self.randomness, self.logging, self.params, self.engine, self.stats)
            if transformation == "CON_NODE_REM" and not self.params["only_queryfuzz"]:
                CON_NODE_REM(self.transformed_graph, self.randomness, self.logging, self.engine, self.stats)
            if transformation == "CON_ADD_SELF_EDGE" and not self.params["only_queryfuzz"]:
                CON_ADD_SELF_EDGE(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)
            if transformation == "MOD_CON" and not self.params["disable_queryfuzz"]:
                MOD_CON(self.transformed_graph, self.randomness, self.logging, self.engine, self.full_logs, self.stats)


            self.logging.dump_log_file()