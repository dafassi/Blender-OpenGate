# OpenGate — Progress Log

Chronological development log. Newest entries at the top.

---

## 2026-06-29 — Dead code cleanup

**Removed (no callers):**
- `render_format.py`: `mask_safe_margins`, `scaled_mask_frame`, `frame_format_label`, `iter_active_frame_labels`, `_FORMAT_TIERS`, `Iterator` import
- `masks.py`: `mask_by_id`, `mask_by_flag`, `enable_mask`, `disable_mask`, `toggle_mask`, `set_mask_enabled`, `ALL_MASKS_FLAG`, `NEXT_MASK_BIT`, `image_stem`/`image_filename` properties; moved `paths` import to top
- `mask_combo_matrix.py`: `binary`, `labels`, `relpath`, `equivalent_filenames` properties, `iter_mask_combo_matrix`
- `platform_presets.py`: `delivery_resolution_label` property
- `blender_compat.py`: `blender_version`, `is_blender_5_or_newer`

**Refactored:**
- `camera_display.py`: `pull_passepartout_from_camera_to_scenes` now reuses `pull_display_settings_from_camera` (removed duplicated suppress logic + in-loop `global`)

---

## 2026-06-29 — Platform presets moved to JSON data file

**Done:**
- All platform data (resolution, FPS, duration, notes, URLs) now lives in `assets/platform_presets.json`
- `core/platform_presets.py` loads the file at import via `_load_from_json()`; `VERIFIED_AS_OF`, `DISCLAIMER`, and `PLATFORM_PRESETS` are derived from JSON
- `PlatformPreset` dataclass extended with `recommended_fps` field
- Future spec updates: edit **only** the JSON file — no Python changes needed

---

## 2026-06-29 — Leading dot on bundled PNG filenames

**Done:**
- All mask / logo PNGs use a leading `.` (e.g. `.opengate-16_9.png`)
- Code: `core/paths.py` (`IMAGE_FILENAME_DOT_PREFIX`), `masks.py`, `mask_combos.py`, `mask_combo_matrix.py`, `platform_presets.py`, `ui/branding.py`
- Docs: `MASK_COMBO_MATRIX.md`, `AGENT_CONTEXT.md`, `IMAGE_COLLECTOR.md`, `SHADER_NETWORK.md`, `README.md`

---

## 2026-06-25 — Safezones, UI polish, cleanup (v0.2.0)

**Milestone:** Platform-specific safezone masks + release hygiene

**Done:**
- Platform safezone PNGs: YouTube Shorts, Instagram Reels, TikTok (`platform_presets.py` + `mask_combos.py`)
- **Show Safezones** checkbox — visible only for presets with a safezone file; pure 9:16 required
- UI: left-aligned panel content; export resolution on one line
- Branding footer: OpenGate logo beside team credit
- Removed dead operators: `refresh_mask`, `setup_mask`
- Removed unused code: `combined_frame_label`, `_opengate_entry_mask_flags`
- Docs: `FUNCTION_MATRIX.md`, `AGENT_CONTEXT.md`, `MASK_COMBO_MATRIX.md` updated
- Version bump: `0.1.0` → **`0.2.0`**

**Next:**
- Pack images inside collector blend for fully portable asset
- More platform safezone PNGs (Stories, Facebook Reels, …) as assets arrive

---

## 2026-06-22 — Camera background images + image collector

**Milestone:** Production mask display path

**Done:**
- Replaced mesh plane / shader gates with **camera background images**
- Added `core/image_collector.py` — append `opengate-imagecollector.blend`
- Added `core/background_image.py` — backup/restore, incremental sync
- Pre-combined combo PNGs (flags 1–7) in collector blend
- `mask_combo_matrix.py` + `MASK_COMBO_MATRIX.md`
- Safe areas + passepartout (`camera_display.py`) unchanged
- Platform presets, canvas slider, branding footer
- Performance: no `image.pixels` in hot path; opacity fast path
- Removed: `shader.py`, `overlay.py`, `camera.py`, disk PNG loader

**Next:**
- Pack images inside collector blend for fully portable asset

---

## 2026-06-22 — Viewport overlay experiments (rejected)

**Done:**
- Documented approaches in `VIEWPORT_OVERLAY_MATRIX.md`
- GPU POST_PIXEL, mesh shader — rejected (latency, DOF, occlusion)

---

## 2026-06-18 — Mask bitmask registry

**Milestone:** Initial repository structure

**Done:**
- Created Blender extension layout (`blender_manifest.toml`, package, assets, development)
- Added `AGENT_CONTEXT.md` for AI agent continuity
- Added function matrix, error matrix, progress log (this file)
- Stubbed Python package: constants, properties, prefs, operators, UI, geometry nodes
- Registered minimal panel so extension loads in Blender 5.1

**Next:**
- Implement `OpenGate_Mask` shader group (alpha mix driven by `masks.py` flags)
- Wire `mask_flags` scene property to shader uniform
- Add mask PNG assets: `.opengate-16_9.png`, `.opengate-9_16.png`, `.opengate-5_4.png` (present in `assets/masks/`)

---

## 2026-06-18 — `core/` package, trim root

**Done:**
- Moved `masks.py`, `shader.py`, `overlay.py` → `core/`
- Removed `constants.py`, `apply_format` operator (platform workflow v2)
- Root now: `__init__.py`, `properties.py`, `prefs.py` only

---

**Milestone:** Clear folder structure

**Done:**
- Removed `shader_network/`, `geometry_nodes/`, `assets/geometry_nodes/` (redundant with `assets/shader/`)
- Flat modules: `shader.py` (loads blend), `overlay.py` (camera plane)
- Moved `AGENT_CONTEXT.md` → `development/AGENT_CONTEXT.md`
- Documented structure rules in agent context

**Next:**
- Test extension reload after restructure

---

## 2026-06-18 — Mask bitmask registry

**Milestone:** Shader-oriented mask system defined

**Done:**
- Added `opengate/masks.py` — bitmask IDs (16:9=1, 9:16=2, 5:4=4), registry, helpers
- Documented shader contract (alpha mix, `Mask Flags` uniform)
- Updated `AGENT_CONTEXT.md` and function matrix for shader path

**Next:**
- Build shader node group
- Scene UI for toggling mask bits / combinations

**Blockers:** None

---

*Template for future entries:*

```markdown
## YYYY-MM-DD — Short title

**Milestone:** ...

**Done:**
- ...

**Next:**
- ...

**Blockers:** ...
```
