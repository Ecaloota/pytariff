def two_pointer_intersection_search(seq_a: list, seq_b: list) -> list:
    inter_list = []
    i, j = 0, 0
    while i < len(seq_a) and j < len(seq_b):
        inter = seq_a[i] & seq_b[j]
        if inter:
            inter_list.append(inter)
        elif seq_a[i] < seq_b[j]:
            i += 1
        else:
            j += 1
    return inter


def intersection_search_sorted_sequence(seq: list) -> list:
    inter_list = []
    for idx, _ in enumerate(seq):
        inter = seq[idx - 1] & seq[idx]
        if inter:
            inter_list.append(inter)
    return inter_list
