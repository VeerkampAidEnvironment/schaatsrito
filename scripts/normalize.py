import unicodedata
import re

def normalize_name(name: str) -> str:
    if not name:
        return ""

    # Normalize unicode (important!)
    name = unicodedata.normalize("NFKC", name)

    # Replace ALL weird spaces with normal space
    name = re.sub(r"[\u00A0\u2000-\u200D\u202F\u205F\u3000]", " ", name)

    # Remove stray commas at end (ISU sometimes adds them)
    name = name.strip(" ,")

    # Collapse whitespace
    name = " ".join(name.split())

    return name
