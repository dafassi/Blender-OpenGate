# OpenGate

Blender extension for social-media framing — square Open Gate master, crop in post.

**Docs:** `development/AGENT_CONTEXT.md` · `development/IMAGE_COLLECTOR.md`

## Development & attribution

OpenGate's concept, mask assets, architecture, and test design are original work
by the FLIP Fluids team, crafted by hand. The Python source code was authored
with assistance from artificial intelligence tools.

## Layout

```
opengate/
├── blender_manifest.toml
├── __init__.py
├── properties.py, prefs.py
├── core/            # masks, image_collector, background_image, …
├── operators/, ui/
├── assets/
│   ├── platform_presets.json          # ← edit here to update platform specs
│   ├── .opengate-logo_rev0.png
│   ├── shader/opengate-imagecollector.blend
│   └── masks/MASK_COMBO_MATRIX.md   # PNG names: `.opengate-…`
└── development/
```

## Quick start

1. Enable extension in Blender 5.1+
2. OpenGate panel → assign **Camera**
3. Choose a **Platform** preset (or toggle framing masks manually)
4. For 9:16 platforms: optional **Show Safezones** (IG / YT / TT / FB Reels)
5. **NumPad 0** — camera view shows mask as background image
