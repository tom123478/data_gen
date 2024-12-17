import random as rnd
import re
import string

def create_strings_from_corpus_file(corpus_file_path):
    with open(corpus_file_path, 'r', encoding="utf8") as f:
        strings = [l.strip() for l in f]    
        return strings

def create_strings_from_texts_file(filename, count, mini=10, maxi=40):
    """
    从指定的文件中读取每一行文字并生成字符串列表。

    参数:
        filename (str): 要读取的文件路径。
        count (int): 需要生成的字符串数量。
        mini (int): 每行字符串的最小长度，默认值为10。
        maxi (int): 每行字符串的最大长度，默认值为40。

    返回:
        list: 包含生成字符串的列表。
    """

    strings = []  # 初始化一个空列表，用于存储生成的字符串。

    # 打开文件并确保文件以 UTF-8 编码读取。
    with open(filename, 'r', encoding="utf8") as f:
        # 去掉每行两端的空白符，并将多个空格替换为一个空格，处理后的行存储到 `lines`。
        lines = [' '.join(l.strip().split()) for l in f]

        # 过滤掉长度小于等于 mini 的行，并将每行裁剪为不超过 maxi 的长度。
        lines = [l[:maxi] for l in lines if len(l) > mini]

        # 随机打乱行的顺序。
        rnd.shuffle(lines)

        # 如果文件中没有符合条件的行，抛出异常。
        if len(lines) == 0:
            raise Exception("No lines could be read in file")

        # 循环填充字符串列表，直到达到所需的数量 `count`。
        while len(strings) < count:
            # 如果剩余需要的字符串数量小于等于 `lines` 的长度，直接扩展所需的部分。
            if len(lines) >= count - len(strings):
                strings.extend(lines[:count - len(strings)])
            else:
                # 如果 `lines` 的长度不足以补足 `count`，重复使用 `lines` 中的字符串。
                strings.extend(lines)

    # 返回生成的字符串列表。
    return strings


def create_strings_from_muti_files(path, dict=None):
    """
    从指定目录下的多个文件中读取所有字符串。

    参数:
        path (str): 包含多个文本文件的目录路径。
        dict (optional): 其他可选的字典或规则 (暂未使用)。

    功能:
        这个函数目前是占位符，没有实现具体逻辑。
    """
    pass  # 函数未实现

def create_strings_from_dict(length, allow_variable, count, lang_dict):
    """
    从字典中创建所有字符串，通过循环读取字典内容生成字符串。

    参数:
        length (int): 每个字符串的目标长度。
        allow_variable (bool): 是否允许字符串长度可变。
        count (int): 需要生成的字符串数量。
        lang_dict (list): 包含所有单词的字典。

    返回:
        list: 包含生成字符串的列表。
    """

    dict_len = len(lang_dict)  # 获取字典中单词的数量
    strings = []  # 初始化一个空列表用于存储生成的字符串

    # 生成字符串的逻辑（非随机）
    for i in range(count):  # 重复生成字符串直到达到所需数量
        n = i % dict_len  # 如果超出字典范围，就从头循环取单词
        strings.append(lang_dict[n])  # 从字典中按顺序取单词
    return strings  # 返回生成的字符串列表

def create_strings_randomly_from_chars(length, allow_variable, count, let, num, sym, lang):
    """
    通过从字符池中随机采样生成所有字符串。

    参数:
        length (int): 每个字符串的目标长度。
        allow_variable (bool): 是否允许字符串长度可变。
        count (int): 需要生成的字符串数量。
        let (bool): 是否包含字母。
        num (bool): 是否包含数字。
        sym (bool): 是否包含符号。
        lang (str): 语言代码，用于确定字符池的范围。

    返回:
        list: 包含生成的随机字符串的列表。
    """

    # 如果字母、数字和符号全未启用，则默认启用所有类型。
    if True not in (let, num, sym):
        let, num, sym = True, True, True

    pool = ''  # 初始化字符池
    if let:  # 如果启用了字母
        if lang == 'cn':  # 如果语言是中文
            pool += ''.join([chr(i) for i in range(19968, 40908)])  # Unicode 范围内的中文字符
        else:  # 如果语言不是中文
            pool += string.ascii_letters  # 英文字母（大小写）
    if num:  # 如果启用了数字
        pool += "0123456789"  # 添加数字到字符池
    if sym:  # 如果启用了符号
        pool += "!\"#$%&'()*+,-./:;?@[\\]^_`{|}~"  # 添加符号到字符池

    # 根据语言设置字符序列的最小和最大长度
    if lang == 'cn':
        min_seq_len = 1  # 中文字符最小序列长度为1
        max_seq_len = 2  # 中文字符最大序列长度为2
    else:
        min_seq_len = 2  # 非中文字符最小序列长度为2
        max_seq_len = 10  # 非中文字符最大序列长度为10

    strings = []  # 初始化空列表用于存储生成的字符串
    for _ in range(0, count):  # 按需求生成指定数量的字符串
        current_string = ""  # 初始化当前字符串为空
        for _ in range(0, rnd.randint(1, length) if allow_variable else length):
            # 如果允许长度可变，随机选择一个序列长度，否则使用固定长度
            seq_len = rnd.randint(min_seq_len, max_seq_len)
            # 从字符池中随机选择字符，构建当前序列
            current_string += ''.join([rnd.choice(pool) for _ in range(seq_len)])
            current_string += ' '  # 每个序列后面加一个空格
        strings.append(current_string[:-1])  # 去掉末尾多余的空格，将当前字符串添加到列表
    return strings  # 返回生成的字符串列表