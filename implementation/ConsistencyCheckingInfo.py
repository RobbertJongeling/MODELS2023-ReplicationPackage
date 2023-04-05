# Format: {FromLocation, ToLocation, UncertaintyType, thing_type}
def get_pl_example_propagation_directions():
    return [
        {"from": "RefM", "to": "RefRD", "uncType": "O", "thing_type": "Component"},
        {"from": "RefM", "to": "RefRD", "uncType": "A", "thing_type": "Component"},
        {"from": "RefM", "to": "PM", "uncType": "O", "thing_type": "Component"},
        {"from": "RefM", "to": "PM", "uncType": "P", "thing_type": "Component"},
        {"from": "RefM", "to": "PM", "uncType": "A", "thing_type": "Component"},
        {"from": "PM", "to": "PMRD", "uncType": "O", "thing_type": "Component"},
        {"from": "PM", "to": "PMRD", "uncType": "A", "thing_type": "Component"},
        {"from": "RefRD", "to": "PMRD", "uncType": "O", "thing_type": "Connection"},
        {"from": "RefRD", "to": "PMRD", "uncType": "P", "thing_type": "Connection"},
        {"from": "RefRD", "to": "PMRD", "uncType": "A", "thing_type": "Connection"}
    ]


# Here, consistency means that "occurrence in loc_a IMPLIES occurrence in loc_b"
def get_pl_example_consistency_rules():
    return [
        {"loc_a": "PM", "loc_b": "RefM", "thing_type_a": "Component", "thing_type_b": "Component", "cons_type": "Implies"},  # up
        {"loc_a": "RefRD", "loc_b": "RefM", "thing_type_a": "Component", "thing_type_b": "Component", "cons_type": "Implies"},  # left
        {"loc_a": "PMRD", "loc_b": "RefRD", "thing_type_a": "Component", "thing_type_b": "Component", "cons_type": "Implies"},  # up
        {"loc_a": "PMRD", "loc_b": "RefRD", "thing_type_a": "Connection", "thing_type_b": "Connection", "cons_type": "Implies"},  # up
        {"loc_a": "PMRD", "loc_b": "PM", "thing_type_a": "Component", "thing_type_b": "Component", "cons_type": "Implies"}  # left
    ]


# Here, consistency means that "occurrence in loc_a BI-IMPLIES occurrence in loc_b"
def get_sysml_example_consistency_rules():
    return [
        {"loc_a": "SysML", "loc_b": "CPP", "thing_type_a": "Component", "thing_type_b": "Repository", "cons_type": "Equals"},
        {"loc_a": "SysML", "loc_b": "CPP", "thing_type_a": "State", "thing_type_b": "Class", "cons_type": "Equals"},
        {"loc_a": "SysML", "loc_b": "CPP", "thing_type_a": "Event", "thing_type_b": "Case", "cons_type": "Equals"}
    ]


# sort according to inconsistency priority: !, none, ~, ?, ??
def get_sorted_inconsistencies(inconsistencies):
    sorted_inconsistencies = []
    # I couldn't find quickly enough how to do nice sorting so I did it the stupid way
    prios = ['??', '?', '~', '', '!']
    for icon in prios:
        for incons in inconsistencies:
            if incons['prio'] == icon:
                sorted_inconsistencies.insert(0, incons)

    return sorted_inconsistencies


