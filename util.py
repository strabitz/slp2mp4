# Misc. utilities

import subprocess


def update_dict(d1: dict, d2: dict):
    for k, v in d2.items():
        if isinstance(v, dict):
            if k not in d1:
                d1[k] = {}
            update_dict(d1[k], d2[k])
        else:
            d1[k] = v


def flatten_arg_tuples(args):
    return [arg for arg_tuple in args for arg in arg_tuple]


def run_and_check(args):
    output = subprocess.run(args)
    return output.returncode == 0
