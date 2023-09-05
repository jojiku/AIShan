from pathlib import Path
from random import sample

class Joker:
    def __init__(self, jokes_path: Path):

        with open(jokes_path, "r") as f:
            raw_str = f.read()
            self.jokes = raw_str.split(";")

    def tell_joke(self) -> str:
        return sample(self.jokes, 1)[0]
