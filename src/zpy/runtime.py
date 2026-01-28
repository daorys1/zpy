import builtins
import sys
# KEYWORDS_CONFIG_PATH and load_keywords are no longer directly used here,
# as builtins_map will be passed as an argument.
# from .tokenizer import load_keywords, KEYWORDS_CONFIG_PATH

def bootstrap(exec_builtins_dict, builtins_map):
    """
    Sets up the `__builtins__` dictionary for the executed code with Chinese aliases for
    Python built-in functions and exceptions.

    Args:
        exec_builtins_dict (dict): The dictionary to populate, typically `exec_globals["__builtins__"]`.
        builtins_map (dict): A dictionary mapping Chinese built-in names to Python built-in names.
    """
    if builtins_map is None:
        print("Error: Built-ins map is None. Skipping built-in aliases.", file=sys.stderr)
        return

    # Alias built-in functions from the config file
    for zpy_name, py_name in builtins_map.items():
        if hasattr(builtins, py_name):
            exec_builtins_dict[zpy_name] = getattr(builtins, py_name)
        else:
            print(f"Warning: Python built-in '{py_name}' (aliased as '{zpy_name}') not found.", file=sys.stderr)

    # Alias specific exceptions as requested
    exception_aliases = {
        "错误": "Exception",
        "值错误": "ValueError",
        "键错误": "KeyError",
    }
    for zpy_exc_name, py_exc_name in exception_aliases.items():
        if hasattr(builtins, py_exc_name):
            exec_builtins_dict[zpy_exc_name] = getattr(builtins, py_exc_name)
        else:
            print(f"Warning: Python exception '{py_exc_name}' (aliased as '{zpy_exc_name}') not found.", file=sys.stderr)