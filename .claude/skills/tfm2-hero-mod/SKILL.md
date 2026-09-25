---
name: tfm2-hero-mod
description: >-
  Build, port, review and publish hero (champion) mods for Teamfight Manager 2 (TFM2, 团战经理2,
  Steam app 3009300): data-only packs made of mod.mod_info, mod.override_info,
  champion/*.data_champion JSON kits, Aseprite pixel sprites (.aseprite or #sheet.png +
  #anim.fanim), 64x64 skill icons, champion.i18n text, champion_view offsets and sfx
  .sound_info files, plus the Steam Workshop page. Use this skill whenever the user wants to add
  heroes from another game (王者荣耀/Honor of Kings, League of Legends, Dota 2, anime...) to TFM2,
  design or balance a TFM2 skill kit or effect tree, draw or check TFM2-style pixel sprites or VFX,
  write TFM2 localization, debug a mod hero that does not load / shows no animation / has invisible
  effects or silent sounds, or prepare a Workshop release - even if they only say
  "做个团战经理的英雄", "port this hero", or "make a mod character".
---

# TFM2 hero mods

TFM2 heroes are pure data: a JSON kit, a pixel sprite, three icons, text and sounds, wired
together by asset paths. This skill distils the base game's own data (68 champions, 78 sprites,
read from `bundle.game_data`) and the best-rated Workshop packs - oppi's *League of Legends
Reborn* (3774304166) and *Dota 2 Heroes* (3770621310), plus the Touhou pack - into rules,
templates and checkers. Numbers are measured; guesses are marked *(inferred)* in the references.

## How a hero is wired

```
champion/<hero>.data_champion
  id ─────────────────────────────> text/champion.i18n  description.<id>.* / skill_name.<id>.*
  sprite: asset/<mod_id>/champions/<hero> ──> <hero>.aseprite   tags: idle run attack skill skill2 ult hit dead ...
  skill_icons: asset/<mod_id>/icons/<hero>_skill{,2}, _ult ──> 64x64 PNG
  attack|skill|skill2|ult
     action_name ──────────────────> a sprite tag (must exist)
     effect tree ─ projectile names ─> view_projectiles ─> anim + tag
                 ─ ViewEffect names ─> view_effects ────> anim + tag
                 ─ buff names ───────> view_buffs ──────> anim + tag
                 ─ Sfx names ────────> asset/base/sound/sfx/<name> (override_info -> your .sound_info)
style/champion_view.champion_view ─> face/center offsets for <id>
mod.override_info merges text + champion_view into base, injects custom sounds
```

A broken link anywhere in this chain fails silently (no animation, invisible VFX, no sound,
empty tooltip). That is why the linter exists - run it after every edit.

## Workflow

1. **Choose the hero** - score candidates with `references/porting-heroes.md` (recognition,
   kit fit, sprite cost, roster gap, showcase). Only build heroes the data system can express.
2. **Design the kit on paper** - map passive/skills to `attack`/`skill`/`skill2`/`ult`, pick
   effect types from `references/champion-data.md`, set numbers inside the base ranges there.
   Remember the AI casts skills whenever a target is in range.
3. **Start from the template** - copy `templates/mymod/` (a lint-clean skeleton hero that
   borrows base sprite/effects/sounds as placeholders), rename `mymod`/`mymod_hero`, rewrite the kit.
   The skeleton hero is lint-clean against the base bundle but has not been play-tested; its
   patterns are copied from shipped packs.
4. **Make the art** - follow `references/art-spec.md` (35 px chibi, 1 px black outline, no
   anti-aliasing, hard 3-4 step shading, facing right; saturated outline-free VFX). Check with
   `python scripts/tfm2_ase.py metrics <sprite>` and preview with `render`.
5. **Text and sound** - `references/text-audio.md` (colour codes, icon ids, sound overrides).
6. **Validate** - `python scripts/lint_mod.py <mod folder>` (add `--game <TFM2 folder>` if the
   game is not in a standard Steam path) until 0 errors; read every WARN.
7. **Play-test** - copy to `<game>/mods/<mod_id>/`, enable in the Mods menu, watch each action,
   compare the hero's height with a base champion. Details: `references/mod-structure.md`.
8. **Publish** - `TFM2ModUploader.exe` + the page layout in `references/workshop-page.md`.

## Rules that prevent silent failures

- Namespace everything: champion id `<mod>_<hero>`, and every buff / projectile / effect / sfx
  name `<mod>_<hero>_<thing>`.
- Paths are `asset/<mod_id>/<path without extension>`; `mod_id` never changes after release.
- `action_name` and every `CasterAnimation` name must be tags in the hero's sprite.
- Every projectile / ViewEffect / buff that should be seen needs a view entry with the exact
  same name; typos compile fine and draw nothing.
- Time is ticks: 60 ticks = 1 s. Ratios are percent (`attack_ratio: 120` = 120% AD).
- `text/champion` and `style/champion_view` are `merge` overrides - never `override`.
- Custom sounds need override entries for both the sound name and its clip.
- Do not use `Native`, `ShrinkingBarrier`, `AddStatScaledBuff` or `Rush` - base-only effects.
- Never translate stat-icon ids inside `<i#...:ad_0>` tags.

## Bundled resources

| Path | Use it for |
|---|---|
| `references/mod-structure.md` | folders, manifests, override rules, asset paths, local testing, uploader |
| `references/champion-data.md` | full schema, units, base balance ranges, effect catalogue, buff fields, view bindings, proven patterns |
| `references/art-spec.md` | sprite/VFX/icon spec with measured numbers, animation tags and timings, anchoring, QA |
| `references/text-audio.md` | i18n structure, rich-text colours and icons, champion_view, sound_info |
| `references/porting-heroes.md` | adapting HoK / LoL / Dota kits, mechanic->effect feasibility, hero scoring |
| `references/workshop-page.md` | thumbnail, showcase GIF, collection page, BBCode description, change notes |
| `scripts/lint_mod.py` | static validation of a whole mod folder (exit 1 on errors) |
| `scripts/tfm2_ase.py` | `info` / `render` / `metrics` for .aseprite, exported sheets, or base sprites by asset path |
| `scripts/bundle_tool.py` | list / cat / extract base assets, list base sound names |
| `templates/mymod/` | skeleton mod: manifest, override_info, one hero, 4-language text, champion_view, icons |

Scripts need Python 3.9+ and Pillow (`pip install pillow`). They only read the game files.

## When reporting back to the user

Say which checks ran and what they found (lint counts, sprite metrics), what was verified
in-game versus only statically, and which parts of a ported kit were approximated and why.
