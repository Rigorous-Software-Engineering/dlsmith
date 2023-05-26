
def get_variables_with_types(all_vars_and_types):
    """
        input relation DDValTest2(a: Map<usize, string>, b: (bool, Set<u128>))
        -> ["a: Map<usize, string>", "b: (bool, Set<u128>)"]
    """
    all_vars_and_types = all_vars_and_types.replace(" ", "")
    variables_with_types = list()
    while True:
        print(all_vars_and_types)
        if all_vars_and_types.find(":") == -1: break
        location_of_first_colon = all_vars_and_types.find(":")
        var_name = all_vars_and_types[0:location_of_first_colon]
        var_type = ""
        if all_vars_and_types[location_of_first_colon + 1:].find(":") == -1:
            # No more colons left
            var_type = all_vars_and_types[location_of_first_colon + 1:]
            variables_with_types.append(var_name + ":" + var_type)
            break
        else:
            location_of_next_colon = all_vars_and_types[location_of_first_colon + 1:].find(":")
            location_of_last_comma = all_vars_and_types[0: location_of_next_colon+ location_of_first_colon].rfind(",")
            var_type = all_vars_and_types[location_of_first_colon + 1: location_of_last_comma]
            all_vars_and_types = all_vars_and_types[location_of_last_comma + 1:]
            variables_with_types.append(var_name + ":" + var_type)
    return variables_with_types



"""
    a: Map<usize, string>, b: (bool, Set<u128>)
"""
vars = get_variables_with_types("scc: entid_t, bindings: Ref<TS::Set64<tnid_t>>")
for var in vars:
    print(var)
 