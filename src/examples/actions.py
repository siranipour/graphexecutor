# Example file of actions

def add_one(num):
    return num + 1

def multiply_three(num):
    return num * 3

def action(add_one, multiply_three):
    """f: x |-> 1 + x + 3x = 1+4x
    """
    return add_one + multiply_three

def more_complicated_action(action, add_one):
    """ Returns (1+x)^2 + 1+4x = x^2 + 6x + 2
    """
    return action + add_one ** 2

def some_other_action(more_complicated_action, foo):
    return foo

def bar(baz):
    return baz

def v1(v2, v3):
    return 1

def v2(v1, v3):
    return 1

def v3(v1, v2):
    return 1

def cycle(v1, v2, v3):
    return 1