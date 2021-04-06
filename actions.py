# Example file of actions

def add_one(num):
    return num + 1

def multiply_three(num):
    return num * 3

def action(add_one, multiply_three):
    """f: x |-> 1 + x + 3x
    """
    return add_one + multiply_three

def more_complicated_action(action, add_one):
    return action + add_one ** 2

def some_other_action(more_complicated_action, foo):
    return foo

def bar(baz):
    return baz