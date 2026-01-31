import builtins
import importlib.abc
import importlib.machinery
import importlib.util
import os
import sys

from .runtime import bootstrap
from .tokenizer import translate_zpy_to_py


class ZpyLoader(importlib.abc.Loader):
    def __init__(self, filepath, fullname, is_package, keyword_map, builtins_map):
        self.filepath = filepath
        self.fullname = fullname
        self._is_package = is_package
        self.keyword_map = keyword_map
        self.builtins_map = builtins_map

    def create_module(self, spec):
        return None

    def is_package(self, fullname):
        return self._is_package

    def exec_module(self, module):
        module.__file__ = self.filepath
        module.__loader__ = self
        module.__package__ = self.fullname if self._is_package else self.fullname.rpartition(".")[0]
        if self._is_package:
            module.__path__ = [os.path.dirname(self.filepath)]

        module.__dict__.setdefault("__builtins__", dict(builtins.__dict__))
        bootstrap(module.__dict__["__builtins__"], self.builtins_map)

        try:
            with open(self.filepath, "r", encoding="utf-8") as handle:
                zpy_code = handle.read()
        except OSError as exc:
            raise ImportError(f"Unable to read module file {self.filepath}: {exc}") from exc

        python_code = translate_zpy_to_py(zpy_code, self.keyword_map, self.builtins_map)
        if python_code is None:
            raise ImportError(f"Failed to translate zpy module {self.fullname}")

        code_obj = compile(python_code, self.filepath, "exec")
        exec(code_obj, module.__dict__, module.__dict__)


class ZpyMetaPathFinder(importlib.abc.MetaPathFinder):
    def __init__(self, keyword_map, builtins_map):
        self.keyword_map = keyword_map
        self.builtins_map = builtins_map

    def find_spec(self, fullname, path=None, target=None):
        search_paths = sys.path if path is None else path
        parts = fullname.split(".")
        module_parts = parts if path is None else parts[-1:]

        for base_path in search_paths:
            if base_path == "":
                base_path = os.getcwd()

            package_path = os.path.join(base_path, *module_parts)
            zpy_init = os.path.join(package_path, "__init__.zpy")
            if os.path.isfile(zpy_init):
                loader = ZpyLoader(
                    zpy_init,
                    fullname,
                    True,
                    self.keyword_map,
                    self.builtins_map,
                )
                return importlib.util.spec_from_file_location(
                    fullname,
                    zpy_init,
                    loader=loader,
                    submodule_search_locations=[package_path],
                )

            py_init = os.path.join(package_path, "__init__.py")
            if os.path.isfile(py_init):
                loader = importlib.machinery.SourceFileLoader(fullname, py_init)
                return importlib.util.spec_from_file_location(
                    fullname,
                    py_init,
                    loader=loader,
                    submodule_search_locations=[package_path],
                )

            zpy_module = os.path.join(base_path, *module_parts) + ".zpy"
            if os.path.isfile(zpy_module):
                loader = ZpyLoader(
                    zpy_module,
                    fullname,
                    False,
                    self.keyword_map,
                    self.builtins_map,
                )
                return importlib.util.spec_from_file_location(
                    fullname,
                    zpy_module,
                    loader=loader,
                )

            py_module = os.path.join(base_path, *module_parts) + ".py"
            if os.path.isfile(py_module):
                loader = importlib.machinery.SourceFileLoader(fullname, py_module)
                return importlib.util.spec_from_file_location(
                    fullname,
                    py_module,
                    loader=loader,
                )

        return None
