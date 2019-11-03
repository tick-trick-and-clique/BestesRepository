def a_is_b(l1, l2):
    if l1 == l2:
        return True
    elif l1 in ["a", "b"] and l2 in ["a", "b"]:
        return True
    else:
        return False