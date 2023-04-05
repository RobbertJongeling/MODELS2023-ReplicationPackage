import argparse

from textx import metamodel_from_file
from Helpers import *
from LookupTables import *
from ConsistencyCheckingInfo import *
import copy
# HACK TO GET AROUND TypeError when doing DeepCopy. This hack was completely written by ChatGPT!
import copyreg
import io


def exclude_text_io_wrapper(obj):
    return reconstruct_text_io_wrapper, ()


def reconstruct_text_io_wrapper():
    return io.StringIO()
# END HACK


# this method returns a list of propagated uncertainties.
# it does not yet "and" double uncertainties.
def get_propagated_uncertainties(estimated_uncertainties, propagation_rules, architecture):
    propagated_uncertainties = []

    for u in estimated_uncertainties:
        if u.uOperator != "!":
            for pr in propagation_rules:
                if propagation_rule_applicable_to_uncertainty_expression(u, pr, architecture):
                    to_loc = pr['to']
                    el = u.uElement
                    if exists_in(architecture, el, to_loc):
                        # If the other side has also the same uncertainty already, don't propagate
                        other_element = get_element_in_diagram(el, get_diagram(architecture, to_loc))
                        other_exp = get_uncertainty_expression_for_element(to_loc, other_element, estimated_uncertainties)
                        if not (other_exp and other_exp.actor == u.actor and other_exp.uOperator == u.uOperator):

                            # Normally, deepcopy fails due to TypeError: cannot serialize '_io.TextIOWrapper' object
                            copyreg.pickle(io.TextIOWrapper, exclude_text_io_wrapper)
                            propagated_expression = copy.deepcopy(u)
                            propagated_expression.uElement.uElementLocation = to_loc
                            # Add rationale to existing, or create new object
                            propagated_expression.rationale += " -> PROPAGATED FROM: " + uncertainty_expression_to_string(u)

                            propagated_uncertainties.append(propagated_expression)

    return propagated_uncertainties


def propagation_rule_applicable_to_uncertainty_expression(u_expr, prop_rule, architecture):
    if u_expr.uElement.uElementLocation == prop_rule['from']:
        if u_expr.uType == prop_rule['uncType']:
            if get_element_type(u_expr.uElement, architecture) == prop_rule['thing_type']:
                return True
    return False


# given an uncertainElement and an architecture,
# returns the ElementType of the Element with the same ID in the architecure
def get_element_type(uncertain_element, architecture):
    for d in architecture.diagrams:
        if d.name == uncertain_element.uElementLocation:
            element = get_element_in_diagram(uncertain_element, d)
            return element.type if element else None

    # if not found, we get here
    return None


def get_diagram(arch, diag_name):
    for diagram in arch.diagrams:
        if diagram.name == diag_name:
            return diagram

    return None

def get_element_in_diagram(element, diagram):
    # find FQN of elements in diagram contents
    search_in = diagram
    nr_levels = len(element.uElementIDs)
    for level in range(0, nr_levels):
        for content_element in search_in.contents:
            if content_element.name == element.uElementIDs[level]:
                # if we are at the end, then we are dome, else, search one level deeper
                if level == nr_levels - 1:
                    return content_element
                else:
                    search_in = search_in.contents
                    break
    return None


# Note: searched_element is an UncertaintElement whereas elements from the architecture are Elements.
def exists_in(architecture, searched_element, location):
    if searched_element.uElementIDs:  # No point to look for propagation of non-elements
        for diagram in architecture.diagrams:
            if diagram.name == location:
                return get_element_in_diagram(searched_element, diagram) is not None
    return False


# takes a list of estimated and propagated uncertainties.
# in cases where there was only a propagated uncertainty, that one is taken
# in cases where there was both an estimated and propagated uncertainty, they are "and-ed"
# in cases where there was only an estimated uncertainty, that one is taken
# the method thus returns a list of all uncertainties after complete propagation
def get_anded_uncertainties(estimated_uncertainties, propagated_uncertainties):
    to_return = []
    anded = []
    # for each estimated, see if there is also a propagated. If so, "and" them, else just add
    for e in estimated_uncertainties:
        for p in propagated_uncertainties:
            if e.actor == p.actor and is_same_unc_type_about_same_thing(e, p):
                to_return.append(get_anded_uncertainty(e, p))
                # mark "e" and "p" as anded so that we do not add them once more later on
                anded.append(e)
                anded.append(p)
        # if we get here and we didn't "and" any p, then there was only the estimated, so we add that one
        if e not in anded:
            to_return.append(e)

    # now we also have to add those cases where there was only a p, but no corresponding e. These are the remaining P's
    for p in propagated_uncertainties:
        if p not in anded:
            to_return.append(p)

    return to_return


def is_same_unc_type_about_same_thing(u1, u2):
    u1e = u1.uElement
    u2e = u2.uElement
    return u1.uType == u2.uType and \
           have_equal_element_ids(u1e, u2e) and \
           u1e.uElementLocation == u2e.uElementLocation and \
           ((u1e.uElementProperty and u2e.uElementProperty and u1e.uElementProperty == u2e.uElementProperty) or
            (not u1e.uElementProperty and not u2e.uElementProperty))


def have_equal_element_ids(e1, e2):
    if e1.uElementIDs and e2.uElementIDs:
        l1 = len(e1.uElementIDs)
        l2 = len(e2.uElementIDs)
        if l1 == l2:
            for i in range(0, l1):
                if e1.uElementIDs[i] != e2.uElementIDs[i]:
                    return False
            # if no reason for False, then true
            return True

    # if not elementIDs or not same length, false
    return False


# e: estimated uncertainty and p: propagated uncertainty
def get_anded_uncertainty(e, p):
    a = copy.deepcopy(e)
    a.uOperator = get_anded_operators(e.uOperator, p.uOperator)
    a.rationale += " ANDED: " + uncertainty_expression_to_string(e) + " AND " + uncertainty_expression_to_string(p)
    return a


# derived_uncertainties is a list of all estimated and propagated (and anded) uncertainties.
# now we check to find the same uncertainties on the same things by different actors and merge them
def get_merged_uncertainties(derived_uncertainties):
    merged_uncertainties = []
    duplicates = []

    # first we make lists out of all uncertainties, so that we have 1 list per type per thing
    for i in range(0, len(derived_uncertainties)):
        u1 = derived_uncertainties[i]
        # if we already found u1, we don't look further
        if not any(u1 in sublist for sublist in duplicates):
            u1_duplicates = [u1]
            for j in range(i + 1, len(derived_uncertainties)):
                u2 = derived_uncertainties[j]
                if is_same_unc_type_about_same_thing(u1, u2):
                    # now we found that u1 and u2 are duplicates, to be merged
                    u1_duplicates.append(u2)

            duplicates.append(u1_duplicates)

    # now we have the list of lists of duplicates
    # for each list holds, if it's of length >1, we need to merge the opinions
    for to_merge in duplicates:
        if len(to_merge) == 1:
            merged_uncertainties.append(to_merge[0])
        elif len(to_merge) > 1:
            # Normally, deepcopy fails due to TypeError: cannot serialize '_io.TextIOWrapper' object
            copyreg.pickle(io.TextIOWrapper, exclude_text_io_wrapper)
            merged_uncertainty = copy.deepcopy(to_merge[0])
            merged_uncertainty.uOperator = get_average_uncertainty(to_merge)
            merged_uncertainty.actor = "*"
            merged_uncertainty.rationale = "MERGED " + uncertainty_expression_to_string(to_merge[0])
            for i in range(1, len(to_merge)):
                merged_uncertainty.rationale += " WITH " + uncertainty_expression_to_string(to_merge[i])
            merged_uncertainties.append(merged_uncertainty)

    return merged_uncertainties


def is_already_in_list(element, list_of_inconsistencies):
    for incons in list_of_inconsistencies:
        if "left" in incons.keys() and incons["left"][0] == element.name:
            return True

    return False


# This implementation turns out to be fairly similar to the initial propagation, naturally
def find_inconsistencies(estimated_uncertainties, merged_uncertainties, consistency_rules, architecture):
    inconsistencies = []
    for d in architecture.diagrams:
        flattened_elements = get_all_elements_in_diagram(d)
        for e in flattened_elements:
            for cr in consistency_rules:
                # if e already in inconsistencies, we do not go furhter
                if cr['cons_type'] == "Implies" or (cr['cons_type'] == "Equals" and not is_already_in_list(e, inconsistencies)):
                    side_of_consistency_rule = get_side_of_consistency_rule_applicable_to_element(d, e, cr)
                    if side_of_consistency_rule:
                        other_side = 'loc_a' if side_of_consistency_rule == 'loc_b' else 'loc_b'
                        e_uncertainty = get_uncertainty_expression_for_element(d.name, e, merged_uncertainties)
                        e_op = e_uncertainty.uOperator if e_uncertainty and e_uncertainty.uType == "O" else ""
                        counterpart = get_counterpart(e, cr, side_of_consistency_rule, architecture)
                        # an uncertainty is either a case where no counterpart is found (explicit/naive)
                        if not counterpart:
                            inconsistencies.append({"prio": e_op, "type": "RULE", "not": cr['cons_type'], "left_unc": e_op,
                                                    "left": get_fqn(e), "left_in": d.name, "right_unc": "", "right": get_fqn(e),
                                                    "right_in": cr[other_side]})
                        else:  # or a case where the counterpart has occurrence uncertainty (uncovered)
                            # for implies, if the uncertainty in the left is "!" than it becomes an uncertainty, but
                            # only if there is a non-bang and non-none uncertainty on the original too.
                            # for equals, if either side is bang and the other non-bang and non-none, it becomes one.
                            # finally, when the uncertainty on original and counterpart is the same,
                            # we do not consider this as an uncovered inconsistency
                            c_uncertainty = get_uncertainty_expression_for_element(cr[other_side], counterpart,
                                                                                   merged_uncertainties)

                            # if not c_uncertainty, then c_op = e_op, else we change.
                            c_op = ""
                            if c_uncertainty and c_uncertainty.uType == 'O':
                                c_op = c_uncertainty.uOperator

                            # for implies, if the uncertainty on the right side is none, we are not interested.
                            if c_op != "":
                                e_est_had_bang = had_estimated_bang(e_uncertainty, estimated_uncertainties)
                                c_est_had_bang = had_estimated_bang(c_uncertainty, estimated_uncertainties)

                                original_had_bang = (e_est_had_bang and is_uncertain(c_op)) or \
                                                    (cr['cons_type'] == "Equals" and c_est_had_bang and is_uncertain(e_op))

                                # first we check unequal operators and bang on merged uncertainties
                                # that is then "orred" with cases where we had bangs in the original
                                if (c_op != e_op and not ((c_op == "!" and e_op == "") or (c_op == "" and e_op == "!"))) or original_had_bang:

                                    if original_had_bang:
                                        incons_uncert = "!"
                                        if c_est_had_bang:
                                            c_op = "!"
                                        if e_est_had_bang:
                                            e_op = "!"

                                    elif cr['cons_type'] == "Implies":
                                        incons_uncert = get_combined_implies_operators(e_op, c_op)
                                    else:
                                        incons_uncert = get_combined_equals_operators(e_op, c_op)

                                    inconsistencies.append({"prio": incons_uncert,
                                                            "type": "UNC.", "not": cr['cons_type'],
                                                            "left_unc": e_op, "left": get_fqn(e), "left_in": d.name,
                                                            "right_unc": c_op, "right": get_fqn(e), "right_in": cr[other_side]})

    return inconsistencies


def had_estimated_bang(u_exp, estimated_uncerts):
    if u_exp:
        for e_unc in estimated_uncerts:
            if u_exp.uElement.uElementLocation == e_unc.uElement.uElementLocation and\
                    have_equal_element_ids(u_exp.uElement, e_unc.uElement) and e_unc.uOperator == "!":
                return True

    return False


# return true if uncertainty operator is not none and not bang
def is_uncertain(uncertainty_operator):
    return uncertainty_operator != "" and uncertainty_operator != "!"


# flatten
def get_all_elements_in_diagram(diagram):
    elements = []
    for element in diagram.contents:
        elements += get_all_elements_in_element(element)
    return elements


def get_all_elements_in_element(element):
    elements = [element]
    for el in element.contents:
        elements += get_all_elements_in_element(el)
    return elements


# check if this uncertainty is relevant for this consistency rule, if so, return the "side" of its relevance
# applicable means that the thing_types correspond and the the uncertainty is in a relevant location of the rule
# the location is relevant is on either side, in case of EQUALS, or on the left side of an IMPLIES
def get_side_of_consistency_rule_applicable_to_element(diagram, element, consistency_rule):
    # either way check loc_a, and if rules is of type Equals, then also check loc_b
    if consistency_rule['loc_a'] == diagram.name and element.type == consistency_rule['thing_type_a']:
        return 'loc_a'
    elif consistency_rule['cons_type'] == "Equals" and consistency_rule['loc_b'] == diagram.name and element.type == consistency_rule['thing_type_b']:
        return 'loc_b'
    else:
        return None


# returns the uncertainty associated with this element if any, else returns empty
def get_uncertainty_expression_for_element(diagram_name, element, list_of_uncertainties):
    for u in list_of_uncertainties:
        ue = u.uElement
        if ue.uElementIDs and diagram_name == ue.uElementLocation and ue.uElementIDs[0] == element.name:
            return u

    return None


# Check if uncertain element and architecture element have the same ID
def ua_have_equal_element_ids(ue, ae):
    fqn = get_fqn(ae)

    if ue.uElementIDs:
        ueids = ue.uElementIDs
        if len(ueids) == len(fqn):
            for i in range(0, len(ueids)):
                if ueids[i] != fqn[i]:
                    return False
            return True

    return False


# constructs an #FQN of ae as list of element names
def get_fqn(ae):
    fqn = [ae.name]
    parent = ae.parent
    while parent:
        if parent.type != 'Diagram':
            fqn += [parent.name]
            parent = parent.parent
        else:
            parent = None

    return fqn


# returns None if no counterpart coud be found, or an element if it can be found
# counterpart means an element with the same name and needed type in the "to" diagram of the consistency rule
# here we do not consider hierarchy
def get_counterpart(element_to_find, consistency_rule, side_of_rule, architecture):
    if side_of_rule:
        if side_of_rule == 'loc_a':
            side_to_check = 'loc_b'
            type_to_find = consistency_rule['thing_type_b']
        elif side_of_rule == 'loc_b':
            side_to_check = 'loc_a'
            type_to_find = consistency_rule['thing_type_a']
        else:
            return None

    # the consistency check should check occurrence in the other location of the artefact
    for d in architecture.diagrams:
        if d.name == consistency_rule[side_to_check]:
            for element in get_all_elements_in_diagram(d):
                if element.name == element_to_find.name and element.type == type_to_find:
                    return element

    return None


def main():
    # for demo run with sysml_example (1) or pl_example (2)
    uncertainty_mm = metamodel_from_file("uncertainty.tx")
    architecture_mm = metamodel_from_file("architecture.tx")

    debug_mode = True  # to easier test, print only occurrence uncertainties
    demo = 1
    if demo == 1:
        estimations_file = "Example1-SysML-CPP.uncertainty"
        example_model = architecture_mm.model_from_file("SysMLexample.arch")
        propagation_directions = []
        consistency_rules = get_sysml_example_consistency_rules()

    if demo == 2:
        estimations_file = "Example2-ProductLine.uncertainty"
        example_model = architecture_mm.model_from_file("PLexample.arch")
        # TODO: for any real playing around, we must be able to read a "configuration" that tells us
        #  (i) in what direction to propagate, and (ii) what the consistency rules are. For now, I hardcode them.
        propagation_directions = get_pl_example_propagation_directions()
        consistency_rules = get_pl_example_consistency_rules()

    # Just checking that we can read the input
    estimated_uncertainties_file = uncertainty_mm.model_from_file(estimations_file)
    print(">>>>> ESTIMATED >>>>>")
    print(uncertainty_file_to_string(estimated_uncertainties_file))

    estimated_uncertainties = estimated_uncertainties_file.uncertaintyExpressions

    # Uncertainties after propagation
    print("\n>>>>> Propagated uncertainties >>>>>\n")
    propagated_uncertainties = get_propagated_uncertainties(estimated_uncertainties,
                                                            propagation_directions, example_model)
    propagated_uncertainties = sorted(propagated_uncertainties, key=lambda u: u.uElement.uElementLocation)
    for uncertainty in propagated_uncertainties:
        if not(debug_mode and not uncertainty.uType == 'O'):
            print(uncertainty_expression_to_string(uncertainty))

    # Uncertainties after "and-ing"
    # After propagation, we need to "and" cases where we have an estimated + propagated opinion
    # if they are on the same thing, of the same uncertainty type, by the same actor
    print("\n>>>>> Derived uncertainties after propagation and 'and-ing' >>>>>\n")
    derived_uncertainties = get_anded_uncertainties(estimated_uncertainties, propagated_uncertainties)
    derived_uncertainties = sorted(derived_uncertainties, key=lambda u: u.uElement.uElementLocation)
    for uncertainty in derived_uncertainties:
        if not(debug_mode and not uncertainty.uType == 'O'):
            print(uncertainty_expression_to_string(uncertainty))

    # Uncertainties after "merging" multiple uncertainties on the same elements by different actors
    print("\n>>>>> Uncertainties after 'merging' double ones from different actors >>>>>\n")
    merged_uncertainties = get_merged_uncertainties(derived_uncertainties)
    merged_uncertainties = sorted(merged_uncertainties, key=lambda u: u.uElement.uElementLocation)
    for uncertainty in merged_uncertainties:
        if not(debug_mode and not uncertainty.uType == 'O'):
            print(uncertainty_expression_to_string(uncertainty))

    print("\n>>>>> Detected inconsistencies >>>>>")
    inconsitencies = find_inconsistencies(estimated_uncertainties, merged_uncertainties, consistency_rules, example_model)
    print("these do not hold:")
    # this is not sorting according to our rules, but it took too long to figure out how to sort "!" above ""
    # so I did that in the ugly way
    sorted_inconsistencies = get_sorted_inconsistencies(inconsitencies)
    for inconsistency in sorted_inconsistencies:
        print(inconsistency_to_string(inconsistency))

    print("Done")


if __name__ == "__main__":
    main()
