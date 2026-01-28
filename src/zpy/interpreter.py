import sys
from .tokenizer import translate_zpy_to_py, load_keywords, KEYWORDS_CONFIG_PATH

def run_zpy_file(filepath):
    """
    Translates and executes a .zpy file within a controlled environment.
    """
    # Load the keyword map
    keyword_map = load_keywords(KEYWORDS_CONFIG_PATH)
    if keyword_map is None:
        print("Failed to load keywords. Exiting.", file=sys.stderr)
        return

    # Read the zpy source file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            zpy_code = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {filepath}", file=sys.stderr)
        return
    except Exception as e:
        print(f"Error reading input file {filepath}: {e}", file=sys.stderr)
        return

    # Translate the code
    python_code = translate_zpy_to_py(zpy_code, keyword_map)

    if python_code is None:
        print("Failed to translate the code. Exiting.", file=sys.stderr)
        return

    # Execute the translated code
    try:
        # Create a dedicated globals dictionary for the executed code
        # to avoid polluting the interpreter's own global scope.
        # We also add the file's path to __file__ for relative imports.
        import os
        exec_globals = {
            '__name__': '__main__',
            '__file__': os.path.abspath(filepath)
        }
        exec(python_code, exec_globals)
    except Exception as e:
        print(f"An error occurred during execution of '{filepath}':\n{e}", file=sys.stderr)


def main():
    """
    Main function to run the zpy interpreter from the command line.
    """
    if len(sys.argv) != 2:
        # Corrected usage message for running as a module
        print(f"Usage: python -m src.zpy.interpreter <input_zpy_file>", file=sys.stderr)
        sys.exit(1)

    input_zpy_file = sys.argv[1]
    run_zpy_file(input_zpy_file)

if __name__ == "__main__":
    main()
