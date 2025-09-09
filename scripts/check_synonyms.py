from __future__ import annotations

from app.services.synonyms import canonicalize


def run():
    samples = [
        ("Sleep Training", "topic_sleep"),
        ("vitamin d", "topic_nutrition"),
        ("Unicorn allergy", None),
        ("  NAPS  ", "topic_naps"),
        ("Baby Led   Weaning", "pref_blw"),
        ("eczema", "cond_eczema"),
    ]
    for text, expected in samples:
        got = canonicalize(text)
        print(f"{text!r} -> {got!r} (expected {expected!r})")


if __name__ == "__main__":
    run()

