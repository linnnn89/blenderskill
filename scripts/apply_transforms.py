"""Apply Location, Rotation & Scale on all GEO- objects before export.

Engines (Unity, Unreal, Godot, web) expect transforms baked into the
mesh. A model that is scale (2,2,2) in Blender will import at double
size or with broken normals if transforms are not applied first.

Usage (via mcp__blender__execute_blender_code):

    exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/apply_transforms.py").read())

Loading the file applies transforms to every GEO- object and prints a
summary. To target specific objects, call the function directly:

    apply_transforms(names=["GEO-sword_blade", "GEO-sword_grip"])
"""

import bpy


def apply_transforms(names=None, prefix="GEO-"):
    """Apply location, rotation and scale to objects.

    Args:
        names: Explicit list of object names. If None, targets all
               objects whose name starts with *prefix*.
        prefix: Fallback prefix filter when names is None.

    Returns:
        List of object names that were processed.
    """
    if names is not None:
        targets = [bpy.data.objects[n] for n in names if n in bpy.data.objects]
    else:
        targets = [obj for obj in bpy.data.objects if obj.name.startswith(prefix)]

    if not targets:
        print("apply-transforms: no matching objects found")
        return []

    # Deselect all first
    bpy.ops.object.select_all(action="DESELECT")

    processed = []
    for obj in targets:
        # Skip non-mesh objects (lights, cameras, empties)
        if obj.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
            continue

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)
        processed.append(obj.name)

    return processed


_processed = apply_transforms()
print(f"apply-transforms: applied to {len(_processed)} object(s): {_processed}")
