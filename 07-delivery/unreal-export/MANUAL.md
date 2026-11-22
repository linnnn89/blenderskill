---
name: unreal-export
description: Unreal Engine-specific Blender export for FBX scale, LODs, UCX collision, sockets, materials, and skeletal mesh workflows via MCP.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: Unreal, UE5, UE4, Unreal export, UCX, Unreal LOD, skeletal mesh, Unreal FBX, socket
  related-skills: export-pipeline, lod-pipeline, collision-proxy, asset-optimization, materials
---

# Unreal Export

UE-ready FBX. Correct centimeter scale awareness. UCX collision. LOD and socket naming.

## When to Use

- Static mesh or skeletal mesh to Unreal
- UCX collision export
- LOD chain import
- Socket / pivot setup for gameplay

## Pre-Flight

1. `asset-optimization` PASS
2. `lod-pipeline` for LOD0–N
3. `collision-proxy` for UCX meshes
4. Apply scale; pivots at intended UE origin

## Scale Note

Unreal is centimeter-based. Common approaches:
- Model in meters in Blender, export FBX with unit conversion / 0.01 awareness per project pipeline
- Or work to project-documented scale and verify with a 100cm reference

**Always measure a known edge after import.**

## FBX Defaults (Static)

```
Selected Objects
Apply Scalings: FBX All
Forward: -Z Forward
Up: Y Up
Mesh: ON
Smoothing: Face
```

## Naming for UE

| Type | Pattern |
|------|---------|
| Static mesh | `SM_Name` |
| Skeletal | `SK_Name` |
| Skeleton | `SKEL_Name` |
| LOD | `SM_Name_LOD0` … |
| Collision | `UCX_SM_Name_01` |
| Socket empty | `SOCKET_Name` |

## Collision

- Prefer convex UCX pieces over complex mesh colliders
- Multiple UCX meshes supported
- See `collision-proxy`

### Checked static FBX with UCX collision

Use `scripts/ucx_export.py` for one render mesh and its named convex hulls. In Object mode, each name must identify one visible mesh in the active view layer. If a linked library uses the same name, hide or exclude the other mesh for this export. Use local export objects, which can share linked mesh data. Blender appends the library name to directly linked objects in FBX and can break UCX matching. The render mesh must still have faces after its modifiers run. Substitute the installed handbook root, your object names and a new absolute output path.

```python
import runpy

ucx = runpy.run_path(r"${COMMANDCODE_SKILL_DIR}/07-delivery/unreal-export/scripts/ucx_export.py")
mesh = "SM_Crate"
hulls = ["UCX_SM_Crate_01", "UCX_SM_Crate_02"]
result = ucx["collision_report"](mesh, hulls)
print(result)
```

Once the report passes, use the same names in the export call. The exporter repeats the preflight on the current scene.

```python
import runpy

ucx = runpy.run_path(r"${COMMANDCODE_SKILL_DIR}/07-delivery/unreal-export/scripts/ucx_export.py")
result = ucx["export_collision_fbx"](
    "SM_Crate", ["UCX_SM_Crate_01", "UCX_SM_Crate_02"], r"/absolute/output/crate.fbx")
print(result)
```

Each evaluated collider must be one closed, outward-wound convex mesh named `UCX_<render mesh>` with an optional numeric suffix. The export uses the supplied meshes and their modifiers, preserves selection, and writes a static FBX with external texture references. On POSIX the destination filesystem must support hard links for atomic publication. In Unreal, import the file and inspect the custom hull count, size and clearance. [Epic's FBX collision conventions](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)

## Skeletal

- UE mannequin-oriented proportions when required
- Root bone; no leftover Blender deform leftovers
- Export morph targets if needed (shape keys)

## Verify in Unreal

- [ ] Scale (door ~200cm, character ~180cm)
- [ ] Collision wireframe
- [ ] LODs auto-detected
- [ ] Materials / texture sampling
- [ ] Sockets transform

## Constraints

### MUST DO
- Confirm scale with known-dimension test
- Prefix collision with `UCX_`
- Validate LODs and materials after import

### MUST NOT DO
- Export without collision plan for physics actors
- Mix unit systems undocumented

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Unreal Checklist | `references/unreal-checklist.md` | When needed |
| Ucx Naming | `references/ucx-naming.md` | When needed |
