---
name: blender-skill
description: Entry point and router for a 123-manual Blender 3D production handbook covering modeling, surfacing, lighting, animation, physics, scene assembly, export, and art direction.
when_to_use: Any 3D creation, modification, lighting, rendering, animation, simulation, or export task in Blender, or matching reference images/blueprints.
---

# Blender Handbook — Router

Entry router for the 3D production handbook (**123 manuals across 10 groups**). Load only what is needed.

## Navigation: 3 Levels

```text
${COMMANDCODE_SKILL_DIR}/SKILL.md                     ← Level 0: Global entry router (this file)
${COMMANDCODE_SKILL_DIR}/<group>/INDEX.md             ← Level 1: Domain member index and trigger rules
${COMMANDCODE_SKILL_DIR}/<group>/<skill>/MANUAL.md    ← Level 2: Task-specific production manual
```

1. **Route**: Match user intent to 1–2 domain groups from the **Level-1 Routing Table** below.
2. **Index**: Read that group's `<group>/INDEX.md` to pick the concrete manual.
3. **Execute**: Read and strictly follow only the relevant `MANUAL.md` files in production order.

## Level-1 Routing Table

| Group | Open when the request is about… |
|-------|--------------------------------|
| `01-orchestration/` | Multi-step/multi-skill planning, precedence rules, user recovery, finisher MCP |
| `02-modeling/` | Mesh creation, hard-surface/mechanical, character, creature, environment, procedural, sculpting |
| `03-surfacing/` | Materials, look-dev, UV unwrapping, texture atlases, decals, hair and fur |
| `04-imaging/` | Lighting schemes, camera composition, Cycles/EEVEE render engines, compositing |
| `05-motion/` | Keyframe animation, rigging/armatures, physics & cloth simulation, VFX particles |
| `06-scene/` | Large scene assembly, collection hierarchies, set dressing and prop placement |
| `07-delivery/` | Multi-engine export (glTF/FBX/USD/OBJ/STL), LODs, polycount optimization, collision meshes |
| `08-reference-locked/` | 1:1 Reference/blueprint/wireframe matching, dimension verification, misalignment repair |
| `09-quality-gates/` | Final ship/no-ship validation checklists for assets and animations |
| `10-art-direction/` | Visual styles (anime, stylized, voxel, retro, sci-fi, horror, pixel) |

*For MCP connection troubleshooting (port 9876, safe mode), refer to the separate `blender-mcp` skill.*

## Always-On Rules (Critical Baseline)

1. **Scene Preflight**:
   - Check connection via `get_scene_info`. If disconnected, instruct user to start Blender & enable the BlenderMCP addon (port 9876).
   - If the scene is empty, build fresh. If existing objects exist, preserve them unless asked. A lone default cube is safe to remove.
2. **Environment Reset**:
   - Always run `scripts/reset_world.py` before building to prevent missing texture nodes flooding the render magenta:
     `exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/reset_world.py").read())`
3. **Code Execution Standards**:
   - Each MCP call runs in a fresh namespace. Re-import necessary modules (except `bpy`).
   - Prefix names systematically (`GEO-`, `MAT-`, `LGT-`, `CAM-`, `ARM-`, `COL-`). Chunk work into ~5–20 lines. Detailed rules: `references/code-execution-rules.md`.
4. **Camera & Visual Validation Guard**:
   - Always ensure an active camera exists before rendering: `scripts/ensure_camera.py`.
   - Never rely on numeric metrics alone. Inspect viewport via `get_viewport_screenshot` to confirm visibility, framing, and proportions (`references/output-and-reporting.md`).
5. **Real Dimensions**:
   - Never guess real-world scales; verify bounds against `references/common-object-dimensions.md`.
6. **Pre-Export Hygiene**:
   - Before exporting (glTF/FBX), bake object transforms with `scripts/apply_transforms.py` and purge orphan blocks with `scripts/cleanup_unused.py`.
7. **Production Sequence**:
   - Reference/Plan → Block-out → Camera lock → Light v1 → Refine geometry → Materials v1 → Light v2 → Final render → Composite → Export (`references/assembly-order.md`).

## Core Orchestrator References

- **Intent & Recovery**: `references/intent-routing.md`, `references/failure-modes.md`
- **Execution & Tools**: `references/code-execution-rules.md`, `references/mcp-integration.md`
- **Quality & Checklist**: `references/output-and-reporting.md`, `references/validation-checklist.md`
- **Workflow & Scales**: `references/assembly-order.md`, `references/common-object-dimensions.md`
- **Automation Scripts**: `scripts/reset_world.py`, `scripts/ensure_camera.py`, `scripts/apply_transforms.py`, `scripts/cleanup_unused.py`, `scripts/detect_blender_version.py`

## Scope Boundary (What This Is NOT For)

- Custom GPU render engine development (use Cycles / EEVEE).
- Real-time gameplay logic (use Unity / Unreal / Godot directly).
- Manual brush sculpting strokes from natural language (interactive sculpting requires manual input).
- CAD precision engineering CFD (Mantaflow is visual VFX only).
