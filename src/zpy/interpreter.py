import sys
import os
import builtins # Import builtins module to copy its dict
from .tokenizer import translate_zpy_to_py, load_keywords, KEYWORDS_CONFIG_PATH
from .runtime import bootstrap

def run_zpy_file(filepath):
    """
    Translates and executes a .zpy file within a controlled environment.
    """
    # Load the keyword map and built-ins map
    keyword_map, builtins_map = load_keywords(KEYWORDS_CONFIG_PATH)
    if keyword_map is None or builtins_map is None:
        print("Failed to load keywords or built-ins. Exiting.", file=sys.stderr)
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
    python_code = translate_zpy_to_py(zpy_code, keyword_map, builtins_map)

    if python_code is None:
        print("Failed to translate the code. Exiting.", file=sys.stderr)
        return

    # Execute the translated code
    try:
        # Initialize exec_globals with essential module attributes
        # and a sandboxed __builtins__ dictionary.
        exec_globals = {
            '__name__': '__main__',
            '__file__': os.path.abspath(filepath),
            '__package__': None, # For simple scripts, no package
            '__builtins__': dict(builtins.__dict__) # Copy builtins.__dict__ for sandboxing
        }

        # Bootstrap the environment with Chinese aliases for built-ins and exceptions
        # This now operates on exec_globals['__builtins__']
        bootstrap(exec_globals['__builtins__'], builtins_map)

        # Compile the code object for better traceback information
        code_obj = compile(python_code, os.path.abspath(filepath), "exec")

        # Execute the compiled code
        exec(code_obj, exec_globals, exec_globals) # Use exec_globals for both globals and locals
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