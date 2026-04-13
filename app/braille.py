import os
import logging
from pathlib import Path

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def save_output(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# ----------------------------
# BRAILLE STANDARD MAPS
# ----------------------------

BRAILLE_LETTERS = {
    'a':'⠁','b':'⠃','c':'⠉','d':'⠙','e':'⠑','f':'⠋',
    'g':'⠛','h':'⠓','i':'⠊','j':'⠚','k':'⠅','l':'⠇',
    'm':'⠍','n':'⠝','o':'⠕','p':'⠏','q':'⠟','r':'⠗',
    's':'⠎','t':'⠞','u':'⠥','v':'⠧','w':'⠺','x':'⠭',
    'y':'⠽','z':'⠵'
}

BRAILLE_DIGITS = {
    '0':'⠚','1':'⠁','2':'⠃','3':'⠉','4':'⠙',
    '5':'⠑','6':'⠋','7':'⠛','8':'⠓','9':'⠊'
}

BRAILLE_PUNCTUATION = {
    ':':'⠒','.':'⠲'
}

NUMBER_PREFIX = '⠼'   # indicates start of number
CAPITAL_PREFIX = '⠠'  # indicates next letter is capital

def normalize(text):
    return (
        text.replace("{", "")
            .replace("}", "")
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace('"', "")
            .replace(",", "\n")
            .replace("_", " ")
    )

def to_braille(text):
    result = []
    number_mode = False

    for c in text:

        # ---------------- numbers ----------------
        if c.isdigit():
            if not number_mode:
                result.append(NUMBER_PREFIX)
                number_mode = True
            result.append(BRAILLE_DIGITS[c])
            continue

        number_mode = False

        # ---------------- letters ----------------
        if c.isalpha():
            if c.isupper():
                result.append(CAPITAL_PREFIX)
            result.append(BRAILLE_LETTERS[c.lower()])
            continue

        # ---------------- punctuation ----------------
        if c in BRAILLE_PUNCTUATION:
            result.append(BRAILLE_PUNCTUATION[c])
            continue

        # ---------------- whitespace ----------------
        if c == ' ':
            result.append(' ')
        elif c == '\n':
            result.append('\n')
        elif c == '\t':
            result.append('    ')
        else:
            result.append('⠿')  # unknown char placeholder

    return ''.join(result)

def convert_to_braille(original_file: str, base_dir="app/final_json_output"):
    output_file = None

    try:
        os.makedirs(base_dir, exist_ok=True)

        file_name = Path(original_file).stem
        output_file = Path(base_dir) / f"{file_name}.txt"

        raw_text = read_file(original_file)
        formatted_text = normalize(raw_text)
        braille_text = to_braille(formatted_text)

        # Display
        print("\n===== ORIGINAL TEXT =====\n")
        print(formatted_text)

        print("\n===== BRAILLE OUTPUT =====\n")
        print(braille_text)

        # Save
        save_output(output_file, braille_text)

        print(f"\nBraille output saved to: {output_file}")

    except Exception as e:
        logging.error(f"Failed to process file '{output_file}': {e}")