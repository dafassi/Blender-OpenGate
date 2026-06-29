# OpenGate — Shader network (authoring reference)

> **Runtime:** OpenGate no longer drives this shader for viewport display.  
> Masks are shown via **camera background images** from pre-combined PNGs in  
> `opengate-imagecollector.blend`. See **`IMAGE_COLLECTOR.md`** for the current path.

This document remains as a reference for the **authoring setup** inside the collector blend (material `opengate-mask` keeps image datablocks alive).

---

## Principle: two stages (legacy compositing model)

| Stage | Purpose | Mix blend mode | Count (3 masks) |
|-------|---------|----------------|-----------------|
| **Gate** | Turn each mask on/off (0 or 1) | **Mix** (linear) | 3 |
| **Combine** | Stack active masks together | **Maximum** | 2 |

Gate per mask + Maximum combine scales to any number of masks (N gates + N−1 combines).

---

## Node naming (in blend)

| Node | Name | Notes |
|------|------|-------|
| Image Texture 16:9 | `opengate-tex-16_9` | `.opengate-16_9.png` |
| Image Texture 9:16 | `opengate-tex-9_16` | `.opengate-9_16.png` |
| Image Texture 5:4 | `opengate-tex-5_4` | `.opengate-5_4.png` |
| Gate mix bit 1 | `opengate-mask-1` | Factor ← bit 1 (16:9) |
| Gate mix bit 2 | `opengate-mask-2` | Factor ← bit 2 (9:16) |
| Gate mix bit 4 | `opengate-mask-4` | Factor ← bit 4 (5:4) |
| Stack mix #1 | `opengate-stack-1` | MAX of gate 1 & 2 |
| Stack mix #2 | `opengate-stack-2` | MAX of stack-1 & gate 4 |

Gate node names use the **bit value** (1, 2, 4, 8, …) — same as `masks.py`.

---

## Runtime combo PNGs (what Python actually uses)

Instead of live gate factors, export **one PNG per bitmask** and name datablocks per `MASK_COMBO_MATRIX.md`:

| Flags | Image datablock |
|------:|-----------------|
| 1 | `.opengate-16_9.png` |
| 2 | `.opengate-9_16.png` |
| 3 | `.opengate-16_9-9_16.png` |
| 4 | `.opengate-5_4.png` |
| 5 | `.opengate-16_9-5_4.png` |
| 6 | `.opengate-9_16-5_4.png` |
| 7 | `.opengate-16_9-9_16-5_4.png` |

---

*Last updated: 2026-06-29 — superseded for runtime by IMAGE_COLLECTOR.md*
