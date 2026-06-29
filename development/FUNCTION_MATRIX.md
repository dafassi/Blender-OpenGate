# OpenGate — Function Matrix

Track every feature from idea to shipped. Update status as work progresses.

**Legend:** `PLANNED` · `IN PROGRESS` · `DONE` · `DEFERRED` · `N/A`

---

## 1. Canvas & render format

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| F-005 | Apply square canvas resolution to render settings | DONE | `render_format.py`, canvas slider |
| F-006 | Canvas presets (HD, FHD, 4K, 8K) | DONE | `operators/canvas_preset.py` |
| F-007 | Live export / post crop resolution labels | DONE | Panel info block |

## 2. Mask display (camera background)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| F-010 | Pre-combined mask PNG per combo (flags 1–7) | DONE | In `opengate-imagecollector.blend` |
| F-011 | Toggle mask visibility (checkboxes + show overlay) | DONE | Bitmask → combo image |
| F-012 | Mask opacity slider | DONE | Fast path: alpha only |
| F-013 | Safe area crop guides (Solid) | DONE | `camera_display.py` |
| F-014 | Passepartout outside camera frame | DONE | Native camera property |
| F-015 | Append image collector from blend | DONE | `image_collector.py` |
| F-016 | Backup / restore user camera backgrounds | DONE | JSON on camera custom prop |
| F-017 | Combo filename order independence | DONE | `mask_combos.py` permutations |

## 3. Mask registry

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| F-020 | Mask bitmask registry (`masks.py`) | DONE | 16:9=1, 9:16=2, 5:4=4 |
| F-021 | Combo matrix (flags → image name) | DONE | `mask_combo_matrix.py` |
| F-022 | Platform delivery presets | DONE | `platform_presets.py` |
| F-023 | Auto-sync on checkbox / opacity change | DONE | `properties.py` update callbacks |
| F-024 | Clean remove OpenGate setup from scene | DONE | `operators/remove_setup.py` |
| F-025 | `mask_flags` from checkboxes | DONE | `_rebuild_mask_flags` |
| F-026 | ~~Mesh overlay aligned to view_frame~~ | N/A | Removed — background images |
| F-027 | Auto-refresh on render resolution change | DONE | `handlers.py` msgbus |
| F-028 | ~~Manual refresh mask button~~ | REMOVED | Auto-sync via property updates |
| F-029 | Platform safezone mask variants | DONE | `platform_presets.py` + `mask_combos.py` |

## 4. UI

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| F-030 | Main panel in 3D View sidebar (OpenGate tab) | DONE | `ui/panels.py` |
| F-031 | Platform dropdown | DONE | With duration / crop hints |
| F-032 | Framing mask checkboxes | DONE | 16:9, 9:16, 5:4 + safezones per platform |
| F-033 | Live canvas / crop resolution info | DONE | Panel labels |
| F-034 | ~~One-click Apply format~~ | DEFERRED | Canvas slider replaces |
| F-035 | Addon preferences | DONE | `prefs.py` — default opacity, about |
| F-036 | FLIP Fluids team branding footer | DONE | `ui/branding.py` + logo |

## 5. Integration & polish

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| F-040 | Framing visible in camera view (all shading modes) | DONE | Background images + safe areas |
| F-041 | Persist settings in .blend file | DONE | Scene `opengate` PropertyGroup |
| F-042 | Restore user backgrounds on disable | DONE | Backup JSON |
| F-043 | Extension reload safe (dev workflow) | DONE | `load_post` handler |
| F-044 | Real-time checkbox / opacity (no lag) | DONE | No pixel iteration; incremental sync |

## 6. Out of scope (v1)

| ID | Feature | Status | Notes |
|----|---------|--------|-------|
| F-900 | Batch export all formats | DEFERRED | |
| F-901 | Video codec / bitrate presets | DEFERRED | |
| F-902 | Multi-camera format sets | DEFERRED | |
| F-903 | Runtime shader gate compositing | WONTFIX | Pre-combined PNGs instead |
| F-904 | Mesh plane viewport overlay | WONTFIX | DOF + Solid occlusion |

---

*Last updated: 2026-06-25*
