from dlsmith.utils.file_operations import create_file, read_file
from termcolor import colored
import os
import string

def generate_comparison_queries(dependencyGraph, path_to_original_result, path_to_transformed_result, 
                                    oracle, program, transformation_number, params, engine):
    
    # Type declerations
    type_decls = ""
    for decl in dependencyGraph.get_parsed_graph().get_type_declerations():
        type_decls += decl + "\n"

    # original result declaration string
    orig_result_decl_string = ".decl orig_result("  
    
    if len(dependencyGraph.get_output_node().get_variables()) == 0:
        orig_result_decl_string += ")"
    else:
        for i, var in enumerate(dependencyGraph.get_output_node().get_variables()):
            if engine == "ddlog" or engine == "formulog" or engine == "scallop" or engine == "scallop_compiler":
                # we consider everything a string when we are dealing with DDLOG
                orig_result_decl_string += string.ascii_uppercase[i] + ":" + "symbol" + ", "
            elif var.get_type() == "integer": 
                orig_result_decl_string += string.ascii_uppercase[i] + ":number" + ", "
            elif var.get_type() == "string":
                orig_result_decl_string += string.ascii_uppercase[i] + ":symbol" + ", "
            else: 
                orig_result_decl_string += string.ascii_uppercase[i] + ":" + var.get_type() + ", "
        orig_result_decl_string = orig_result_decl_string[:-2] + ")"

    # import original results
    orig_result_input = '.input orig_result(filename="' + path_to_original_result + '")'
    # Transformed result declaration string
    trans_result_decl_string = orig_result_decl_string.replace("orig_result", "trans_result")
    # import transformed result
    trans_result_input = '.input trans_result(filename="' + path_to_transformed_result + '")'
    variable_string = "".join(i + "," for i in string.ascii_lowercase[:len(dependencyGraph.get_output_node().get_variables())])[:-1]
    # Comparison query 1
    comp_decl_string_1 = orig_result_decl_string.replace("orig_result", "comparison_result1")
    query_1 = "comparison_result1(" + variable_string + ") :- orig_result(" + variable_string + ") , !trans_result(" + variable_string + ")." 
    # Comparison query 2
    comp_decl_string_2 = orig_result_decl_string.replace("orig_result", "comparison_result2")
    query_2 = "comparison_result2(" + variable_string + ") :- trans_result(" + variable_string + ") , !orig_result(" + variable_string + ")." 

    # Final query string
    query_file_string = ""
    query_file_string += "\n\n// Type decls\n" + type_decls
    query_file_string += "\n\n// Original result\n" + orig_result_decl_string + "\n" + orig_result_input
    query_file_string += "\n\n// Transformation result\n" + trans_result_decl_string + "\n" + trans_result_input
    query_file_string += "\n\n\n\n// Comparison query 1\n" + comp_decl_string_1 + "\n" + query_1
    query_file_string += "\n\n// Comparison query 2\n" + comp_decl_string_2 + "\n" + query_2
    query_file_string += "\n\n\n\n.output comparison_result1\n.output comparison_result2"

    comparison_query_path = ""
    if oracle == "EQU":
        query_file_string += "\n\n\n// EQU QUERY \n// comparison_results1 should always be empty \n// comparison_results2 should always be empty\n"
        comparison_query_path = os.path.join(program.get_program_path(), "EQU_" + str(transformation_number) + ".dl" )
        create_file(query_file_string, comparison_query_path)
    if oracle == "EXP":
        query_file_string += "\n\n\n// EXP QUERY \n// comparison_results1 SHOULD ALWAYS be empty. Both in case of EXP_EQU and strict EXP transformations" \
                        "  \n// comparison_results2 will be empty in case of EXP_EQU transformation and will not be empty in case of strict EXP transformation\n"
        comparison_query_path = os.path.join(program.get_program_path(), "EXP_" + str(transformation_number) + ".dl")
        create_file(query_file_string, comparison_query_path)
    if oracle == "CON":
        query_file_string += "\n\n\n// CON QUERY \n// comparison_result1 will NOT be empty in case of strict CON transformation. It will be empty in case of EQU_CON transformation" \
                        "  \n// comparison_results2 SHOULD ALWAYS BE empty. Both in case of CON_EQU and strict CON transformations\n"
        comparison_query_path = os.path.join(program.get_program_path(), "CON_" + str(transformation_number) + ".dl")
        create_file(query_file_string, comparison_query_path)
    return comparison_query_path


def compare_results(original_result, transformed_result, oracle, dependencyGraph, transformation_number, 
                        original_program, params, engine):
    """
        original_result: Path to original csv result
        transformed_result: Path to transformed csv result
    """
    def print_results():
        len_orig_result = len(read_file(original_result))
        len_trans_result = len(read_file(transformed_result))

        if oracle == "EQU": print("     [" + str(transformation_number) + "]  [" + colored(oracle, "yellow", attrs=["bold"]) + "] ", end="")
        if oracle == "EXP": print("     [" + str(transformation_number) + "]  [" + colored(oracle, "green", attrs=["bold"]) + "] ", end="")
        if oracle == "CON": print("     [" + str(transformation_number) + "]  [" + colored(oracle, "red", attrs=["bold"]) + "] ", end="")
        
        if oracle == "EQU":
            if len_orig_result == len_trans_result:
                print(str(len_orig_result) + " == " + str(len_trans_result) + " ", end="")
                print(colored(u'\u2714', "green", attrs=["bold"]), end="")

            else:
                print(str(len_orig_result) + " != " + str(len_trans_result) + " ", end="")
                print(colored(u'\u274c', "red", attrs=["bold"]), end="")

        if oracle == "EXP":
            if len_orig_result <= len_trans_result:
                print(str(len_orig_result) + " <= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u2714', "green", attrs=["bold"]), end="")
            else:
                print(str(len_orig_result) + " ! >= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u274c', "red", attrs=["bold"]), end="")

        if oracle == "CON":
            if len_orig_result >= len_trans_result:
                print(str(len_orig_result) + " >= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u2714', "green", attrs=["bold"]), end="")
            else:
                print(str(len_orig_result) + " ! <= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u274c', "red", attrs=["bold"]), end="")

        if len_orig_result != len_trans_result:
            return True
        else:
            return False
   
    new_result = print_results()
    # Generate comparison query
    comparison_query_path = generate_comparison_queries(dependencyGraph=dependencyGraph, path_to_original_result=original_result, 
                            path_to_transformed_result=transformed_result, oracle=oracle, program=original_program, 
                            transformation_number=transformation_number, params=params, engine=engine)

    # Run comparison query
    command = "timeout 500s " + params["path_to_souffle"] + " -w --output-dir=" + original_program.get_program_path() + " " + comparison_query_path
    os.system(command)

    # Compare results
    path_to_compairson_result_1 = os.path.join(original_program.get_program_path(), "comparison_result1.csv")
    path_to_compairson_result_2 = os.path.join(original_program.get_program_path(), "comparison_result2.csv")
    # If both the files exist then we proceed
    if os.path.exists(path_to_compairson_result_1) and os.path.exists(path_to_compairson_result_2):
        comp_data_1 = read_file(path_to_compairson_result_1)
        comp_data_2 = read_file(path_to_compairson_result_2)
        print("   Comparison query:", end="")
        if oracle == "CON":
            # For CON we need to check that the result of the transformed query is contained the original query
            # The second query should always be empty
            if len(comp_data_2) != 0:
                print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                os.remove(comparison_query_path)
                return 1
            else:
                print(" " + colored(u'\u2714', "green", attrs=["bold"]), end="")
        if oracle == "EQU":
            # Both comparison files should be empty
            if len(comp_data_1) != 0 or len(comp_data_2) != 0:
                print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                os.remove(comparison_query_path)
                return 1
            else:
                print(" " + colored(u'\u2714', "green", attrs=["bold"]), end="")
        if oracle == "EXP":
            # For EXP, we need to check that the first query is empty
            if len(comp_data_1) != 0:
                print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                os.remove(comparison_query_path)
                return 1
            else:
                print(" " + colored(u'\u2714', "green", attrs=["bold"]), end="")

    # Print if we were able to change the result
    if new_result: print("  " + colored("New Result", "white", "on_green", attrs=["bold"]))
    else: print("")
    # Delete comparison results file even if the comparison was unsuccessful. 
    # No need to communicate the failure upstream.
    os.remove(comparison_query_path)
    try: 
        os.remove(os.path.join(original_program.get_program_path(), "comparison_result1.csv"))
        os.remove(os.path.join(original_program.get_program_path(), "comparison_result2.csv"))
    except:
        print("FAILED TO DELETE")
