from typing import Protocol


class ModelClient(Protocol):
    def generate(self, prompt: str, file_text: str) -> str:
        """Generate filtering output lines from one text input file."""
