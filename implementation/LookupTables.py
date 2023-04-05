# there should be some way to do "switch" but I couldn't figure it out fast enough
# U.soil> !c.andTable()
#  _ ~ ? $
#  ~ ? ? $
#  ? ? $ $
#  $ $ $ $
def get_anded_operators(op_1, op_2):
    if op_1 == '??':
        return '??'
    elif op_1 == '?':
        return '??' if op_2 == '?' or op_2 == '??' else '?'
    elif op_1 == '~':
        return '??' if op_2 == '??' else '?' if op_2 == '?' or op_2 == '~' else '~'
    elif op_1 == '!':  # just added for completeness, but we don't calculate with "!" we only use it for prioritization
        return op_2


# This is for combining the uncertainties on an inconsistency
# it should be '!' if either is '!'
# otherwise 'implies' table
# U.soil> !c.impliesTable()
# _ ~ ? $
# _ ~ ? $
# _ ~ ? $
# _ ~ ? $
def get_combined_implies_operators(op_1, op_2):
    if op_1 == "!" or op_2 == "!":
        return "!"
    else:
        return op_2


# U.soil > !c.equivTable()
# _ ~ ? $
# ~ ~ ? $
# ? ? ~ $
# $ $ $ ?
def get_combined_equals_operators(op_1, op_2):
    if op_1 == "!" or op_2 == "!":
        return "!"
    if op_1 == "":
        return op_2
    if op_2 == "":
        return op_1
    else:
        if op_1 == "~":
            if op_2 == '??':
                return '??'
            if op_2 == '?':
                return '?'
            if op_2 == '~':
                return '~'

        if op_1 == "?":
            if op_2 == '??':
                return '??'
            if op_2 == '?':
                return '~'
            if op_2 == '~':
                return '?'

        if op_1 == "??":
            if op_2 == '??':
                return '?'
            if op_2 == '?':
                return '??'
            if op_2 == '~':
                return '??'


def get_implies_table(left_op, right_op):
    return left_op


# I wrote it out here for readability, since we don't calculate with !, I leave it out here
# U.soil> !c.abfTable()
#  _ ~ ? $
#  ~ ~ ? ?
#  ? ? ? $
#  $ ? $ $
# U.soil> !c.wbfTable()
#  _ ~ ? $
#  ~ ~ ? ?
#  ? ? ? $
#  $ ? $ $
def get_average_operator(op_1, op_2):
    # at this point, we don't want to calculate yet with '!', so we just keep the associated uncertainty of the other
    if op_1 == '!':
        return op_2
    if op_2 == '!':
        return op_1

    if op_1 == '??':
        if op_2 == '??':
            return '??'
        if op_2 == '?':
            return '??'
        if op_2 == '~':
            return '?'

    if op_1 == '?':
        if op_2 == '??':
            return '??'
        if op_2 == '?':
            return '?'
        if op_2 == '~':
            return '?'

    if op_1 == '~':
        if op_2 == '??':
            return '?'
        if op_2 == '?':
            return '?'
        if op_2 == '~':
            return '~'


# this method takes a list of uncertainties to be merged
# it returns a single merged opinion using weighted belief fusion (which in our case is just average)
def get_average_uncertainty(uncertainties_list):
    return get_average_operator(uncertainties_list[0].uOperator, uncertainties_list[1].uOperator)
