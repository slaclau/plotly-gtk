import numpy as np


def get_random_strings(n):
    LENGTH = 4

    alphabet = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    np_alphabet = np.array(alphabet)
    np_codes = np.random.choice(np_alphabet, [n, LENGTH])
    codes = ["".join(np_codes[i]) for i in range(len(np_codes))]
    return np.array(codes)
