from pathlib import Path

from .utils import Joker

joker = Joker(Path("data/raw_data/jokes.txt"))

def tell_joke() -> str:
    return joker.tell_joke()

if __name__ == "__main__":
    print(tell_joke())
