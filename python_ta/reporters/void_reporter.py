from .core import PythonTaReporter


class VoidReporter(PythonTaReporter):
    """Void reporter. Screams into the void; doesn't report anything."""

    name = "VoidReporter"

    def print_messages(self, level: str = "all") -> None:
        pass
