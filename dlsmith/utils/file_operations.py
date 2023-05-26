import os
import shutil
from termcolor import colored
import json
from shutil import copyfile

def create_fact_file_with_data(data, path):
    file  = open(path, "w")
    for row in data:
        file.write(row + "\n")
    file.close()


def delete_all_csv_files(dir):
    all_csv_files = list()
    for r, d, f in os.walk(dir):
        for file in f: 
            if file.find(".csv") != -1:
                all_csv_files.append(os.path.join(r, file))
    for file in all_csv_files: 
        os.remove(file)


def create_core_directory(temp_dir, server, core):
    core_dir = os.path.join(temp_dir, server, "core_" + str(core))
    if os.path.exists(core_dir):
        shutil.rmtree(core_dir)
    os.mkdir(core_dir)
    return core_dir


def create_server_directory(temp_dir, server):
    server_dir = os.path.join(temp_dir, server)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    # If the server directory exists, then leave it
    if not os.path.exists(server_dir):
        os.mkdir(server_dir)


def load_parameters(home):
    with open(os.path.join(home, "params.json")) as f:
        data = json.load(f)
    return data


def create_program_directory(path):
    if os.path.exists(path): shutil.rmtree(path)
    os.mkdir(path)
    return path


def create_file(data, path):
    file = open(path, "w")
    file.write(data)
    file.close()

def read_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
        for i in range(0,len(lines)):
            lines[i] = lines[i].replace("\t", "-")
    return lines

def read_souffle_output_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
        for i in range(0, len(lines)):
            lines[i] = lines[i].split("\t")
    return lines

def copy_fact_files(program_folder_path, seed_folder_path):
    for r, d, f in os.walk(seed_folder_path):
        for ff in f: 
            if ff.find(".facts") != -1:
                copyfile(os.path.join(seed_folder_path, ff), os.path.join(program_folder_path, ff))


def generate_ddlog_facts_file(program, output_node):
    file_text = "dump " + output_node.get_name() + ";"
    file_path = program.get_program_path() + "/facts.dat"
    create_file(file_text, file_path)


def delete_compiled_datalog_stuff(program, engine):
    if engine == "ddlog":
        dir_path = program.get_program_path() + "/rules_ddlog"
        shutil.rmtree(dir_path)


def pick_seed_program(randomness, path_to_engine_seed_folder):
    for r,d,f in os.walk(path_to_engine_seed_folder):
        picked_seed = randomness.random_choice(d)
        program_file_path = ""
        for rr,dd,ff in os.walk(os.path.join(path_to_engine_seed_folder, picked_seed)):
            for fff in ff: 
                if fff.find(".dl") != -1 or fff.find(".flg") != -1 or fff.find(".flix") != -1 or fff.find(".scl") != -1: 
                    program_file_path = fff
        if program_file_path == "": 
            return None, None
        else: 
            return os.path.join(path_to_engine_seed_folder, picked_seed), os.path.join(path_to_engine_seed_folder, picked_seed, program_file_path)


def export_buggy_instance_for_soundness(path_to_program, parent_temp_dir):
    # check if the soundness folder exists
    path_to_soundness_folder = os.path.join(parent_temp_dir, "soundness")
    number_of_directories = 0
    for r,d,f in os.walk(path_to_soundness_folder):
        number_of_directories = len(d)
        break
    if not os.path.exists(path_to_soundness_folder):
        print(colored("Creating a soundness folder at: ", "red"), end="")
        print(colored(parent_temp_dir, "red"))
        os.mkdir(path_to_soundness_folder)
    path_to_copied_db_instance = os.path.join(path_to_soundness_folder, str(number_of_directories))
    shutil.copytree(path_to_program, path_to_copied_db_instance, copy_function = shutil.copy)
    print(colored("Buggy program exported at: " + path_to_copied_db_instance, "red"))


def export_errored_out_instance(path_to_program, home, trasformed_program):
    main_temp_dir = os.path.join(home, "temp")
    path_to_fuzzed_error_instances = os.path.join(main_temp_dir, "errors", "Original_Instances")
    if trasformed_program:
        path_to_fuzzed_error_instances = os.path.join(main_temp_dir, "errors", "Transformed_Programs")
    print(colored("Creating Errors folder at: ", "red"), end="")
    print(path_to_fuzzed_error_instances)
    # check if the error folder exists
    path_to_error_folder = os.path.join(main_temp_dir, "errors")
    if not os.path.exists(path_to_error_folder):
        os.mkdir(path_to_error_folder)
    number_of_directories = 0
    for r, d, f in os.walk(path_to_fuzzed_error_instances):
        number_of_directories = len(d)
        break
    if not os.path.exists(path_to_fuzzed_error_instances):
        os.mkdir(path_to_fuzzed_error_instances)
    path_to_copied_program = os.path.join(path_to_fuzzed_error_instances, str(number_of_directories))
    shutil.copytree(path_to_program, path_to_copied_program, copy_function=shutil.copy)
    print(colored("Errored out database instance's exported at: " + path_to_copied_program, "red"))