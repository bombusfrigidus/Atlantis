"""Flatten landed titles and keep only the Atlantis capital and landless flag.

Run from the mod root with:
    python tools/flatten_landed_titles.py

The script preserves each file preamble, removes county/barony title IDs, and
rewrites every retained title as an independent top-level block.
"""

from pathlib import Path
import re


TARGETS = (
    Path("common/landed_titles/00_landed_titles.txt"),
    Path("common/landed_titles/07_pam_ecclesiastical_titles.txt"),
)
HEADER = re.compile(r"(?m)^[ \t]*([ebcdkh]_[A-Za-z0-9_]+)[ \t]*=[ \t]*\{")
RENDERED_BLOCK = re.compile(
    r"(?m)^(?P<name>[edkh]_[A-Za-z0-9_]+) = \{\n"
    r"\tcapital = c_atlantis\n\tlandless = yes\n\}$(?:\n|$)"
)


def flatten_titles(text: str, target: Path) -> tuple[str, int, int]:
    """Return flattened file text, removed county/barony count, retained count."""
    matches = list(HEADER.finditer(text))
    if not matches:
        raise ValueError(f"No title declarations found in {target}")

    names = [match.group(1) for match in matches]
    retained = [name for name in names if not name.startswith(("c_", "b_"))]
    removed_count = len(names) - len(retained)
    if not retained:
        raise ValueError("No titles remain after excluding county and barony titles")

    prefix = text[: matches[0].start()].rstrip()
    blocks = [
        f"{name} = {{\n\tcapital = c_atlantis\n\tlandless = yes\n}}"
        for name in retained
    ]
    result = prefix + "\n\n" + "\n\n".join(blocks) + "\n"

    output_matches = list(RENDERED_BLOCK.finditer(result))
    if [match.group("name") for match in output_matches] != retained:
        raise ValueError("Output validation failed: title blocks are not standalone or minimal")
    if len(output_matches) != len(retained):
        raise ValueError("Output validation failed: unexpected title block count")

    return result, removed_count, len(retained)


def main() -> None:
    for target in TARGETS:
        raw = target.read_bytes()
        has_bom = raw.startswith(b"\xef\xbb\xbf")
        newline = "\r\n" if b"\r\n" in raw else "\n"
        text = raw.decode("utf-8-sig").replace("\r\n", "\n")
        result, removed_count, retained_count = flatten_titles(text, target)

        encoded = result.encode("utf-8")
        if newline == "\r\n":
            encoded = encoded.replace(b"\n", b"\r\n")
        if has_bom:
            encoded = b"\xef\xbb\xbf" + encoded
        target.write_bytes(encoded)
        print(
            f"{target}: removed {removed_count} county/barony titles and wrote "
            f"{retained_count} standalone title blocks."
        )


if __name__ == "__main__":
    main()
