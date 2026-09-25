"""Read League of Legends client files (read-only): WAD archives, Wwise sound packs, textures.

    from riot import Wad, xxh64, fnv1
    wad = Wad(r"D:\\WeGameApps\\lol\\Game\\DATA\\FINAL\\Champions\\Garen.wad.client")
    data = wad.read_path("assets/sounds/wwise2016/sfx/characters/garen/skins/base/garen_base_sfx_audio.bnk")

Formats (as used by the 2024-2026 clients):
  WAD 3.x   "RW" + ECDSA sig + checksum + TOC of 32-byte entries keyed by xxh64(lower-case path);
            payload raw / gzip / zstd / zstd-with-raw-prefix (Python 3.14 ships compression.zstd)
  WPK       Riot "r3d2" pack of Wwise .wem files named "<media id>.wem"
  BNK       Wwise SoundBank: BKHD, DIDX/DATA (embedded media), HIRC (events -> actions -> sounds)
  TEX       Riot texture: "TEX\\0", size, DXT1/DXT5/BGRA8 (+ mipmaps, smallest first)
Needs only the standard library (+ Pillow for textures).
"""
import gzip
import io
import os
import struct

try:
    from compression import zstd  # Python 3.14+
except ImportError:  # pragma: no cover
    zstd = None

M64 = 0xFFFFFFFFFFFFFFFF
P1, P2, P3, P4, P5 = (0x9E3779B185EBCA87, 0xC2B2AE3D27D4EB4F, 0x165667B19E3779F9,
                      0x85EBCA77C2B2AE63, 0x27D4EB2F165667C5)


def _rotl(x, r):
    return ((x << r) | (x >> (64 - r))) & M64


def _round(acc, lane):
    return (_rotl((acc + lane * P2) & M64, 31) * P1) & M64


def xxh64(data, seed=0):
    """XXH64 (WAD path hashes use the lower-case path, seed 0)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    n, p = len(data), 0
    if n >= 32:
        v = [(seed + P1 + P2) & M64, (seed + P2) & M64, seed & M64, (seed - P1) & M64]
        while p <= n - 32:
            for i in range(4):
                v[i] = _round(v[i], int.from_bytes(data[p:p + 8], "little"))
                p += 8
        h = (_rotl(v[0], 1) + _rotl(v[1], 7) + _rotl(v[2], 12) + _rotl(v[3], 18)) & M64
        for x in v:
            h = ((h ^ _round(0, x)) * P1 + P4) & M64
    else:
        h = (seed + P5) & M64
    h = (h + n) & M64
    while p + 8 <= n:
        h ^= _round(0, int.from_bytes(data[p:p + 8], "little"))
        h = (_rotl(h, 27) * P1 + P4) & M64
        p += 8
    if p + 4 <= n:
        h ^= (int.from_bytes(data[p:p + 4], "little") * P1) & M64
        h = (_rotl(h, 23) * P2 + P3) & M64
        p += 4
    while p < n:
        h ^= (data[p] * P5) & M64
        h = (_rotl(h, 11) * P1) & M64
        p += 1
    h ^= h >> 33
    h = (h * P2) & M64
    h ^= h >> 29
    h = (h * P3) & M64
    return h ^ (h >> 32)


def fnv1(name):
    """Wwise short id: FNV-1 32-bit of the lower-case name."""
    h = 2166136261
    for b in name.lower().encode("utf-8"):
        h = (h * 16777619) & 0xFFFFFFFF
        h ^= b
    return h


def _lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# ----------------------------------------------------------------------------- WAD
class Wad:
    ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

    def __init__(self, path):
        self.path = path
        with open(_lp(path), "rb") as f:
            head = f.read(4)
            if head[:2] != b"RW":
                raise ValueError(f"not a WAD: {path}")
            self.version = (head[2], head[3])
            if head[2] >= 3:
                f.seek(4 + 256 + 8)
            elif head[2] == 2:
                f.seek(4 + 1 + 83 + 8 + 2 + 2)   # ecdsa length + sig + checksum + toc start/size
            else:
                f.seek(4 + 4)
            (count,) = struct.unpack("<I", f.read(4))
            self.entries = {}
            for _ in range(count):
                h, off, csize, size, typ, dup, sub, _crc = struct.unpack("<QIIIBBHQ", f.read(32))
                self.entries[h] = (off, csize, size, typ)

    def has(self, path):
        return xxh64(path.lower()) in self.entries

    def read(self, h):
        off, csize, size, typ = self.entries[h]
        with open(_lp(self.path), "rb") as f:
            f.seek(off)
            raw = f.read(csize)
        kind = typ & 0xF
        if kind == 0:
            return raw
        if kind == 1:
            return gzip.decompress(raw)
        if kind == 2:
            raise ValueError("satellite/link entry")
        if kind == 3:
            return zstd.decompress(raw)
        if kind == 4:  # zstd with an uncompressed prefix (subchunked)
            i = raw.find(self.ZSTD_MAGIC)
            return raw if i < 0 else raw[:i] + zstd.decompress(raw[i:])
        raise ValueError(f"unknown WAD entry type {typ}")

    def read_path(self, path):
        return self.read(xxh64(path.lower()))


# ----------------------------------------------------------------------------- Wwise
def parse_wpk(data):
    """Riot WPK -> {media id (int): wem bytes}."""
    if data[:4] != b"r3d2":
        raise ValueError("not a WPK")
    _ver, count = struct.unpack_from("<II", data, 4)
    offsets = struct.unpack_from(f"<{count}I", data, 12)
    out = {}
    for o in offsets:
        if not o:
            continue
        doff, dsize, nlen = struct.unpack_from("<III", data, o)
        name = data[o + 12:o + 12 + nlen * 2].decode("utf-16-le")
        out[int(name.split(".")[0])] = data[doff:doff + dsize]
    return out


def bnk_sections(data):
    """Wwise bank -> {section tag: bytes}."""
    out, p = {}, 0
    while p + 8 <= len(data):
        tag = data[p:p + 4].decode("ascii", "replace")
        (size,) = struct.unpack_from("<I", data, p + 4)
        out[tag] = data[p + 8:p + 8 + size]
        p += 8 + size
    return out


def bnk_media(data):
    """Embedded media of a bank: {media id: wem bytes} (DIDX + DATA)."""
    s = bnk_sections(data)
    didx, blob = s.get("DIDX", b""), s.get("DATA", b"")
    out = {}
    for i in range(0, len(didx), 12):
        mid, off, size = struct.unpack_from("<III", didx, i)
        out[mid] = blob[off:off + size]
    return out


def hirc_objects(data):
    """HIRC objects of a bank: {object id: (type, body bytes)}."""
    s = bnk_sections(data).get("HIRC", b"")
    if not s:
        return {}
    (count,) = struct.unpack_from("<I", s, 0)
    p, out = 4, {}
    for _ in range(count):
        typ, size, oid = struct.unpack_from("<BII", s, p)
        out[oid] = (typ, s[p + 9:p + 5 + size])
        p += 5 + size
    return out


def bank_version(data):
    s = bnk_sections(data)
    return struct.unpack_from("<I", s["BKHD"], 0)[0] if "BKHD" in s else None


# ----------------------------------------------------------------------------- events -> media
class SoundBanks:
    """Resolve Wwise event names to the media (.wem) they can play (bank version 145)."""

    SOUND, ACTION, EVENT = 2, 3, 4

    def __init__(self, banks, media):
        self.h = {}
        for b in banks:
            self.h.update(hirc_objects(b))
        self.media = media

    def _children(self, body):
        """Container children: the first `u32 count + count known object ids` run in the body."""
        for i in range(0, len(body) - 8):
            (n,) = struct.unpack_from("<I", body, i)
            if 0 < n <= 64 and i + 4 + 4 * n <= len(body):
                ids = struct.unpack_from(f"<{n}I", body, i + 4)
                if all(x in self.h for x in ids):
                    return list(ids)
        return []

    def _resolve(self, oid, seen):
        if oid in seen or oid not in self.h:
            return []
        seen.add(oid)
        typ, body = self.h[oid]
        if typ == self.SOUND:
            return [struct.unpack_from("<I", body, 5)[0]]
        if typ == self.ACTION:
            return self._resolve(struct.unpack_from("<I", body, 2)[0], seen)
        if typ == self.EVENT:
            n = body[0]
            out = []
            for aid in struct.unpack_from(f"<{n}I", body, 1):
                out += self._resolve(aid, seen)
            return out
        out = []
        for c in self._children(body):
            out += self._resolve(c, seen)
        return out

    def event_media(self, name):
        """Media ids an event can play (random containers give several variants)."""
        return [m for m in dict.fromkeys(self._resolve(fnv1(name), set())) if m in self.media]
