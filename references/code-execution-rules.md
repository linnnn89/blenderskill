# Code-Execution Rules for `mcp__blender__execute_blender_code`

Everything you emit runs in a fresh, isolated namespace inside Blender. These rules are non-negotiable — most "it worked in one call but failed in the next" bugs come from violating rule 1 or 2.

---

## The five hard rules

1. **Each call is a fresh namespace.** Only `bpy` is pre-imported. Re-import `math`, `bmesh`, `numpy`, `os`, etc. in *every* call that needs them.
2. **Identify objects by stable name, never by Python variable.** `bpy.data.objects['GEO-sword']` survives across calls; a `sword = ...` assignment does not.
3. **Print structured output** so you can parse the result back. End each chunk with `print(f"...")` reporting what changed — object names, vertex counts, file paths.
4. **Chunk the work.** 180-second timeout per call. Do not dump 500 lines in one call — split into ~5–20-line chunks.
5. **Use Blender Studio naming conventions** for everything you create (`GEO-`, `MAT-`, `LGT-`, `CAM-`, `ARM-`, `COL-`). Never leave anything named `Cube.027`.

---

## Standard skeleton for every operation

```python
import bpy
# (re-import other modules here as needed)

# 1. Scope: identify or create objects by NAME
obj = bpy.data.objects.get('GEO-target') or bpy.data.objects.new('GEO-target', None)

# 2. Do the work
# ...

# 3. Report
print(f"done:GEO-target {len(obj.data.vertices) if obj.data else 0}")
```

---

## Naming conventions (apply to everything you create)

| Prefix | Meaning |
|--------|---------|
| `GEO-` | Geometry / mesh objects |
| `MAT-` | Materials |
| `LGT-` | Lights |
| `CAM-` | Cameras |
| `ARM-` | Armatures (rigs) |
| `COL-` | Collections |
| `WGT-` | Custom bone shapes / widgets |

Suffix `.L` / `.R` for left/right. Examples: `GEO-sword_blade`, `MAT-steel_brushed`, `LGT-key`.

---

## Validation rule of thumb

After significant work, call `mcp__blender__get_scene_info` and verify:

- Expected objects exist with correct names.
- Object counts make sense (no runaway duplication).
- Polycount roughly matches target.

Before reporting success on a render or export, confirm the file actually exists (`Bash`: `ls -la /path/to/output`). Numerical validation alone is not enough — see the visual checkpoint in `SKILL.md` and `${COMMANDCODE_SKILL_DIR}/references/output-and-reporting.md`.

---

## Common API gotchas (preventing silent bugs & crashes)

1. **Operator context & active object**: `bpy.ops` operators rely on `context.active_object` and selection state. Before calling operators on an object, explicitly make it active and selected:
   ```python
   bpy.context.view_layer.objects.active = obj
   obj.select_set(True)
   ```
2. **Context override (`temp_override`)**: In headless / MCP executions without an open 3D view, area-dependent operators may fail (`RuntimeError: Operator bpy.ops.xxx.poll() failed`). Use `temp_override` when context is missing:
   ```python
   # e.g., overriding window / area / region if executing viewport-dependent operators
   ```
3. **Edit Mode vs Object Mode data synchronization**: Reading or writing `mesh.vertices` while in `EDIT` mode yields stale or incorrect data. Switch back to `OBJECT` mode before inspecting attributes, or use `bmesh.from_edit_mesh(me)`:
   ```python
   bpy.ops.object.mode_set(mode='OBJECT')
   ```
4. **Dependency Graph updates**: Modifiers (Bevel, Subsurf, Boolean) do not alter `obj.data.vertices` directly. To inspect deformed or generated geometry:
   ```python
   depsgraph = bpy.context.evaluated_depsgraph_get()
   eval_obj = obj.evaluated_get(depsgraph)
   eval_mesh = eval_obj.to_mesh()
   # remember to call eval_obj.to_mesh_clear() when done
   ```
5. **Collection linking**: Always create or fetch a target collection explicitly instead of relying on default scene links:
   ```python
   col = bpy.data.collections.get('COL-props') or bpy.data.collections.new('COL-props')
   if col.name not in bpy.context.scene.collection.children:
       bpy.context.scene.collection.children.link(col)
   col.objects.link(obj)
   ```
6. **Mutating collections during iteration**: Modifying `bpy.data.objects` or collections while iterating directly over them leads to crashes or skipped items. Always copy to a list:
   ```python
   for o in list(bpy.data.objects):
       if o.name.startswith("Cube"):
           bpy.data.objects.remove(o, do_unlink=True)
   ```

---

## Known version pitfalls

Blender 5.x changed several APIs that appear in older recipes. Consult `${COMMANDCODE_SKILL_DIR}/references/blender-version-compat.md` for the compat matrix and the smoke test. Quick list:

| Symptom | Cause | Where the fix lives |
|---------|-------|--------------------|
| `BLENDER_EEVEE_NEXT` rejected | 5.x renamed the engine back to `BLENDER_EEVEE` | `blender-rendering` Recipe 3 (try/except fallback) |
| `'Action' object has no attribute 'fcurves'` | 5.x layered Actions | `blender-animation` Recipe 3 (`get_fcurves_compat()`) |
| `KeyError: 'Subsurface IOR'` / `'Weight'` | 5.x marks some BSDF inputs `enabled=False`, blocking string-key lookup | `blender-materials` Recipe 9 (`set_input` helper — iterate inputs, match by name) |
| `Mesh.use_auto_smooth` missing | Removed in 5.x | Wrap in `hasattr(mesh, 'use_auto_smooth')`, or just use `bpy.ops.object.shade_smooth()` |
| `Error: Cannot render, no camera` | `scene.camera is None` | Run the `ensure_camera()` guard before any render — `blender-rendering` Recipes 5 / 6 |
