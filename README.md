# OpenGate

**Version 0.3.0** — Blender extension for social-media framing: render a square **Open Gate** master, preview aspect-ratio masks in the camera view, and export platform-ready crops for YouTube, Instagram, TikTok, Facebook, LinkedIn, and X.

## Requirements

- Blender **4.2+** (developed and tested on **5.1**)

## Installation

1. Download or clone this repository.
2. Install as a local extension (Blender **Edit → Preferences → Get Extensions → Install from Disk**)  
   **or** copy the `opengate` folder into your Blender extensions directory, for example:  
   `Blender/5.1/extensions/user_default/opengate`
3. Enable **OpenGate** in Preferences → Extensions.

## Quick start

1. Open the **OpenGate** sidebar panel in the 3D Viewport.
2. Assign a **Camera**.
3. Choose a **Platform** preset (or toggle framing masks manually).
4. For 9:16 platforms: optional **Show Safezones** (Instagram, YouTube, TikTok, Facebook Reels).
5. Set **Canvas** resolution for your square master render.
6. Press **NumPad 0** — the camera view shows the active mask as a background image.

## Platform presets

Choose a **Platform** preset in the OpenGate panel to apply the matching framing masks and see delivery recommendations — resolution, suggested frame rates, and maximum length — for that destination. Specs are verified periodically; always confirm current platform requirements before you publish.

## Project layout

```
opengate/
├── blender_manifest.toml
├── __init__.py
├── properties.py, prefs.py
├── core/
├── operators/, ui/
└── assets/
    ├── platform_presets.json
    ├── masks/          # aspect-ratio and safezone PNGs
    └── shader/         # image-collector blend
```

## License

GPL-3.0-or-later — see `blender_manifest.toml`.

## Developers

**Ryan Guy & Dennis Fassbaender**  
Contact: [support@flipfluids.com](mailto:support@flipfluids.com) · [flipfluids.com](https://flipfluids.com/)

Concept, mask assets, and architecture are original work by the FLIP Fluids team.

Platform delivery specs are maintained in `assets/platform_presets.json` — update that file to adjust recommendations without changing Python code.

<sub>Python source was authored with AI assistance.</sub>
