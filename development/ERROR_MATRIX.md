# OpenGate — Error Matrix

Known issues, root causes, and fixes. Add a row for every bug encountered during development.

**Legend:** `OPEN` · `INVESTIGATING` · `FIXED` · `WONTFIX`

---

## Active issues

| ID | Summary | Severity | Status | First seen | Notes |
|----|---------|----------|--------|------------|-------|
| — | *No active issues* | — | — | — | — |

---

## Resolved issues

| ID | Summary | Severity | Status | Fixed in | Root cause | Fix |
|----|---------|----------|--------|----------|------------|-----|
| E-001 | Extension won't enable — `platform` EnumProperty | high | FIXED | 2026-06-18 | Dynamic enum with string default | Static enum items; int default |
| E-002 | Mask plane spawns on scene floor | high | FIXED | 2026-06-18 | Parent + matrix order | **Removed** mesh plane approach |
| E-003 | Mask shader black on plane | med | FIXED | 2026-06-18 | Missing UVs | **Removed** mesh plane approach |
| E-004 | GPU overlay slow / broken | high | FIXED | 2026-06-22 | POST_PIXEL composite | Rejected GPU path |
| E-005 | DOF blurs mask overlay | high | FIXED | 2026-06-22 | Mesh in 3D scene | Camera background FRONT |
| E-006 | Relative vs absolute image paths | med | FIXED | 2026-06-22 | Path flipping broke reload | Collector blend + datablock names |
| E-007 | Mask checkbox active but not shown | high | FIXED | 2026-06-22 | `has_data` false in Blender 5 | Use `image.size` / pixels check |
| E-008 | UI lag on opacity / checkboxes | high | FIXED | 2026-06-22 | `len(image.pixels)` every sync | Fast alpha path; incremental sync |
| E-009 | Full BG rebuild every toggle | med | FIXED | 2026-06-22 | Always `background_images.clear()` | Update entry in place |

---

## Error template (copy for new entries)

```markdown
| E-XXX | Short description | low/med/high | OPEN | YYYY-MM-DD | Reproduction steps, suspected cause |
```

### Severity guide

- **high** — crash, data loss, extension won't load, mask unusable
- **med** — feature broken, workaround exists
- **low** — cosmetic, edge case, dev-only annoyance

---

*Last updated: 2026-06-22*
