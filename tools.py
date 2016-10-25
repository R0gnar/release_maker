from urllib.request import Request, urlopen
from urllib.error import URLError
from base64 import b64encode


class bcolors:
    HEADER = '\033[42m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[31m'
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
