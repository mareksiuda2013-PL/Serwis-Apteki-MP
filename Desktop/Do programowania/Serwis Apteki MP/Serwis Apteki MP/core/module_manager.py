from dataclasses import dataclass


@dataclass
class Module:
    name: str
    widget: object


class ModuleManager:

    def __init__(self):
        self._modules = []

    def register(self, name, widget):
        self._modules.append(Module(name, widget))

    def modules(self):
        return self._modules