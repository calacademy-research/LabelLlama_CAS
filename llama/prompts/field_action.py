import importlib
from pathlib import Path


class FieldAction:
    def __init__(self, link: str) -> None:
        lnk = Path(link)

        self.name = lnk.stem
        self.module = lnk

        cls_name = lnk.stem[0].upper() + lnk.stem[1:]
        mod_name = link.removeprefix("../").removesuffix(".py").replace("/", ".")
        module = importlib.import_module(mod_name)
        field_class = getattr(module, cls_name)

        self.columns = field_class().get_field_names()
        self.field_class = getattr(module, cls_name)
