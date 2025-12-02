import re
import html

import unicodedata

encountered_strings = []


def string_with_style(text: str):
    # removes following white spaces
    text = re.sub(r"^\s*", "", text)
    # removes ending white spaces
    text = re.sub(r"\s*$", "", text)
    # removes multiple spacing between spacial characters and any following text/letters
    text = re.sub(r"(?<=[.,?!])(?=[\w])", r" ", text)
    return text


def string_with_newlines_fixed(text: str):
    # removes following new lines
    text = re.sub(r"^(\r?\n)*", "", text)
    # removes ending new lines
    text = re.sub(r"(\r?\n)*$", "", text)
    # removes multiple new lines
    text = re.sub(r"(\r?\n)+", r"\n", text)
    return text


def string_with_meaning(text: str) -> bool:
    return re.search("[^\W_]", text) != None


def convert_utf8_symbols(text: str):
    return unicodedata.normalize("NFKC", html.unescape(text))


def ask_for_authorization(text: str):
    if encountered_strings.count(text) == 0:
        # encountered_strings.append(text)
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


def fix_bad_detections(input: str) -> str:
    result = re.sub(r"(\W)(\wm )", r"\1I'm ", input)
    result = re.sub(r"\n+", "\n", result)
    result = result.replace("|", "I")
    return result


def check_is_same(str1: str, str2: str, side_tolerance: int) -> bool:
    if len(str1) < side_tolerance * 3 or len(str2) < side_tolerance * 3:
        return False
    if side_tolerance == 0:
        return str1 == str2
    return (
        str2.find(str1[side_tolerance:-side_tolerance]) != -1 and str1.find(str2[side_tolerance:-side_tolerance]) != -1
    )
