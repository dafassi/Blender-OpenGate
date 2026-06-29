# OpenGate

**Version 0.3.0** — Blender extension for social-media framing: render a square **Open Gate** master, preview aspect-ratio masks in the camera view, and export platform-ready crops for YouTube, Instagram, TikTok, Facebook, LinkedIn, and X.

## Screenshots

**16:9 landscape framing**

![OpenGate 16:9 viewport framing](docs/screenshots/opengate-16_9.jpg)

**9:16 portrait framing (with safe zones)**

![OpenGate 9:16 viewport framing](docs/screenshots/opengate-9_16.jpg)

## Requirements

- Blender **5.1+** — developed and tested on 5.1; older versions have not been tested.

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

Choose a **Platform** preset in the OpenGate panel to apply the matching framing masks and see delivery recommendations — resolution, suggested frame rates, and maximum length — for that destination.

The specs live in `assets/platform_presets.json`. We review platform changes regularly and update the repository accordingly; you can edit that file locally if you need different values in the meantime. Always confirm current platform requirements before you publish.

## Project layout

```
opengate/
├── blender_manifest.toml
├── __init__.py
├── properties.py, prefs.py
├── core/
├── operators/, ui/
├── docs/screenshots/   # README images
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

<sub>Python source was authored with AI assistance.</sub>
