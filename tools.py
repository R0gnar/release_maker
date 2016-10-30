import math
from urllib.request import Request, urlopen
from urllib.error import URLError
from base64 import b64encode


class bcolors:
    HEADER = '\033[42m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    ERROR = '\033[31m'
    WARNING = '\033[33m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def styled(text, style=None):
    if style:
        text = style + text + bcolors.ENDC

    return text


def input_req(question):
    text = ''
    while True:
        text = input(question)
        if text:
            break

    return text


def input_list(questions):
    i = 1
    for question in questions:
        print(str(i) + ') ' + question)
        i += 1
    print('0) Exit')

    while True:
        answer = int(input_req('Enter number: '))
        if answer == 0:
            exit()

        if len(questions) >= answer > 0:
            break

    return answer


def print_table(data):
    rows_width = []
    for row in data:
        if len(rows_width) == 0:
            rows_width = [0] * len(row)

        for i, text in enumerate(row):
            text = str(text)
            if len(text) > 100:
                text = text[:100]

            text_length = len(text) + 6
            if rows_width[i] < text_length:
                rows_width[i] = text_length

    total_width = sum(rows_width) + len(rows_width) + 1
    print('-' * total_width)

    for row in data:
        row_text = '|'
        for i, text in enumerate(row):
            text = str(text)
            if len(text) > 100:
                text = text[:100]

            empty_space = rows_width[i] - len(text)
            lspace = math.floor(empty_space / 2)
            rspace = math.ceil(empty_space / 2)

            row_text += ' ' * lspace
            row_text += text
            row_text += ' ' * rspace
            row_text += '|'

        print(row_text)
        print('-' * total_width)


def make_http_request(url, data=None, headers=None):
    # Convert to bytes
    if isinstance(data, str):
        data = data.encode('utf-8')

    req = Request(url, data=data, headers=headers)
    try:
        response = urlopen(req)
    except URLError as e:
        return False
    else:
        data = response.read()
        return data.decode('utf-8')


def make_basic_auth_str(login, password):
    if isinstance(login, str):
        login = login.encode('utf-8')
    if isinstance(password, str):
        password = password.encode('utf-8')

    basic_str = b64encode(bytearray(login) + bytearray(b":") + bytearray(password)).decode("utf-8")

    return basic_str
