# OpenGate — Viewport Overlay Matrix

Decision matrix for framing-mask display in the 3D Viewport (Blender 5.1).

**Legend:** ✅ Works · ⚠️ Partial · ❌ Unacceptable · — N/A

---

## 1. Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| R-01 | Mask toggle in **real time** (no delay) | **Need** |
| R-02 | Mask visible in **camera view** | **Need** |
| R-03 | **DOF** must not blur the mask overlay | **Need** |
| R-04 | Mask must **not block** Solid view geometry | **Need** |
| R-05 | Crop feedback in **Solid** (at minimum) | **Need** |
| R-06 | Opacity slider | **Need** |
| R-07 | Camera view alignment | **Need** |

---

## 2. Approaches tested

| Approach | Real-time toggle | DOF-safe | Solid bars | Solid blocks scene | Verdict |
|----------|------------------|----------|------------|--------------------|---------|
| Mesh TEXTURED (all modes) | ✅ | ❌ blurred | ⚠️ | ❌ occludes | ❌ |
| Mesh BOUNDS | ✅ | ❌ | ❌ | ✅ | ❌ |
| GPU POST_VIEW / POST_PIXEL | ❌ slow | ✅ | ⚠️ | ✅ | ❌ |
| Mesh shader + Safe Areas | ✅ | ❌ | — lines only | ❌ occludes | ❌ |
| **Camera background image + Safe Areas** | ✅ | ✅ FRONT | — lines only | ✅ | ✅ **Current** |

---

## 3. Current architecture

```
Mask checkbox toggled
        │
        ├─► image_collector.py — ensure blend appended (once)
        │
        ├─► background_image.py — set camera BG image + alpha
        │
        └─► camera_display.py — safe area margins (Solid guides)

Camera view (NumPad 0)
        └─► Background image shows pre-combined PNG bars (all shading modes)

Solid / Wireframe
        └─► Safe Areas + Passepartout show crop rectangle
        └─► Scene geometry not occluded by mask plane
```

**Rules:**
- Pre-combined PNG per combo — no runtime pixel composite.
- Opacity changes only touch `CameraBackgroundImage.alpha`.
- Never iterate `image.pixels` in property update callbacks.

---

## 4. User-facing behaviour

| Viewport mode | PNG letterbox bars | Crop guides |
|---------------|-------------------|-------------|
| Material Preview | ✅ BG image | ✅ Safe Areas |
| Rendered (Eevee) | ✅ BG image | ✅ Safe Areas |
| Solid | ✅ BG image | ✅ Safe Areas + Passepartout |
| Wireframe | ✅ BG image | ✅ Safe Areas |

Background images require **camera view** (standard Blender behaviour).

---

## 5. Test checklist

- [ ] Toggle 16:9 / 9:16 / 5:4 — no perceptible delay
- [ ] Opacity slider — smooth, no stutter
- [ ] DOF enabled — mask stays sharp (foreground BG)
- [ ] Disable all masks — user camera backgrounds restored
- [ ] Safe areas track combined masks in Solid

---

*Last updated: 2026-06-22*
