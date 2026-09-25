#!/usr/bin/env python3
"""Static checks for a Teamfight Manager 2 data-only mod folder.

    python lint_mod.py <mod folder> [--game <Teamfight Manager2 folder>] [-v]

Catches the mistakes that make heroes break silently: invalid JSON, sprite / anim / icon paths
that do not resolve, action_name or CasterAnimation tags missing from the sprite, projectile /
ViewEffect names without a view binding (invisible VFX), view bindings nothing uses (usually a
typo), SwitchByBuff on a buff nobody adds, missing i18n text, custom sfx that were never injected
into asset/base/sound/sfx, override_info targets that do not exist, id collisions with base.
With --game (or TFM2_GAME_DIR / a standard Steam path) asset/base/... references are resolved
through bundle.game_data as well. Exit code 1 when errors were found.
"""
import argparse
import difflib
import glob
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

KNOWN_EFFECTS = {
    # flow
    "Combine", "Delayed", "WithSelf", "SwitchByBuff", "SwitchByLevel3", "RandomTarget", "RangeEffect",
    # damage / sustain
    "Attack", "ApAttack", "FixedAttack", "Heal", "Shield", "AddCasted",
    # buffs
    "AddBuff", "AddCasterBuff", "RemoveCasterBuff",
    # crowd control / states
    "Stun", "Airborne", "Bind", "Taunt", "Charm", "Fear", "Banish", "Knockback", "Pull", "Grab",
    "BlockAttack", "BlockSkill", "BlockMoveSkill", "Invisible", "CasterInvisible",
    # movement
    "MoveTo", "MoveToTarget", "MoveBack", "RushTime", "RushMoveToBack", "Teleport", "DirTeleport",
    # projectiles / zones
    "TargetProjectile", "AutoTargetProjectile", "TargetSplashProjectile", "LinearProjectile",
    "BackToCasterLinearProjectile", "ParabolicProjectile", "LineRangeProjectile", "RangeProjectile",
    "RangePeriodProjectile", "ApplyInProjectile",
    # presentation
    "ViewEffect", "CasterViewEffect", "CasterAnimation", "RemoveCasterAnimation", "Sfx", "TargetSfx",
}
BASE_ONLY_EFFECTS = {"Native", "ShrinkingBarrier", "AddStatScaledBuff", "Rush"}
PROJECTILE_EFFECTS = {"TargetProjectile", "AutoTargetProjectile", "TargetSplashProjectile", "LinearProjectile",
                      "BackToCasterLinearProjectile", "ParabolicProjectile", "LineRangeProjectile",
                      "RangeProjectile", "RangePeriodProjectile", "ApplyInProjectile"}
CATEGORIES = {"Melee", "Range", "Magician", "Util", "Assassin"}
CASTING_TYPES = {"Targeting", "Direction", "Position", "None"}
CASTING_TARGETS = {"Enemy", "EnemyWithoutTower", "EnemyChampion", "EnemyChampionInCC", "EnemyChampionRecentlyAttacked",
                   "AllyOnlySelf", "AllyChampion", "AllyNotSelf", "AllyChampionInCC", "BothWithoutTower",
                   "BothChampion", "Ally"}
ATTACK_TYPES = {"BaseAttack", "Skill"}
HEAL_TYPES = {"Caster", "Ally", "Any"}
STAT_KEYS = ["attack", "magic_power", "hp", "defence", "magic_resistance", "move_speed", "hp_regen", "stack",
             "crit_chance"]
STAT_ICONS = {"ad_0", "ap_0", "attack_speed_0", "speed_0", "hp_0", "range_0", "armor_0", "magic resistance_0"}
ACTIONS = ("attack", "skill", "skill2", "ult")
AUDIO_EXT = (".mp3", ".wav", ".ogg")


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, where, msg):
        self.items.append((level, where, msg))

    def error(self, where, msg):
        self.add("ERROR", where, msg)

    def warn(self, where, msg):
        self.add("WARN", where, msg)

    def info(self, where, msg):
        self.add("INFO", where, msg)

    def dump(self, verbose):
        order = {"ERROR": 0, "WARN": 1, "INFO": 2}
        for level, where, msg in sorted(self.items, key=lambda x: (order[x[0]], x[1])):
            if level == "INFO" and not verbose:
                continue
            print(f"{level:5s} {where}: {msg}")
        n = {k: sum(1 for i in self.items if i[0] == k) for k in order}
        hidden = "" if verbose else " (use -v to show INFO)"
        print(f"\n{n['ERROR']} errors, {n['WARN']} warnings, {n['INFO']} info{hidden}")
        return n["ERROR"]


def load_json(path, rep, where=None):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        rep.error(where or path, f"invalid JSON: {e}")
        return None


def aseprite_tags(path):
    """Read only the tag names of an .aseprite file (tags live in the first frame)."""
    with open(path, "rb") as f:
        data = f.read()
    nframes = struct.unpack_from("<H", data, 6)[0]
    pos, tags = 128, []
    for _ in range(nframes):
        fbytes, _, oldc = struct.unpack_from("<IHH", data, pos)
        newc = struct.unpack_from("<I", data, pos + 12)[0]
        cp = pos + 16
        for _ in range(newc or oldc):
            csize, ctype = struct.unpack_from("<IH", data, cp)
            if ctype == 0x2018:
                n = struct.unpack_from("<H", data, cp + 6)[0]
                tp = cp + 16
                for _ in range(n):
                    nl = struct.unpack_from("<H", data, tp + 17)[0]
                    tags.append(data[tp + 19: tp + 19 + nl].decode("utf-8", "replace"))
                    tp += 19 + nl
                return tags
            cp += csize
        pos += fbytes
    return tags


def long_path(p):
    """On Windows, lift the 260-character limit (deep Steam / OneDrive / app-sandbox folders)."""
    p = os.path.abspath(p)
    if os.name == "nt" and not p.startswith("\\\\?\\"):
        p = "\\\\?\\UNC\\" + p[2:] if p.startswith("\\\\") else "\\\\?\\" + p
    return p


class Mod:
    def __init__(self, root, rep, bundle):
        self.root = long_path(root)
        self.rep = rep
        self.bundle = bundle
        self.mod_id = None
        self.override = {}
        self._tag_cache = {}

    def rel(self, p):
        return os.path.relpath(p, self.root).replace("\\", "/")

    # --- resolving asset paths -------------------------------------------------------
    def local(self, asset_path):
        """asset/<mod_id>/x/y -> absolute path stem inside the mod, else None."""
        prefix = f"asset/{self.mod_id}/"
        if self.mod_id and asset_path.startswith(prefix):
            return os.path.join(self.root, *asset_path[len(prefix):].split("/"))
        return None

    def find_file(self, asset_path, exts):
        stem = self.local(asset_path)
        if stem is None:
            return None
        for e in exts:
            if os.path.isfile(stem + e):
                return stem + e
        return None

    def sprite_tags(self, asset_path):
        """Tag list for a sprite/anim path, None if unresolvable, 'unknown' if unverifiable."""
        if asset_path in self._tag_cache:
            return self._tag_cache[asset_path]
        tags = None
        stem = self.local(asset_path)
        if stem is not None:
            if os.path.isfile(stem + ".aseprite"):
                tags = aseprite_tags(stem + ".aseprite")
            elif os.path.isfile(stem + ".ase"):
                tags = aseprite_tags(stem + ".ase")
            elif os.path.isfile(stem + "#anim.fanim") and os.path.isfile(stem + "#sheet.png"):
                d = load_json(stem + "#anim.fanim", self.rep)
                tags = list((d or {}).get("anims", {}).keys())
        elif asset_path.startswith("asset/base/"):
            tags = self.bundle.anim_tags(asset_path) if self.bundle else "unknown"
        else:
            tags = "unknown"  # another mod's namespace
        self._tag_cache[asset_path] = tags
        return tags

    def asset_exists(self, asset_path, exts):
        if self.local(asset_path) is not None:
            return self.find_file(asset_path, exts) is not None
        if asset_path.startswith("asset/base/"):
            if not self.bundle:
                return None
            return self.bundle.has(asset_path) or self.bundle.has(asset_path + "#sheet")
        return None


def hint(name, candidates):
    close = difflib.get_close_matches(name, list(candidates), n=1, cutoff=0.75)
    return f" (did you mean '{close[0]}'?)" if close else ""


def sfx_names(node):
    """Every Sfx / TargetSfx name inside an effect tree."""
    if isinstance(node, dict):
        own = {node["name"]} if node.get("type") in ("Sfx", "TargetSfx") and node.get("name") else set()
        return own.union(*(sfx_names(v) for v in node.values()))
    if isinstance(node, list):
        return set().union(*(sfx_names(v) for v in node))
    return set()


def walk_effects(node, out):
    if isinstance(node, dict):
        t = node.get("type")
        if isinstance(t, str):
            out["types"].append(t)
            name = node.get("name")
            if t in PROJECTILE_EFFECTS and name:
                out["projectiles"].add(name)
            if t in ("ViewEffect", "CasterViewEffect") and name:
                out["view_effects"].add(name)
            if t in ("CasterAnimation", "RemoveCasterAnimation") and name:
                out["anims"].add(name)
            if t in ("Sfx", "TargetSfx") and name:
                out["sfx"].add(name)
            if t == "SwitchByBuff" and node.get("buff_name"):
                out["switch_buffs"].add(node["buff_name"])
            if t == "RemoveCasterBuff" and name:
                out["removed_buffs"].add(name)
            if t == "ParabolicProjectile" and node.get("range_effect_name"):
                out["view_effects"].add(node["range_effect_name"])
            for k in ("end_effect_name", "lock_effect_name"):
                if node.get(k):
                    out["view_effects"].add(node[k])
            for k in ("casting_target", "applied_target", "target"):
                if isinstance(node.get(k), str) and node[k] not in CASTING_TARGETS:
                    out["bad_enum"].append((t, k, node[k]))
            if t == "Heal" and node.get("heal_type") not in HEAL_TYPES:
                out["bad_enum"].append((t, "heal_type", node.get("heal_type")))
        bs = node.get("buff_state")
        if isinstance(bs, dict) and bs.get("name"):
            out["buffs"].add(bs["name"])
            d = bs.get("duration")
            if d is None:
                out["no_duration"].add(bs["name"])
            elif not (d in ("Permanent", "WithShield") or (isinstance(d, dict) and "Time" in d)):
                out["bad_enum"].append(("buff_state", "duration", json.dumps(d)))
        for v in node.values():
            walk_effects(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_effects(v, out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mod_dir")
    ap.add_argument("--game", help="Teamfight Manager2 folder (resolves asset/base/... via bundle.game_data)")
    ap.add_argument("--no-game", action="store_true", help="do not look for the base game bundle")
    ap.add_argument("-v", "--verbose", action="store_true", help="also print INFO lines")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # non-UTF-8 consoles (cp936/cp932) must not crash on Thai/Hawaiian text
        sys.stdout.reconfigure(errors="backslashreplace")
    rep = Report()

    bundle = None
    if not args.no_game:
        from bundle_tool import Bundle, find_game_dir
        gd = find_game_dir(args.game)
        if gd:
            bundle = Bundle(gd)
        else:
            rep.info("game", "bundle.game_data not found: asset/base/... references are not verified (pass --game)")

    mod = Mod(args.mod_dir, rep, bundle)
    root = mod.root

    # ---------------------------------------------------------------- mod.mod_info
    info_path = os.path.join(root, "mod.mod_info")
    if not os.path.isfile(info_path):
        rep.error("mod.mod_info", "missing - the game only recognises folders with mod.mod_info")
        return rep.dump(args.verbose) and 1
    info = load_json(info_path, rep, "mod.mod_info") or {}
    for k in ("mod_id", "name", "version", "author", "dependencies"):
        if k not in info:
            rep.warn("mod.mod_info", f"missing '{k}'")
    mod.mod_id = info.get("mod_id")
    if mod.mod_id == "base":
        rep.error("mod.mod_info", "mod_id 'base' is reserved for bundled game assets")
    elif mod.mod_id and not re.fullmatch(r"[a-z0-9_]+", mod.mod_id):
        rep.warn("mod.mod_info", f"mod_id '{mod.mod_id}' should be lowercase snake_case (it becomes asset/<mod_id>/)")
    if not any(d.get("mod_id") == "base" for d in info.get("dependencies", []) if isinstance(d, dict)):
        rep.warn("mod.mod_info", "no dependency on 'base' (packs declare {\"mod_id\": \"base\", \"version\": \">=x.y.z\"})")

    # ---------------------------------------------------------------- mod.override_info
    ov_path = os.path.join(root, "mod.override_info")
    if os.path.isfile(ov_path):
        mod.override = load_json(ov_path, rep, "mod.override_info") or {}
        for key, val in mod.override.items():
            where = f"mod.override_info[{key}]"
            if not isinstance(val, dict) or "remapping" not in val:
                rep.error(where, "entry needs {\"remapping\": ..., \"type\": \"merge\"|\"override\"}")
                continue
            if val.get("type") not in ("merge", "override"):
                rep.error(where, f"type must be merge or override, got {val.get('type')!r}")
            target = val["remapping"]
            if not target.startswith(f"asset/{mod.mod_id}/"):
                rep.error(where, f"remapping '{target}' is not inside asset/{mod.mod_id}/")
            elif mod.find_file(target, ("", ".png", ".aseprite", ".i18n", ".champion_view", ".sound_info", ".mp3",
                                        ".wav", ".ogg", ".ui", ".fanim", ".sprite_sheet", ".json", ".style")) is None \
                    and mod.sprite_tags(target) is None:
                rep.error(where, f"remapping target '{target}' does not exist in the mod")
            if key in ("asset/base/text/champion", "asset/base/style/champion_view") and val.get("type") != "merge":
                rep.error(where, "must be type 'merge' - 'override' would wipe every base champion entry")
    else:
        rep.warn("mod.override_info", "missing - champion text, champion_view and custom sfx are injected through it")

    # ---------------------------------------------------------------- text + champion_view
    text_target = (mod.override.get("asset/base/text/champion") or {}).get("remapping")
    i18n = {}
    if text_target:
        p = mod.find_file(text_target, (".i18n", ""))
        if p:
            i18n = load_json(p, rep, mod.rel(p)) or {}
    else:
        rep.warn("mod.override_info", "no merge for asset/base/text/champion - heroes will have no names/tooltips")
    langs = list(i18n.keys())
    for lang, block in i18n.items():
        for sect in ("description", "skill_name"):
            for cid, entry in (block.get(sect) or {}).items():
                for k, s in (entry or {}).items():
                    if not isinstance(s, str):
                        continue
                    opens = len(re.findall(r"<#[0-9a-fA-F]{6,8}>", s))
                    closes = s.count("<>")
                    if opens != closes:
                        rep.warn(f"i18n {lang}.{sect}.{cid}.{k}", f"{opens} colour tags vs {closes} '<>' closers")
                    for icon in re.findall(r"<i#asset/base/ui/banpick/champion_stat_icon:([^>]+)>", s):
                        if icon not in STAT_ICONS:
                            rep.warn(f"i18n {lang}.{sect}.{cid}.{k}", f"unknown stat icon '{icon}'")

    cv_target = (mod.override.get("asset/base/style/champion_view") or {}).get("remapping")
    cview = {}
    if cv_target:
        p = mod.find_file(cv_target, (".champion_view", ""))
        cview = ((load_json(p, rep, mod.rel(p)) or {}).get("entries") or {}) if p else {}

    # ---------------------------------------------------------------- sounds
    sfx_dir = os.path.join(root, "sound", "sfx")
    mod_sfx = {}
    for p in glob.glob(os.path.join(glob.escape(sfx_dir), "*.sound_info")):
        name = os.path.splitext(os.path.basename(p))[0]
        mod_sfx[name] = p
        d = load_json(p, rep, mod.rel(p)) or {}
        for play in d.get("plays", []):
            clip = play.get("clip")
            if not clip:
                rep.error(mod.rel(p), "play without 'clip'")
                continue
            if not any(os.path.isfile(os.path.join(sfx_dir, clip + e)) for e in AUDIO_EXT):
                rep.error(mod.rel(p), f"clip '{clip}' has no audio file ({'/'.join(AUDIO_EXT)}) next to it")
            elif f"asset/base/sound/sfx/{clip}" not in mod.override:
                rep.info(mod.rel(p), f"clip '{clip}' has no override entry (published packs add one per clip too)")

    # ---------------------------------------------------------------- champions
    base_ids = set()
    if bundle:
        sheet = bundle.read_json("asset/base/setting/champion_info", "champion_info_sheet") or {}
        base_ids = {k for k, v in sheet.items() if isinstance(v, dict)}
        base_ids |= {c.get("id") for c in sheet.get("mod_champions", [])}
    seen_ids = {}
    champ_files = sorted(glob.glob(os.path.join(glob.escape(root), "**", "*.data_champion"), recursive=True))
    if not champ_files:
        rep.warn("champion/", "no *.data_champion files found")
    for path in champ_files:
        where_file = mod.rel(path)
        d = load_json(path, rep, where_file)
        if d is None:
            continue
        cid = d.get("id", "?")
        W = f"{where_file} [{cid}]"
        if cid in seen_ids:
            rep.error(W, f"duplicate id (also in {seen_ids[cid]})")
        seen_ids[cid] = where_file
        if cid in base_ids:
            rep.error(W, "id collides with a base champion")
        if "_" not in cid:
            rep.warn(W, "id has no namespace prefix (use e.g. <pack>_<hero> to avoid collisions)")
        if d.get("category") not in CATEGORIES:
            rep.error(W, f"category must be one of {sorted(CATEGORIES)}")
        for block in ("stat", "growth"):
            missing = [k for k in STAT_KEYS if k not in (d.get(block) or {})]
            if missing:
                rep.error(W, f"{block} missing {missing}")

        # sprite
        sprite = d.get("sprite")
        tags = mod.sprite_tags(sprite) if sprite else None
        if not sprite:
            rep.error(W, "no 'sprite'")
        elif tags is None:
            rep.error(W, f"sprite '{sprite}' not found (.aseprite or #sheet.png + #anim.fanim)")
        elif tags == "unknown":
            rep.info(W, f"sprite '{sprite}' not verified (outside this mod, no bundle)")
        else:
            for t in ("idle", "run"):
                if t not in tags:
                    rep.error(W, f"sprite has no '{t}' tag")
            for t in ("hit", "dead"):
                if t not in tags:
                    rep.info(W, f"sprite has no '{t}' tag (all base champions have one)")

        # icons
        icons = d.get("skill_icons")
        if isinstance(d.get("skill_icon"), dict):
            src = d["skill_icon"].get("source", "")
            p = mod.find_file(src, ("#data.sprite_sheet",))
            if p:
                images = (load_json(p, rep, mod.rel(p)) or {}).get("images", {})
                for t in d["skill_icon"].get("tags", []):
                    if t not in images:
                        rep.error(W, f"skill_icon tag '{t}' not in {mod.rel(p)}")
            elif mod.local(src) is not None:
                rep.error(W, f"skill_icon source '{src}#data.sprite_sheet' not found")
        elif not icons or len(icons) != 3:
            rep.error(W, "skill_icons must list 3 icon paths (skill, skill2, ult)")
        if icons:
            for ic in icons:
                ok = mod.asset_exists(ic, (".png",))
                if ok is False:
                    rep.error(W, f"skill icon '{ic}' not found (.png)")

        # actions + effects
        found = dict(types=[], projectiles=set(), view_effects=set(), anims=set(), sfx=set(), switch_buffs=set(),
                     removed_buffs=set(), buffs=set(), bad_enum=[], no_duration=set())
        for slot in ACTIONS:
            a = d.get(slot)
            if not isinstance(a, dict):
                rep.error(W, f"missing action '{slot}'")
                continue
            WA = f"{W}.{slot}"
            for k in ("action_name", "duration", "cooltime", "start_timing", "range", "casting_type",
                      "casting_target", "attack_type", "effect"):
                if k not in a:
                    rep.error(WA, f"missing '{k}'")
            if a.get("casting_type") not in CASTING_TYPES:
                rep.error(WA, f"casting_type {a.get('casting_type')!r} not in {sorted(CASTING_TYPES)}")
            if a.get("casting_target") not in CASTING_TARGETS:
                rep.warn(WA, f"casting_target {a.get('casting_target')!r} is not one seen in shipped packs")
            if a.get("attack_type") not in ATTACK_TYPES:
                rep.error(WA, f"attack_type must be BaseAttack or Skill")
            if isinstance(a.get("duration"), int) and isinstance(a.get("start_timing"), int) \
                    and a["start_timing"] > a["duration"]:
                rep.warn(WA, "start_timing is after duration - the effect may never fire")
            an = a.get("action_name")
            if isinstance(tags, list) and an and an not in tags:
                rep.warn(WA, f"action_name '{an}' is not a tag in the sprite{hint(an, tags)} - the action will most "
                             f"likely play no animation (tags: {', '.join(tags)})")
            desc = a.get("description")
            if not desc:
                (rep.info if slot == "attack" else rep.warn)(WA, "no description (tooltip will be empty)")
            elif i18n:
                m = re.match(r"#asset/base/text/champion\?description\.([^.]+)\.(\w+)$", desc)
                if not m:
                    rep.warn(WA, f"description '{desc}' is not #asset/base/text/champion?description.<id>.<slot>")
                else:
                    miss = [lg for lg in langs if m.group(2) not in ((i18n[lg].get("description") or {})
                                                                     .get(m.group(1)) or {})]
                    if "en" in miss:
                        rep.error(WA, f"text key description.{m.group(1)}.{m.group(2)} missing in 'en'")
                    elif miss:
                        rep.info(WA, f"text key missing in {len(miss)} language(s): {', '.join(miss)}")
            walk_effects(a.get("effect"), found)
            if slot == "attack" and f"{cid}_attack" in sfx_names(a.get("effect")):
                rep.warn(WA, f"Sfx '{cid}_attack': the engine already plays <id>_attack on every basic attack, "
                             f"so it sounds twice - rename it (e.g. {cid}_attack_hit)")

        for t in found["types"]:
            if t in BASE_ONLY_EFFECTS:
                rep.error(W, f"effect type '{t}' is engine/base-only (Native effects need game code)")
            elif t not in KNOWN_EFFECTS:
                rep.warn(W, f"unknown effect type '{t}' (not seen in base or shipped packs)")
        for t, k, v in found["bad_enum"]:
            rep.warn(W, f"{t}.{k} = {v!r} is not a value seen in shipped packs")
        for nm in sorted(found["no_duration"]):
            rep.info(W, f"buff '{nm}' has no duration (shipped packs do this; set Permanent or Time explicitly)")
        if isinstance(tags, list):
            for an in sorted(found["anims"]):
                if an not in tags:
                    rep.warn(W, f"CasterAnimation '{an}' is not a tag in the sprite{hint(an, tags)}")

        # view bindings
        def check_view(kind, entries):
            names = set()
            for v in entries or []:
                nm = v.get("name")
                names.add(nm)
                anim = v.get("anim") or v.get("sprite")
                WV = f"{W}.{kind}[{nm}]"
                if not anim:
                    rep.error(WV, "no anim/sprite path")
                    continue
                if v.get("type") == "Sprite":
                    if mod.asset_exists(anim, (".png", ".aseprite")) is False:
                        rep.error(WV, f"sprite '{anim}' not found")
                    continue
                at = mod.sprite_tags(anim)
                if at is None:
                    rep.error(WV, f"anim '{anim}' not found")
                elif isinstance(at, list):
                    for tk in ("tag", "pre_tag", "loop_tag", "remove_tag"):
                        if v.get(tk) and v[tk] not in at:
                            rep.error(WV, f"{tk} '{v[tk]}' not in {anim} (tags: {', '.join(at)})")
            return names

        vp = check_view("view_projectiles", d.get("view_projectiles"))
        ve = check_view("view_effects", d.get("view_effects"))
        vb = check_view("view_buffs", d.get("view_buffs"))
        used = found["projectiles"] | found["view_effects"] | found["buffs"]
        for nm in sorted(vp - used):
            rep.warn(W, f"view_projectiles '{nm}' is used by no effect in the kit{hint(nm, used)} (dead entry or typo)")
        for nm in sorted(ve - used):
            rep.warn(W, f"view_effects '{nm}' is used by no ViewEffect/CasterViewEffect{hint(nm, used)} "
                        f"(dead entry or typo)")
        for nm in sorted(vb - used):
            rep.warn(W, f"view_buffs '{nm}' matches no buff name{hint(nm, used)} (dead entry or typo)")
        for nm in sorted(found["view_effects"] - ve - vp - vb):
            rep.warn(W, f"ViewEffect '{nm}' has no view_effects entry here{hint(nm, ve | vp | vb)} - "
                        f"nothing will be drawn")
        for nm in sorted(found["projectiles"] - vp - ve):
            rep.info(W, f"projectile '{nm}' has no view_projectiles entry (invisible; fine for hidden helpers)")
        for nm in sorted(found["switch_buffs"] - found["buffs"]):
            rep.warn(W, f"SwitchByBuff checks '{nm}' but this kit never adds that buff")

        # sfx
        for nm in sorted(found["sfx"]):
            if nm in mod_sfx:
                if f"asset/base/sound/sfx/{nm}" not in mod.override:
                    rep.warn(W, f"sfx '{nm}' exists in sound/sfx but has no override entry asset/base/sound/sfx/{nm} "
                                f"- shipped packs inject every custom sound this way, so it probably will not play")
            elif bundle is not None:
                if not bundle.has(f"asset/base/sound/sfx/{nm}", "sound_info") \
                        and f"asset/base/sound/sfx/{nm}" not in mod.override:
                    rep.warn(W, f"sfx '{nm}' is neither in this mod nor a base sound")
            else:
                rep.info(W, f"sfx '{nm}' not in this mod (assumed base sound; not verified)")

        # text + champion_view presence
        if i18n:
            for lg in langs:
                if cid not in (i18n[lg].get("description") or {}):
                    (rep.error if lg == "en" else rep.info)(W, f"no description block in i18n '{lg}'")
            if "en" not in langs:
                rep.warn(W, "i18n has no 'en' block")
            for lg in langs:
                if cid in (i18n[lg].get("skill_name") or {}):
                    break
            else:
                rep.info(W, "no skill_name entry (skill titles shown in UI)")
        if cv_target is not None and cid not in cview:
            rep.warn(W, "no champion_view entry (face/center offsets fall back to defaults)")

    return 1 if rep.dump(args.verbose) else 0


if __name__ == "__main__":
    sys.exit(main())
