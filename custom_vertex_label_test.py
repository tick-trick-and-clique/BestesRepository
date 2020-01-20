def e_is_c(l1, l2):
    if l1 == l2:
        return True
    elif l1 in ["e", "c"] and l2 in ["e", "c"]:
        return True
    else:
        return False
