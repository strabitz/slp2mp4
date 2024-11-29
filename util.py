# Misc. utilities


def update_dict(d1: dict, d2: dict):
    for k, v in d2.items():
        if isinstance(v, dict):
            if k not in d1:
                d1[k] = {}
            update_dict(d1[k], d2[k])
        else:
            d1[k] = v
