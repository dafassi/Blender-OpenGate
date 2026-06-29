# OpenGate — Agent Context (Self-Learning)

> Living document for AI agents. Update when architecture or conventions change.

---

## Project snapshot

| Field | Value |
|-------|-------|
| Name | OpenGate |
| Type | Blender extension (add-on), schema 1.0.0 |
| Blender min | 4.2.0 (developed on 5.1) |
| Language | **English only** (code, UI, docs) |
| Philosophy | Lightweight, intuitive, zero bloat |
| Domain | Viewport framing masks for social aspect ratios |

## What OpenGate does

1. User picks a **target camera** in the OpenGate panel.
2. User toggles aspect masks (16:9, 9:16, 5:4) → bitmask → **one pre-combined PNG** as a **camera background image**.
3. Mask images ship inside **`assets/shader/opengate-imagecollector.blend`** — appended once via `core/image_collector.py`.
4. **Platform presets** can expose **9:16 safezone variants** (e.g. IG / YT / TT PNGs) when *Show Safezones* is enabled.
5. **Safe Areas + Passepartout** in Solid view show crop guides without blocking geometry (DOF-safe).
6. **Canvas slider** sets square Open Gate render resolution (4320×4320 at 100%).

## Repository layout

```
opengate/
├── blender_manifest.toml
├── __init__.py
├── properties.py, prefs.py
├── core/
│   ├── masks.py                   # bitmask registry
│   ├── mask_combos.py             # combo filename parsing + flags
│   ├── mask_combo_matrix.py       # canonical combo → image name (flags 1–7)
│   ├── image_collector.py         # append opengate-imagecollector.blend
│   ├── background_image.py        # camera background sync, backup/restore
│   ├── camera_display.py          # safe areas, passepartout
│   ├── camera_target.py           # target camera selection
│   ├── handlers.py                # msgbus refresh on render changes
│   ├── render_format.py           # canvas resolution presets
│   ├── platform_presets.py        # loads assets/platform_presets.json at import
│   ├── mask_setup.py              # thin wrapper for operators
│   └── paths.py                   # extension root + IMAGE_FILENAME_DOT_PREFIX
├── operators/
├── ui/
├── assets/
│   ├── platform_presets.json      # ← edit this to update platform specs
│   ├── .opengate-logo_rev0.png    # panel / prefs branding (leading dot)
│   ├── shader/
│   │   └── opengate-imagecollector.blend   # mask images + collector object
│   └── masks/
│       └── MASK_COMBO_MATRIX.md            # human-readable combo table
└── development/                   # all documentation
```

### Structure rules (do not break)

| Rule | Rationale |
|------|-----------|
| **`core/`** | All runtime Python logic. |
| **`assets/shader/`** | Authoritative `.blend` with mask image datablocks. |
| **`assets/masks/`** | Docs only (+ optional external PNG fallback paths). |
| **`development/`** | All docs including this file. |
| **Root** | Only `__init__.py`, `properties.py`, `prefs.py` (+ manifest). |

## Mask images (current)

- **Source:** `assets/shader/opengate-imagecollector.blend`
- **Append:** object `opengate-imagecollector` + all `.opengate-*.png` image datablocks
- **Display:** single **Camera Background Image** slot (`display_depth = FRONT`, `frame_method = FIT`)
- **Combo map:** `core/mask_combo_matrix.py` + `assets/masks/MASK_COMBO_MATRIX.md`
- **One PNG per active bitmask (1–7)** — checkbox order irrelevant; id order in filename flexible
- **Filename prefix:** all bundled PNGs start with `.` (e.g. `.opengate-16_9.png`) — `core/paths.py`

The blend also contains material `opengate-mask` on the collector object — keeps image datablocks referenced; **Python does not drive shader gates anymore**.

## Mask bitmask

| Bit | Value | Aspect | Image datablock (canonical) |
|-----|-------|--------|----------------------------|
| 0 | 1 | 16:9 | `.opengate-16_9.png` |
| 1 | 2 | 9:16 | `.opengate-9_16.png` |
| 2 | 4 | 5:4 | `.opengate-5_4.png` |
| 3 | 8 | *(next)* | reserved |

Combos (flags 3–7): see `MASK_COMBO_MATRIX.md`.

## Performance rules

- **Never** call `len(image.pixels)` in hot paths (4K images = millions of floats).
- **Opacity slider:** update `entry.alpha` only — no full background rebuild.
- **Same combo active:** skip clear/re-append; swap image only when flags change.
- **`gl_load()`:** once per image (tagged via custom property).

## Blender extension conventions

- `blender_manifest.toml`, not `bl_info`.
- Relative imports (`from . import masks`).
- `bl_idname = __package__` in `prefs.py`.
- EnumProperty: static items → string default OK; dynamic callback → int default + cached list.

## Agent checklist

1. Inspect real folder tree on disk before changing paths.
2. Update `FUNCTION_MATRIX.md`, `ERROR_MATRIX.md`, `PROGRESS.md`, `IMAGE_COLLECTOR.md` when shipping work.
3. Update decision log below for non-obvious choices.
4. English only in UI and docs.
5. Keep `register()` / `unregister()` clean.

## Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-18 | Extension format | Blender 5.1, platform distribution |
| 2026-06-18 | Shader from `assets/shader/` | Artist-owned .blend, not Python nodes |
| 2026-06-18 | `core/` package | Root holds only register + properties |
| 2026-06-22 | GPU overlay experiments | Rejected — latency, DOF issues |
| 2026-06-22 | Mesh plane + shader | Rejected — occludes Solid, DOF blur |
| 2026-06-22 | **Camera background images** | DOF-safe, native Blender, real-time toggle |
| 2026-06-22 | **Pre-combined combo PNGs** | One file per bitmask; no runtime composite |
| 2026-06-22 | **`opengate-imagecollector.blend`** | Bundled images; append object keeps datablocks alive |
| 2026-06-25 | Platform safezone PNGs | Separate combo per platform (not a new bitmask bit) |
| 2026-06-29 | **Platform presets → JSON** | `assets/platform_presets.json` is single source; Python only loads |
| 2026-06-29 | **Leading dot on PNG filenames** | Bundled images use `.opengate-…` — `core/paths.py` |

---

*Last updated: 2026-06-29*
