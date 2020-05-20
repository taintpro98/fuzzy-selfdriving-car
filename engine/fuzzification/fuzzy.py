def get_triangle_fuzzy_set(a, b, c):
    d1 = b - a
    d2 = c - b

    def triangle_fuzzy_set(x):
        if a <= x < b:
            return (x - a) / d1
        elif b <= x < c:
            return (c - x) / d2
        return 0

    def right_triangle_fuzzy_set(x):
        if b <= x < c:
            return (c - x) / d2
        elif x < b:
            return 1
        return 0

    def left_triangle_fuzzy_set(x):
        if a < x <= b:
            return (b - x) / d1
        elif x > b:
            return 1
        return 0

    if a == b:
        return right_triangle_fuzzy_set
    elif b == c:
        return left_triangle_fuzzy_set
    return triangle_fuzzy_set

def get_trapezoid_fuzzy_set(a, b, c, d):
    d1 = b - a
    d2 = d - c

    assert b != c

    def right_trapezoid_fuzzy_set(x):
        if x < c:
            return 1
        elif c <= x < d:
            return (d - x) / d2
        return 0

    def left_trapezoid_fuzzy_set(x):
        if a <= x < b:
            return (x - a) / d1
        elif b <= x:
            return 1
        return 0

    def middle_trapezoid_fuzzy_set(x):
        if a <= x < b:
            return (x - a) / d1
        elif b <= x <= c:
            return 1
        elif c < x < d:
            return (d - x) / d2
        return 0

    if a == b:
        return right_trapezoid_fuzzy_set
    elif c == d:
        return left_trapezoid_fuzzy_set
    return middle_trapezoid_fuzzy_set

def get_labels(x, fuzzy_sets: dict):
    labels = {}
    for label, fuzzy_set in fuzzy_sets.items():
        confident = fuzzy_set(x)
        if confident > 0:
            labels[label] = confident
    return labels