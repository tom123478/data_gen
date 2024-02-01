import random as rnd
import re
import string

def create_strings_from_file(filename, count, mini=10, maxi=40):
    """
        Create all strings by reading lines in specified files
    """

    strings = []

    with open(filename, 'r', encoding="utf8") as f:
        lines = [' '.join(l.strip().split()) for l in f]
        lines = [l[:maxi] for l in lines if len(l) > mini]

        rnd.shuffle(lines)
        if len(lines) == 0:
            raise Exception("No lines could be read in file")
        while len(strings) < count:
            if len(lines) >= count - len(strings):
                strings.extend(lines[:count - len(strings)])
            else:
                strings.extend(lines)

    return strings

def create_strings_from_dict(length, allow_variable, count, lang_dict):
    """
        Create all strings by picking X [NOT random] word in the dictionnary
    """

    dict_len = len(lang_dict)  ### lines in ko.txt
    strings = []
    # for _ in range(0, count):   #[Random word]
    #     current_string = ""
    #     for _ in range(0, rnd.randint(1, length) if allow_variable else length):
    #         current_string += lang_dict[rnd.randrange(dict_len)]
    #         current_string += ' '
    #     strings.append(current_string[:-1])
    # return strings

    # Not Random
    for i in range(count): # repeat dict multiple times
        n = i % dict_len
        strings.append(lang_dict[n])
    return strings


def create_strings_randomly(length, allow_variable, count, let, num, sym, lang):
    """
        Create all strings by randomly sampling from a pool of characters.
    """

    # If none specified, use all three
    if True not in (let, num, sym):
        let, num, sym = True, True, True

    pool = ''
    if let:
        if lang == 'cn':
            pool += ''.join([chr(i) for i in range(19968, 40908)]) # Unicode range of CHK characters
        else:
            pool += string.ascii_letters
    if num:
        pool += "0123456789"
    if sym:
        pool += "!\"#$%&'()*+,-./:;?@[\\]^_`{|}~"

    if lang == 'cn':
        min_seq_len = 1
        max_seq_len = 2
    else:
        min_seq_len = 2
        max_seq_len = 10

    strings = []
    for _ in range(0, count):
        current_string = ""
        for _ in range(0, rnd.randint(1, length) if allow_variable else length):
            seq_len = rnd.randint(min_seq_len, max_seq_len)
            current_string += ''.join([rnd.choice(pool) for _ in range(seq_len)])
            current_string += ' '
        strings.append(current_string[:-1])
    return strings
