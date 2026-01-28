import configparser
import tokenize
import io
import sys

# Path to the keywords configuration file.
# This assumes the script is run from the project root directory.
KEYWORDS_CONFIG_PATH = "src/zpy/zh-Hans.ini"

def load_keywords(config_path):
    """Loads the keyword translation map from an INI file."""
    config = configparser.ConfigParser()
    try:
        # config.read() returns a list of files that were successfully read.
        if not config.read(config_path, encoding='utf-8'):
            print(f"Error: Keywords configuration file not found or is empty at {config_path}", file=sys.stderr)
            return None
        # Assuming all keywords are under the [Keywords] section
        if 'Keywords' in config:
            return dict(config['Keywords'])
        else:
            print(f"Error: [Keywords] section not found in {config_path}", file=sys.stderr)
            return None
    except configparser.Error as e:
        print(f"Error parsing INI file {config_path}: {e}", file=sys.stderr)
        return None

def translate_zpy_to_py(zpy_code, keyword_map):
    """
    Translates a string of zpy code (with Chinese keywords) into a string
    of standard Python code using tokenization.

    Args:
        zpy_code (str): The string of zpy code to translate.
        keyword_map (dict): A dictionary mapping Chinese keywords to Python keywords.

    Returns:
        str: The translated Python code as a string, or None on failure.
    """
    # Use io.StringIO to treat the string as a file for tokenize.generate_tokens
    readline = io.StringIO(zpy_code).readline
    translated_tokens = []

    try:
        for token_info in tokenize.generate_tokens(readline):
            token_type = token_info.type
            token_string = token_info.string

            # Only replace 'NAME' tokens that are in our keyword map
            if token_type == tokenize.NAME and token_string in keyword_map:
                translated_tokens.append(
                    tokenize.TokenInfo(
                        token_type,
                        keyword_map[token_string],
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

    # Untokenize the translated tokens back into Python code
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

    keyword_map = load_keywords(KEYWORDS_CONFIG_PATH)
    if keyword_map is None:
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

    translated_code = translate_zpy_to_py(zpy_code, keyword_map)

    if translated_code is not None:
        # The AST part of the original request:
        # "translated into python ast"
        # We can now parse the translated code into an AST.
        # For this step, we just print the code. The interpreter can
        # take this string and do the ast.parse() call itself.
        print(translated_code)
    else:
        print("Translation failed.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
