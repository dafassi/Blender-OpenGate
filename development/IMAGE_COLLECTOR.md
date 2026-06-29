# OpenGate — Image collector & camera background

How mask images reach the viewport (current architecture, Blender 5.1).

---

## Assets

| File | Purpose |
|------|---------|
| `assets/shader/opengate-imagecollector.blend` | All combo PNGs as image datablocks |
| Object `opengate-imagecollector` | Hidden in scene; material keeps images referenced |
| Material `opengate-mask` | On collector mesh; references individual mask textures |

**Do not** rebuild this in Python. Artists edit the `.blend`; Python appends it.

---

## Append flow (`core/image_collector.py`)

```
First mask activation (or load_post)
        │
        ▼
bpy.data.libraries.load(opengate-imagecollector.blend)
        ├─ append all .opengate-*.png  image datablocks
        └─ append opengate-imagecollector  object
        │
        ▼
Link object to scene (hidden, hide_render)
        │
        ▼
Tag images: opengate_mask_file, opengate_mask_flags
```

Images are looked up **by datablock name** (e.g. `.opengate-16_9.png`), not by file path on disk.

---

## Display flow (`core/background_image.py`)

```
Checkbox / show overlay changed
        │
        ▼
mask_flags rebuilt (bitmask)
        │
        ▼
resolve combo image name  (mask_combos.py + mask_combo_matrix.py)
        │
        ▼
get image from bpy.data.images[name]
        │
        ▼
Camera Background Image slot
        ├─ display_depth = FRONT
        ├─ frame_method = FIT
        ├─ alpha = mask_opacity
        └─ show_on_foreground = True
```

On disable: backup JSON restores user's original background images.

---

## Combo images (flags 1–7)

One pre-combined PNG per active mask **set**. See `assets/masks/MASK_COMBO_MATRIX.md`.

Checkbox order does not matter (16:9 + 5:4 = 5:4 + 16:9).  
Filename id order is flexible (`.opengate-16_9-5_4.png` = `.opengate-5_4-16_9.png`).

### Platform safezone variants

When **Show Safezones** is on with a supported platform preset and **9:16 only**, a separate PNG is used (still bitmask flags `2`). See the safezone table in `assets/masks/MASK_COMBO_MATRIX.md`.

---

## Performance

| Action | What runs |
|--------|-----------|
| Opacity slider | `entry.alpha = value` only |
| Same combo re-selected | early return |
| Combo change | swap `entry.image`, no full scene scan |
| First enable | append blend once, backup user BGs |

**Never** iterate `image.pixels` in update callbacks.

---

## Updating artwork

1. Open `opengate-imagecollector.blend` in Blender.
2. Replace / edit image datablocks (keep names from `MASK_COMBO_MATRIX.md` — leading `.` required).
3. Optional: **File → External Data → Pack Resources** for self-contained blend.
4. Save blend into `assets/shader/`.
5. Reload OpenGate extension in test scenes.

---

## Legacy note

Earlier versions used a **mesh plane + live shader compositing** (`opengate-shader.blend`, gate factors driven by Python). That path was removed — see `VIEWPORT_OVERLAY_MATRIX.md` for rejected approaches.

The collector material may still contain a gate/stack node setup for authoring; **runtime only uses the image datablocks + camera background slot**.

---

*Last updated: 2026-06-29*
