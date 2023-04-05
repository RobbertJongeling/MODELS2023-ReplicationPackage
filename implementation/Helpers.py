def element_to_string(element):
    attributes_string = '{'

    if element.cps:
        attributes_string += 'connectionProperties: {'
        for kvp in element.cps.kvs:
            attributes_string += kvp.key + '=' + kvp.value + ', '
        attributes_string = attributes_string[:-2]  # ugly but just to remove the last sep
        attributes_string += '}, '

    attributes_string += 'propertyValues: {'
    for kvp in element.pvs.kvs:
        attributes_string += kvp.key + '=' + kvp.value + ', '
    attributes_string = attributes_string[:-2]  # ugly but just to remove the last sep
    attributes_string += '}'

    attributes_string += '}'

    return '\t\t' + element.name + ':' + element.type + attributes_string


def kvps_to_string(kvps):
    pvs = kvps.key + '=' + kvps.value + ', '
    pvs = pvs[:-2]  # ugly but just to remove the last sep
    return pvs


def diagram_to_string(diagram):
    to_return = diagram.name + ':' + diagram.type + '{'
    to_return += '\tcontents: {'
    for element in diagram.contents:
        to_return += element_to_string(element)
    to_return += '\t},'

    pvs = 'propertValues: {'
    pvs += kvps_to_string(diagram.pvs.kvs)
    pvs += '}'

    to_return += '\t' + pvs
    to_return += '}'
    return to_return


def uncertainty_expression_to_string(u_expr):
    u_elmnt = ""
    if u_expr.uElement:
        elmnt_id = ""
        for e in u_expr.uElement.uElementIDs:
            elmnt_id += e + '@'
        prop = ""
        if u_expr.uElement.uElementProperty:
            prop = '#' + u_expr.uElement.uElementProperty
        u_elmnt = '(' + elmnt_id + u_expr.uElement.uElementLocation + prop + ')'

    rationale = ""
    if u_expr.rationale:
        rationale = ":" + u_expr.rationale

    return u_expr.actor + u_expr.uOperator + u_expr.uType + u_elmnt + rationale


def uncertainty_file_to_string(uncertainty_file):
    to_return = ''
    for u_expr in uncertainty_file.uncertaintyExpressions:
        to_return += uncertainty_expression_to_string(u_expr) + '\n'

    return to_return


def name_list_to_string(name_list):
    to_return = ''
    for n in name_list:
        to_return += n + '@'
    return to_return


def inconsistency_to_string(inconsistency):
    arrowtype = " --> " if inconsistency['not'] == "Implies" else " <-> "
    return "[" + inconsistency['prio'] + ']' + inconsistency['type'] + " " + \
           inconsistency['left_unc'] + name_list_to_string(inconsistency['left']) + inconsistency['left_in'] + arrowtype + \
           inconsistency['right_unc'] + name_list_to_string(inconsistency['right']) + inconsistency['right_in']
