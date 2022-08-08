import os
import re


def text_format(text):
    text = text.replace("!", ".")
    text = text.replace("?", ".")
    text = text.replace("(", "")
    text = text.replace(")", "")
    return text


def parse_file(file_path, split_digits=False):
    file = file_path
    if not os.path.isfile(file):
        file, _ = os.path.splitext(file)
        file = f"texts/{file}.txt"

    with open(file, "r", encoding="utf-8") as f:
        text = f.read().upper()
        # Format the text
        text = text_format(text)
        # split text per character
        # data = re.findall(r"\S|\s", text)
        # data = re.findall(r"((\S|\s)\2*)", text) # split text per two consecutive characters
        if split_digits:
            digits_re = r"([0-9])|"
        else:
            digits_re = r"()"
        data = re.findall(
            digits_re + r"(" r"(\S|\s)" r"(?:\3*)" r"(?:[\., ]*)" r")", text
        )  # split text per two consecutive characters and dots
        dur_data = []
        for string in data:
            digit, repeats, char = string
            if digit:
                d = (1, *get_char_and_duration(digit))
            else:
                repeats_count = len(repeats)
                char, _ = get_char_and_duration(char)
                d = (
                    repeats_count,
                    char,
                    sum(get_char_and_duration(c)[1] for c in repeats),
                )
            dur_data.append(d)
        # dur_data = [
        #     (
        #         len(string[0]), # Number of repeats
        #         get_char_and_duration(string[1])[0], # Cleaned character
        #         sum(get_char_and_duration(c)[1] for c in string[0]) # Duration
        #     ) for string in data
        # ]
        # for d in dur_data:
        #     print(d)
        return dur_data


def get_char_and_duration(char):
    if char == " ":
        duration = SINGLE_DURATION
    elif char == ",":
        duration = 1
        char = " "
    elif char == ".":
        duration = 1.7
        char = " "
    elif char == "\n":
        duration = 2.2
        char = " "
    elif char in "0123456789":
        duration = SINGLE_DURATION * 1.2
    else:
        duration = SINGLE_DURATION
    return char, duration * SPEED_MODIFIER


SECONDARY_MODIFIER = 1.3
SPEED_MODIFIER = 0.29 / SECONDARY_MODIFIER
SINGLE_DURATION = 0.36
