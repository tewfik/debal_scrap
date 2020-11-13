import itertools


def flatten(nested_list):
    return itertools.chain.from_iterable(nested_list)
