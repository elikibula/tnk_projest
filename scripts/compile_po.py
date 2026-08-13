"""Compile a simple gettext PO catalogue without external gettext binaries."""
from __future__ import annotations

import ast
import struct
import sys
from pathlib import Path


def read_catalog(path: Path) -> dict[str, str]:
    messages: dict[str, str] = {}
    msgid: list[str] | None = None
    msgstr: list[str] | None = None
    active: list[str] | None = None
    for raw_line in [*path.read_text(encoding="utf-8").splitlines(), ""]:
        line = raw_line.strip()
        if line.startswith("msgid "):
            if msgid is not None and msgstr is not None:
                messages["".join(msgid)] = "".join(msgstr)
            msgid = [ast.literal_eval(line[6:])]
            msgstr = []
            active = msgid
        elif line.startswith("msgstr "):
            msgstr = [ast.literal_eval(line[7:])]
            active = msgstr
        elif line.startswith('"') and active is not None:
            active.append(ast.literal_eval(line))
        elif not line and msgid is not None and msgstr is not None:
            messages["".join(msgid)] = "".join(msgstr)
            msgid = msgstr = active = None
    return messages


def write_mo(messages: dict[str, str], output: Path) -> None:
    keys = sorted(messages)
    ids = b""; values = b""; id_offsets = []; value_offsets = []
    for key in keys:
        encoded = key.encode("utf-8"); id_offsets.append((len(encoded), len(ids))); ids += encoded + b"\0"
        encoded = messages[key].encode("utf-8"); value_offsets.append((len(encoded), len(values))); values += encoded + b"\0"
    count = len(keys); key_table = 28; value_table = key_table + count * 8; key_data = value_table + count * 8; value_data = key_data + len(ids)
    payload = [struct.pack("<7I", 0x950412DE, 0, count, key_table, value_table, 0, 0)]
    payload.extend(struct.pack("<2I", length, key_data + offset) for length, offset in id_offsets)
    payload.extend(struct.pack("<2I", length, value_data + offset) for length, offset in value_offsets)
    payload.extend((ids, values))
    output.write_bytes(b"".join(payload))


if __name__ == "__main__":
    source = Path(sys.argv[1]); destination = Path(sys.argv[2])
    catalog = read_catalog(source)
    write_mo(catalog, destination)
    print(f"Compiled {len(catalog)} messages: {source} -> {destination}")
