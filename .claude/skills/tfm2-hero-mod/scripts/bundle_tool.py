#!/usr/bin/env python3
"""Browse the base game's assets inside Teamfight Manager 2's bundle.game_data (read-only).

The bundle is an uncompressed archive:
    u32 entry_count
    repeat: u32 len + type (utf-8) | u32 len + asset path (utf-8) | u32 size + raw bytes
Types seen: data_champion, champion_info_sheet, champion_view, i18n, fanim, png,
sprite_sheet, sound_info, mp3, wav, ui, style, ...

Use it to find base assets you can reference by path from a mod (effects, sfx names,
stat icons), or to study base sprites and data.  Nothing here is meant for redistribution.

    python bundle_tool.py stats
    python bundle_tool.py list --type fanim --grep champions/
    python bundle_tool.py cat asset/base/setting/nightmare
    python bundle_tool.py extract --grep champions/fighter --out ./base_ref
    python bundle_tool.py sfx --grep fighter          # base sound names usable in Sfx/TargetSfx

Game folder: --game DIR, or env TFM2_GAME_DIR, or the usual Steam locations.
"""
import argparse
import json
import os
import struct
import sys

DEFAULT_GAME_DIRS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Teamfight Manager2",
    r"C:\Program Files\Steam\steamapps\common\Teamfight Manager2",
    r"D:\steam\steamapps\common\Teamfight Manager2",
    r"D:\Steam\steamapps\common\Teamfight Manager2",
    r"D:\SteamLibrary\steamapps\common\Teamfight Manager2",
    r"E:\SteamLibrary\steamapps\common\Teamfight Manager2",
    os.path.expanduser("~/.steam/steam/steamapps/common/Teamfight Manager2"),
    os.path.expanduser("~/Library/Application Support/Steam/steamapps/common/Teamfight Manager2"),
]

EXT_BY_TYPE = {"png": ".png", "mp3": ".mp3", "wav": ".wav", "ttf": ".ttf", "otf": ".otf", "svg": ".svg"}


def find_game_dir(explicit=None):
    candidates = [explicit, os.environ.get("TFM2_GAME_DIR")] + DEFAULT_GAME_DIRS
    for c in candidates:
        if c and os.path.isfile(os.path.join(c, "bundle.game_data")):
            return c
    return None


class Bundle:
    """Lazy index over bundle.game_data. Entries are (type, path, size, offset)."""

    def __init__(self, game_dir):
        self.path = os.path.join(game_dir, "bundle.game_data")
        self.entries = []
        with open(self.path, "rb") as f:
            (count,) = struct.unpack("<I", f.read(4))
            for _ in range(count):
                (tl,) = struct.unpack("<I", f.read(4))
                etype = f.read(tl).decode("utf-8", "replace")
                (pl,) = struct.unpack("<I", f.read(4))
                epath = f.read(pl).decode("utf-8", "replace")
                (size,) = struct.unpack("<I", f.read(4))
                offset = f.tell()
                f.seek(size, 1)
                self.entries.append((etype, epath, size, offset))
        self._by_path = {}
        for e in self.entries:
            self._by_path.setdefault(e[1], []).append(e)

    def find(self, path, etype=None):
        for e in self._by_path.get(path, []):
            if etype is None or e[0] == etype:
                return e
        return None

    def has(self, path, etype=None):
        return self.find(path, etype) is not None

    def read(self, entry):
        with open(self.path, "rb") as f:
            f.seek(entry[3])
            return f.read(entry[2])

    def read_path(self, path, etype=None):
        e = self.find(path, etype)
        return None if e is None else self.read(e)

    def read_json(self, path, etype=None):
        raw = self.read_path(path, etype)
        return None if raw is None else json.loads(raw.decode("utf-8-sig"))

    def anim_tags(self, sprite_path):
        """Tag names of a base sprite given as 'asset/base/.../name' (reads name#anim fanim)."""
        data = self.read_json(sprite_path + "#anim", "fanim")
        return None if data is None else list(data.get("anims", {}).keys())


def _open(args):
    game = find_game_dir(args.game)
    if not game:
        sys.exit("bundle.game_data not found. Pass --game <Teamfight Manager2 folder> or set TFM2_GAME_DIR.")
    return Bundle(game)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", help="Teamfight Manager2 install folder")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stats", help="entry count per type")
    p = sub.add_parser("list", help="list entries")
    p.add_argument("--type")
    p.add_argument("--grep", help="substring of the asset path")
    p = sub.add_parser("cat", help="print a text entry")
    p.add_argument("path")
    p.add_argument("--type")
    p = sub.add_parser("extract", help="write matching entries to disk")
    p.add_argument("--grep", required=True)
    p.add_argument("--type")
    p.add_argument("--out", required=True)
    p = sub.add_parser("sfx", help="list base sound names (usable in Sfx/TargetSfx)")
    p.add_argument("--grep", default="")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    b = _open(args)

    if args.cmd == "stats":
        from collections import Counter
        for t, n in Counter(e[0] for e in b.entries).most_common():
            print(f"{n:6d}  {t}")
    elif args.cmd == "list":
        for t, p_, size, _ in b.entries:
            if (not args.type or t == args.type) and (not args.grep or args.grep in p_):
                print(f"{t:20s} {size:>10,}  {p_}")
    elif args.cmd == "cat":
        raw = b.read_path(args.path, args.type)
        if raw is None:
            sys.exit(f"not found: {args.path}")
        sys.stdout.write(raw.decode("utf-8-sig", "replace"))
    elif args.cmd == "extract":
        n = 0
        for e in b.entries:
            t, p_ = e[0], e[1]
            if args.grep in p_ and (not args.type or t == args.type) and t != "folder":
                rel = p_.replace("asset/base/", "", 1)
                out = os.path.join(args.out, *rel.split("/")) + EXT_BY_TYPE.get(t, "." + t)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, "wb") as f:
                    f.write(b.read(e))
                n += 1
        print(f"extracted {n} entries to {args.out}")
    elif args.cmd == "sfx":
        for t, p_, _, _ in b.entries:
            if t == "sound_info" and p_.startswith("asset/base/sound/sfx/") and args.grep in p_:
                print(p_.rsplit("/", 1)[1])


if __name__ == "__main__":
    main()
