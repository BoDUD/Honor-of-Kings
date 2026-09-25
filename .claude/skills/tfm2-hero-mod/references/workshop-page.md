# Steam Workshop page template (oppi's proven layout)

Both benchmark packs (LoL Reborn 3774304166, 122 ratings; Dota 2 Heroes 3770621310, 53 ratings)
reuse one presentation. Title pattern: `(<count>) <Franchise> <Pack name> - <newest hero>` or
`<Franchise> Heroes - <hero list>`; update the title with every release so subscribers notice.

## Images

1. **Thumbnail** (`thumbnail.png` / `preview.png`, square ~650-1280 px): a frame styled like the
   franchise's own UI (LoL gold filigree, Dota red-bronze), a top line
   `<FRANCHISE> / HEROES BY <credits>`, the newest hero's **official splash art** inside the frame,
   a white "NEW UPDATE" burst, and the hero's name on a plate in a chunky pixel font.
2. **New update banner** (16:9): the 3 newest heroes as big upscaled sprites (nearest-neighbour)
   on a desaturated franchise background, names in gold pixel font, arrows "Sprite Showcase ->".
3. **Sprite showcase GIF** (16:9): the newest hero cycling idle / attack / each skill / ult with
   its VFX - this is the image that sells the update.
4. **Collection page**: a grid mimicking the franchise UI ("COLLECTION - HEROES") with every
   released hero and empty slots for upcoming ones (a public roadmap).
5. **Reworked cards** (when a hero changes): "NEW REWORKED <hero>", before/after sprites side
   by side, ability cards with level, cooldown and numbers.
6. Optional roster overview listing all heroes by role.

Build these from `tfm2_ase.py render` output upscaled x4-x6 with nearest-neighbour, never smoothed.

## Description (Steam BBCode) skeleton

```
[h1]<Pack name>[/h1]
[b]Read first:[/b] save/DB notes for players upgrading from older versions.

[h2]About[/h2]
Adds <franchise> heroes whose data and abilities are rebalanced for TFM2.
Unique sprites that stay close to the base game's art style.
Only heroes that the game's data system can currently express.

[h2]Pack includes[/h2]
Released: A, B, C
Upcoming: D, E

[h2]Localization[/h2]
English, 简体中文, 繁體中文, ... - corrections welcome.

[h2]Credits[/h2]
Sprites: ... / Code: ... / Translations: ... / Testers: ...

[h2]Compatibility[/h2]
Requires Teamfight Manager 2 base >= x.y.z. Data-only mod: no executable or bundle changes.

[h2]Disclaimer[/h2]
Free, non-commercial fan mod. <Franchise> and its characters belong to <owner>.

[h2]Other mods / community[/h2]
links, Discord channel
```

## Change notes

Keep a `WORKSHOP_CHANGE_NOTE_<version>.txt` per release (LoL Reborn does) and paste it into the
uploader's "What changed in this version?" box: new hero with a one-line kit summary, balance
changes with old -> new numbers, fixes, credits.

## Listening loop

Comments are the bug tracker: localization mistakes, units pushed out of place by a skill,
balance complaints and hero requests all arrive there. Reply as the creator, batch fixes into the
next version, credit contributors by name.
