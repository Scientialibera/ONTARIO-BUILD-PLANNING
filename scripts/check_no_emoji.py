from __future__ import annotations

from pathlib import Path
import subprocess
import sys

TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
EMOJI_RANGES = (
    (0x00A9, 0x00A9), (0x00AE, 0x00AE), (0x203C, 0x203C), (0x2049, 0x2049),
    (0x20E3, 0x20E3), (0x2122, 0x2122), (0x2139, 0x2139), (0x2194, 0x21FF),
    (0x2300, 0x23FF), (0x24C2, 0x24C2), (0x25AA, 0x27BF), (0x2B00, 0x2BFF),
    (0x3030, 0x3030), (0x303D, 0x303D), (0x3297, 0x3297), (0x3299, 0x3299),
    (0x1F000, 0x1FAFF), (0xFE0F, 0xFE0F),
)


def is_emoji_character(character: str) -> bool:
    codepoint = ord(character)
    return any(start <= codepoint <= end for start, end in EMOJI_RANGES)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        result = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True)
        paths = [root / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    except subprocess.CalledProcessError:
        paths = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    violations = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Dockerfile", "Makefile"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(is_emoji_character(character) for character in line):
                violations.append(f"{path.relative_to(root)}:{line_number}")
    if violations:
        print("Emoji policy violations found:")
        print("\n".join(violations))
        return 1
    print("No emoji characters found in tracked text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
