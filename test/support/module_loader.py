from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_module_from_file(path: Path) -> ModuleType:
    spec = spec_from_file_location("", path.resolve())
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from '{path}'")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
