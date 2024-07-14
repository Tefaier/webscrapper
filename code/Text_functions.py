import re
import html
import unicodedata

encountered_strings = []

def string_with_style(text: str):
    text = re.sub(r'\A\s*', "", text)
    text = re.sub(r'(?<=[.,?!])(?=[\w])', r' ', text)
    return text

def string_with_meaning(text: str):
    return re.search("[^\W_]", text) != None


def convert_utf8_symbols(text: str):
    return unicodedata.normalize("NFKC", html.unescape(text))


def ask_for_authentification(text: str):
    if encountered_strings.count(text) == 0:
        encountered_strings.append(text)
        print(text)
        print("If you want to continue write YES or something else if not")
        command = input()
        return command == "YES"
    else:
        return False

def dict_to_text(dictionary: dict, key_value_sep: str, keys_sep: str):
    answer = ""
    for key, value in dictionary.items():
        if answer != "":
            answer += keys_sep
        answer += f"{key}{key_value_sep}'{value}'"
    return answer
