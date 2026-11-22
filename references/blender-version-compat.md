# Blender Version Compatibility Matrix

The original recipe pack was validated on Blender 5.1.1 on macOS. This handbook has focused Windows regressions on Blender 5.2.2 LTS for the version probe, camera orbit, per-slot curve edits, EEVEE render, Decimate, scoped GLB and static UCX FBX export.

## Compat-critical patches in this plugin

| Patch | Blender 4.x behaviour | Blender 5.x behaviour | Strategy |
|-------|----------------------|----------------------|----------|
| EEVEE engine name (`blender-rendering` Recipe 3) | `BLENDER_EEVEE` (4.0–4.1) or `BLENDER_EEVEE_NEXT` (4.2–4.5) | `BLENDER_EEVEE` | Read the built-in engine identifier from RenderSettings RNA |
| Action F-curves (`blender-animation` Recipe 3) | Legacy Actions and, from 4.4, slotted Actions | Layered Actions | `action_fcurves(owner)` resolves the assigned slot for layered Actions and uses `action.fcurves` for legacy data |
| `Mesh.use_auto_smooth` | Varies by minor version | Absent | Check `bpy.types.Mesh.bl_rna.properties` for availability |
| `Subsurface IOR` and `Weight` BSDF inputs (`blender-materials` Recipe 9) | Reachable by string-key lookup | `enabled=False` flag blocks string-key lookup | `set_input(node, name, value)` helper iterates inputs to find by name |
| Coloured-glass volume density (`blender-materials` Recipe 6b) | Same physics — recipe values are version-agnostic | Same | No special handling needed |

## What's NOT cross-tested

- **Blender 3.x and earlier**: Not supported. Many recipes use Principled BSDF v2 inputs (Coat Weight, Sheen Weight, Subsurface Weight) that don't exist on the older Principled BSDF.
- **Blender 4.x**: Current Windows regression coverage is on 5.2.2. The older runtime paths still need a 4.x installation for an end-to-end check.

## Validation status

| Blender version | Status | Notes |
|----------------|--------|-------|
| 5.2.2 LTS | Local background Blender tests | See the scoped workflows above and the tests in the handbook |
| 5.1.1 | Historical upstream validation | Sword, bottle, chair and aviator scenes tested by the upstream project |
| 4.x | Compatibility paths only | Runtime verification pending |
| 3.x and earlier | ❌ Not supported | Principled BSDF v1 missing required inputs |

## How to confirm cross-version compat in your install

Run the installed probe through the chosen Python execution tool. Substitute the absolute handbook path.

```python
import runpy
result = runpy.run_path(r"${COMMANDCODE_SKILL_DIR}/scripts/detect_blender_version.py")["result"]
```

The probe prints the same fields it returns. On the tested 5.2.2 build, `eevee_engine` is `BLENDER_EEVEE`, `layered_actions` is true and `has_mesh_auto_smooth` is false. Read `version_string` for the running version.

If you find recipes that fail on your version, please file an issue at https://github.com/RobLe3/cc-blender-skill/issues with:
- `bpy.app.version_string`
- The specific recipe / SKILL.md section
- The error message
