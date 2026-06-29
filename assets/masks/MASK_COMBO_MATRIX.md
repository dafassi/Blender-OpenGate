# OpenGate — Mask Combo Matrix

Image datablock names in `assets/shader/opengate-imagecollector.blend` (appended via `core/image_collector.py`).

**Source of truth (code):** `core/mask_combo_matrix.py`

**Key idea:** One unique mask **set** → one PNG. Checkbox order and id order in the filename are both irrelevant.

---

## Rules

| Rule | Detail |
|------|--------|
| Folder | `assets/masks/` |
| Pattern | `.opengate-{mask_id}[-{mask_id}…].png` |
| Leading dot | **Required** on all bundled PNGs — see `core/paths.py` (`IMAGE_FILENAME_DOT_PREFIX`) |
| Mask ids | `16_9` (16:9) · `9_16` (9:16) · `5_4` (5:4) |
| Checkbox order | **Irrelevant** — see equivalent activations below |
| Id order in filename | **Flexible** — only **one file per combination** needed |
| Canonical name | Registry order: `16_9` → `9_16` → `5_4` (preferred when creating new files) |

---

## Matrix (flags 1–7)

| Flags | Binary | Equivalent activations → **same file** | Canonical PNG | Other accepted PNG names |
|------:|--------|----------------------------------------|---------------|--------------------------|
| 1 | `001` | 16:9 | `.opengate-16_9.png` | — |
| 2 | `010` | 9:16 | `.opengate-9_16.png` | — |
| 3 | `011` | 16:9 + 9:16 · **9:16 + 16:9** | `.opengate-16_9-9_16.png` | `.opengate-9_16-16_9.png` |
| 4 | `100` | 5:4 | `.opengate-5_4.png` | — |
| 5 | `101` | 16:9 + 5:4 · **5:4 + 16:9** | `.opengate-16_9-5_4.png` | `.opengate-5_4-16_9.png` |
| 6 | `110` | 9:16 + 5:4 · **5:4 + 9:16** | `.opengate-9_16-5_4.png` | `.opengate-5_4-9_16.png` |
| 7 | `111` | see all six orderings below | `.opengate-16_9-9_16-5_4.png` | any of the six id permutations below |

### Flags 3 — one file for both activations

| User activates | Same PNG |
|----------------|----------|
| 16:9 + 9:16 | `.opengate-16_9-9_16.png` (or `.opengate-9_16-16_9.png`) |
| **9:16 + 16:9** | ↑ **same file** |

### Flags 5 — one file for both activations

| User activates | Same PNG |
|----------------|----------|
| 16:9 + 5:4 | `.opengate-16_9-5_4.png` (or `.opengate-5_4-16_9.png`) |
| **5:4 + 16:9** | ↑ **same file** |

### Flags 6 — one file for both activations

| User activates | Same PNG |
|----------------|----------|
| 9:16 + 5:4 | `.opengate-9_16-5_4.png` (or `.opengate-5_4-9_16.png`) |
| **5:4 + 9:16** | ↑ **same file** |

### Flags 7 — one file for all six activations

| User activates (any order) | Same PNG |
|----------------------------|----------|
| 16:9 + 9:16 + 5:4 | any of the filenames below |
| 16:9 + 5:4 + 9:16 | ↑ **same file** |
| 9:16 + 16:9 + 5:4 | ↑ **same file** |
| 9:16 + 5:4 + 16:9 | ↑ **same file** |
| 5:4 + 16:9 + 9:16 | ↑ **same file** |
| **5:4 + 9:16 + 16:9** | ↑ **same file** |

Accepted filenames (all equivalent):

```
.opengate-16_9-9_16-5_4.png
.opengate-16_9-5_4-9_16.png
.opengate-9_16-16_9-5_4.png
.opengate-9_16-5_4-16_9.png
.opengate-5_4-16_9-9_16.png
.opengate-5_4-9_16-16_9.png
```

---

## Quick checklist (canonical names only)

One PNG per row — covers every activation order above:

- [ ] `.opengate-16_9.png` — flags 1
- [ ] `.opengate-9_16.png` — flags 2
- [ ] `.opengate-16_9-9_16.png` — flags 3 (also **9:16 + 16:9**)
- [ ] `.opengate-5_4.png` — flags 4
- [ ] `.opengate-16_9-5_4.png` — flags 5 (also **5:4 + 16:9**)
- [ ] `.opengate-9_16-5_4.png` — flags 6 (also **5:4 + 9:16**)
- [ ] `.opengate-16_9-9_16-5_4.png` — flags 7 (all six orderings)

---

## Platform safezone variants (9:16 only)

**Not a separate bitmask.** When the user selects a platform preset with a safezone PNG, enables **only 9:16**, and checks **Show Safezones**, Python loads the platform file instead of `.opengate-9_16.png`.

**Source of truth (code):** `core/platform_presets.py` (`safezone_filename`) + `core/mask_combos.py` (`resolve_safezone_filename`)

| Platform preset | PNG datablock |
|-----------------|---------------|
| YouTube Shorts | `.opengate-9_16-yt_safezones.png` |
| Instagram Reels | `.opengate-9_16-ig_safezones.png` |
| TikTok | `.opengate-9_16-tt_safezones.png` |
| Facebook Reels | `.opengate-9_16-fb_safezones.png` |

### Rules

| Rule | Detail |
|------|--------|
| Activation | Platform preset + **9:16 only** + Show Safezones |
| Bitmask | Still flags `2` (9:16) — safezone suffix is not a mask id |
| Filename pattern | `.opengate-9_16-{platform}_safezones.png` |
| Adding a platform | Set `safezone_filename` on `PlatformPreset` in `platform_presets.py` |

### Quick checklist (safezone PNGs)

- [ ] `.opengate-9_16-yt_safezones.png` — YouTube Shorts
- [ ] `.opengate-9_16-ig_safezones.png` — Instagram Reels
- [ ] `.opengate-9_16-tt_safezones.png` — TikTok
- [ ] `.opengate-9_16-fb_safezones.png` — Facebook Reels
