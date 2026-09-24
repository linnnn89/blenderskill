---
name: blender-skill
description: Entry point and router for a 123-manual Blender 3D production handbook covering modeling, materials, UV and texturing, lighting, cameras, rendering, animation, rigging, simulation, VFX, scene assembly, export, art direction and reference-locked reconstruction. Use for ANY request that should be done in Blender — "make a 3D model of...", "render this...", "light it cinematically", "make this glass look frosted", "match this template or mascot exactly", "export as glTF or FBX for Unity or the web", "animate it" — even when the user never says Blender. This is a ROUTER that maps the request to the right handbook volume; the volume carries the detail.
when_to_use: Any 3D creation, modification, lighting, rendering, animation, simulation, or export task. Anything involving Blender, or that should reasonably be done in Blender. Also use when the user supplies reference images, wireframes, texture packs, or templates that a 3D model must match.
allowed-tools: Read Bash Glob Grep mcp__blender__execute_blender_code mcp__blender__get_scene_info mcp__blender__get_object_info mcp__blender__get_viewport_screenshot mcp__blender__search_polyhaven_assets mcp__blender__download_polyhaven_asset mcp__blender__search_sketchfab_models mcp__blender__download_sketchfab_model mcp__blender__search_polypizza_models mcp__blender__download_polypizza_model mcp__blender__generate_hyper3d_model_via_text mcp__blender__generate_hyper3d_model_via_image mcp__blender__generate_hunyuan3d_model
---

# Blender Handbook — Router

This is the **entry point only**. It contains the always-on rules plus a map of where the real guidance lives. The handbook holds **123 manuals in 10 groups**; load them one at a time, only when routed.

## How to navigate (3 levels — read only what you need)

```
${COMMANDCODE_SKILL_DIR}/SKILL.md                     ← level 0: this file (always read)
${COMMANDCODE_SKILL_DIR}/<group>/INDEX.md             ← level 1: one group's member list
${COMMANDCODE_SKILL_DIR}/<group>/<skill>/MANUAL.md    ← level 2: the actual manual
```

1. **Route from the table below** to the one or two groups that match the request.
2. **Read that group's `INDEX.md`** — it lists every member with a one-line "use when" and its manual path.
3. **Read only the `MANUAL.md` files you actually need**, then follow them.

Rules of navigation:

- **Path convention.** A backticked path is resolved **relative to the file that contains it** (standard markdown). So a manual's own `references/` files are resolved against that manual's folder, and a group's `INDEX.md` lists its members relative to itself.
- **Shared handbook files carry an explicit anchor.** Anything at handbook level is written with the `${COMMANDCODE_SKILL_DIR}/` prefix — e.g. `${COMMANDCODE_SKILL_DIR}/references/naming-conventions.md` or `${COMMANDCODE_SKILL_DIR}/scripts/reset_world.py`. A bare relative path never means the handbook-level folder.
- **Never read a whole group's manuals.** Read the `INDEX.md`, pick, then read the one or two that apply.
- A multi-part request legitimately chains several groups (e.g. model → materials → lighting → export). Walk the groups in production order.
- **Cross-group manual links are root-relative** — e.g. `03-surfacing/texture-workflow/MANUAL.md`.
- **To find a manual by bare name** (manuals cross-reference each other, e.g. "see `blender-materials` Recipe 6b"), glob for it instead of guessing the group:
  `Glob: ${COMMANDCODE_SKILL_DIR}/*/<name>/MANUAL.md`
- **Role and priority rules.** Where two manuals cover the same domain, use the canonical one by default and open the supplement only when the request needs that specific specialty. Do not load both just because both exist. Reference-locked work supersedes generic production workflow. Naming and production-order rules in this entry override conflicting examples inside a manual.

## Level-1 routing table

| Group | Open when the request is about… |
|-------|--------------------------------|
| `01-orchestration/` | Multi-step/multi-skill planning, deciding precedence when skills conflict, recovering after the user rejects a result, NIUA finisher MCP |
| `02-modeling/` | Creating or shaping geometry: meshes, hard-surface/mechanical, characters, creatures, environments, vehicles, vegetation, sculpting, retopology, procedural, 2D drawing → 3D |
| `03-surfacing/` | Materials and look-dev, UV unwrapping, texture atlases and decals, texture-driven fitting, hair and fur |
| `04-imaging/` | Lighting, cameras/framing/composition, choosing a render engine and settings, compositing |
| `05-motion/` | Animation and keyframes, rigging/armatures, physics and cloth simulation, VFX (smoke/fire/particles) |
| `06-scene/` | Assembling large scenes, linking/collections, set dressing and prop placement |
| `07-delivery/` | Export formats (glTF/FBX/OBJ/USD/STL), Unity/Unreal/Godot specifics, polycount & LOD optimization, collision meshes |
| `08-reference-locked/` | 1:1 fidelity to supplied templates, wireframes, texture packs, mascot/logo art — measuring the fit, resolving contradictory views, repairing misalignment |
| `09-quality-gates/` | Final ship/no-ship review of an asset or an animation |
| `10-art-direction/` | Choosing a *look*: styles (anime, pixel, low-poly…), horror sub-genres, moods, world settings, game genres, character archetypes |

**The MCP transport itself** (installing/wiring `ahujasid/mcp-for-blender`, safe mode, port 9876, troubleshooting the connection) lives in the separate `blender-mcp` skill — use it when the problem is the connection rather than the artwork.

## Always-on rules (apply before consulting any manual)

**Prerequisites.** Call `mcp__blender__get_scene_info` first. If it errors with "Could not connect to Blender": tell the user to start Blender and enable the BlenderMCP addon (port 9876 default), then stop. Then read the scene state: empty → build fresh; existing objects → operate on them and do NOT delete unless asked; a lone default cube → safe to delete. Optionally check runtime flags via `scripts/detect_blender_version.py`.

**Reset the world** at the start of every scene build (a leftover `Environment Texture` node with `image=None` causes magenta-flooded renders):

```python
exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/reset_world.py").read())
```

**Code execution** via `mcp__blender__execute_blender_code` — each call is a fresh namespace (re-import everything but `bpy`), identify objects by stable name not Python variables, print structured output, chunk work to ~5–20 lines (180 s timeout), and name everything with `GEO-`/`MAT-`/`LGT-`/`CAM-`/`ARM-`/`COL-` prefixes. Full rules: `references/code-execution-rules.md`. Engine naming exceptions and precedence: `references/naming-conventions.md`.

**Camera & rendering guard.** Before any test or final render, ensure a camera exists via `scripts/ensure_camera.py`:
```python
exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/ensure_camera.py").read())
```

**Validate visually, not just numerically.** After rendering, call `mcp__blender__get_viewport_screenshot` (or read the output file) and check that the subject is visible, recognisable, correctly proportioned and in frame. A render can pass every numeric check and still look wrong — never report success on numbers alone. Checklist and reporting template: `references/output-and-reporting.md`.

**Set viewport shading.** After assembly, switch viewport to material preview via `scripts/set_viewport_material_preview.py` so the user doesn't see default grey Solid shading.

**Pre-export hygiene.** Before delivering glTF/FBX/OBJ, bake object transforms and purge orphan data blocks:
```python
exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/apply_transforms.py").read())
exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/cleanup_unused.py").read())
```

**Look up real dimensions before modelling** from natural language — `references/common-object-dimensions.md`. Don't guess a sword's or a chair's proportions.

**Sequence work in production order** — reference/plan → block-out → camera lock → light v1 → refine geometry → materials v1 → light v2 → detail → final render → composite → export. Camera framing comes before lighting; lighting is tuned for the final camera read. Rationale and time budgets: `references/assembly-order.md`.

Do not fake things Blender cannot do from primitives: a "human character" request needs a real base mesh or an asset library, not a sphere with features. See `references/failure-modes.md` and `references/mcp-integration.md`.

## Orchestrator references (this level only)

- `references/intent-routing.md` — intent → group routing, reference-locked routing, edge cases, precedence
- `references/code-execution-rules.md` — exec rules, standard skeleton, naming, validation, Blender 5.x API pitfalls
- `references/mcp-integration.md` — MCP tools, Poly Haven / Sketchfab / Poly Pizza assets, AI generators, connection limits
- `references/failure-modes.md` — symptom → action table
- `references/output-and-reporting.md` — visual validation checklist, reporting template
- `references/assembly-order.md` — canonical sequence, time budgets, recovery patterns
- `references/common-object-dimensions.md` — real-world dimensions by subject
- `references/blender-version-compat.md` — Blender 4.x vs 5.x matrix and smoke test
- `scripts/reset_world.py` — neutral world baseline
- `scripts/set_viewport_material_preview.py` — make materials visible in the viewport
- `scripts/ensure_camera.py` — guarantee active scene camera exists before rendering
- `scripts/cleanup_unused.py` — remove orphan data blocks before export
- `scripts/apply_transforms.py` — bake loc/rot/scale into mesh data before export
- `scripts/detect_blender_version.py` — detect runtime Blender version and capability flags

## What this handbook is NOT for

- Heavy custom GPU work / writing a render engine (use Blender's existing engines)
- Real-time game logic (use Unity / Unreal directly)
- Sculpting strokes from natural language (sculpting is gestural; use brushes interactively)
- CAD precision modeling (use FreeCAD) or engineering CFD (Mantaflow is VFX-quality only)

When the user asks for these, redirect them politely and explain.
