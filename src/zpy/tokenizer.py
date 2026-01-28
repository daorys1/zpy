import configparser
import tokenize
import io
import sys

# Path to the keywords configuration file.
# This assumes the script is run from the project root directory.
KEYWORDS_CONFIG_PATH = "src/zpy/zh-Hans.ini"

def load_keywords(config_path):
    """Loads the keyword and built-in translation maps from an INI file."""
    config = configparser.ConfigParser()
    try:
        if not config.read(config_path, encoding='utf-8'):
            print(f"Error: Configuration file not found or is empty at {config_path}", file=sys.stderr)
            return None, None

        keyword_map = {}
        if 'Keywords' in config:
            keyword_map = dict(config['Keywords'])
        else:
            print(f"Warning: [Keywords] section not found in {config_path}", file=sys.stderr)

        builtins_map = {}
        if 'Builtins' in config:
            builtins_map = dict(config['Builtins'])
        else:
            print(f"Warning: [Builtins] section not found in {config_path}", file=sys.stderr)

        return keyword_map, builtins_map
    except configparser.Error as e:
        print(f"Error parsing INI file {config_path}: {e}", file=sys.stderr)
        return None, None

def translate_zpy_to_py(zpy_code, keyword_map, builtins_map):
    """
    Translates a string of zpy code (with Chinese keywords and built-ins) into a string
    of standard Python code using tokenization.

    Args:
        zpy_code (str): The string of zpy code to translate.
        keyword_map (dict): A dictionary mapping Chinese keywords to Python keywords.
        builtins_map (dict): A dictionary mapping Chinese built-in names to Python built-in names.

    Returns:
        str: The translated Python code as a string, or None on failure.
    """
    readline = io.StringIO(zpy_code).readline
    translated_tokens = []

    # Combine keyword_map and builtins_map for token replacement
    # Builtins take precedence if there's a conflict, though ideally there shouldn't be
    translation_map = {**keyword_map, **builtins_map}

    try:
        for token_info in tokenize.generate_tokens(readline):
            token_type = token_info.type
            token_string = token_info.string

            # Only replace 'NAME' tokens that are in our combined translation map
            if token_type == tokenize.NAME and token_string in translation_map:
                translated_tokens.append(
                    tokenize.TokenInfo(
                        token_type,
                        translation_map[token_string],
                        token_info.start,
                        token_info.end,
                        token_info.line
                    )
                )
            else:
                translated_tokens.append(token_info)
    except tokenize.TokenError as e:
        print(f"Error tokenizing input code: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred during tokenization: {e}", file=sys.stderr)
        return None

    return tokenize.untokenize(translated_tokens)

def main():
    """
    Main function to run the tokenizer from the command line.
    Reads a .zpy file, translates it, and prints the result to stdout.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_zpy_file>", file=sys.stderr)
        sys.exit(1)

    input_zpy_file = sys.argv[1]

    keyword_map, builtins_map = load_keywords(KEYWORDS_CONFIG_PATH)
    if keyword_map is None or builtins_map is None:
        sys.exit(1)

    try:
        with open(input_zpy_file, 'r', encoding='utf-8') as f:
            zpy_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_zpy_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file {input_zpy_file}: {e}", file=sys.stderr)
        sys.exit(1)

    translated_code = translate_zpy_to_py(zpy_code, keyword_map, builtins_map)

    if translated_code is not None:
        print(translated_code)
    else:
        print("Translation failed.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
