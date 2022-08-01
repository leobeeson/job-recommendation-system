from collections import defaultdict


def nested_default_dict():
    return defaultdict(nested_default_dict)