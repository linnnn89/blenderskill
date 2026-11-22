"""Check evaluated UCX hulls and export one named static mesh with its colliders.

Adapted from the collision preflight in RobLe3/cc-blender-skill v1.4.0.
MIT License, Copyright (c) 2026 RobLe3

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
from pathlib import Path
import re
import tempfile

import bmesh
import bpy
import numpy as np


def _hull_error(evaluated):
    mesh = bmesh.new()
    try:
        mesh.from_mesh(evaluated.data)
        if not mesh.faces or not all(v.is_manifold for v in mesh.verts):
            return "Expected a closed manifold mesh"
        if any(not e.is_manifold or not e.is_contiguous for e in mesh.edges):
            return "Open surface or inconsistent winding"

        remaining = set(mesh.verts)
        pending = [remaining.pop()]
        while pending:
            vertex = pending.pop()
            for edge in vertex.link_edges:
                neighbor = edge.other_vert(vertex)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
        if remaining:
            return "Put each disconnected hull in its own collider object"

        # Center before applying world scale/shear so distant objects retain precision.
        linear = evaluated.matrix_world.to_3x3()
        mesh.verts.ensure_lookup_table()
        origin = mesh.verts[0].co.copy()
        for vertex in mesh.verts:
            vertex.co = linear @ (vertex.co - origin)
        mesh.normal_update()
        coords = np.array([v.co[:] for v in mesh.verts])
        if not np.isfinite(coords).all():
            return "Non-finite coordinates"
        tolerance = max(1e-9, np.linalg.norm(np.ptp(coords, axis=0)) * 1e-6)
        if mesh.calc_volume(signed=True) <= tolerance ** 3:
            return "Expected positive volume and outward winding"
        for face in mesh.faces:
            if face.calc_area() <= tolerance ** 2:
                return "Degenerate face"
            anchor = face.verts[0].co
            normal = face.normal
            if any(abs((v.co - anchor).dot(normal)) > tolerance for v in face.verts):
                return "Non-planar face"
            # Every vertex of a convex hull lies behind every outward face plane.
            if (coords @ normal[:]).max() - anchor.dot(normal) > tolerance:
                return "Non-convex surface"
        return None
    finally:
        mesh.free()


def _preflight(render_name, collider_names):
    if isinstance(collider_names, str):
        raise ValueError("Provide a list of collider names")
    names = list(collider_names)
    errors = []
    if not names or len(names) != len(set(names)):
        errors.append("Provide a nonempty list of distinct collider names")
    if render_name in names:
        errors.append("The render mesh cannot also be a collider")
    if render_name.startswith(("UCX_", "UBX_", "USP_", "UCP_")):
        errors.append("Render mesh name uses a collision prefix")
    if bpy.context.mode != "OBJECT":
        errors.append("Finish editing before checking evaluated geometry in Object mode")
    result = {"render_object": render_name, "colliders": names, "errors": errors, "passed": False}
    if errors:
        return result, []

    depsgraph = bpy.context.evaluated_depsgraph_get()
    # Linked libraries may have a mesh with the same name as a local mesh.
    candidates = {name: [] for name in [render_name, *names]}
    for obj in bpy.context.view_layer.objects:
        matches = candidates.get(obj.name)
        if matches is not None and obj.type == "MESH" and obj.visible_get():
            matches.append(obj)

    targets = []
    pattern = re.compile(r"UCX_" + re.escape(render_name) + r"(?:_[0-9]+)?")
    for name, matches in candidates.items():
        if not matches:
            errors.append(f"{name}: expected a visible mesh in the active view layer")
            continue
        if len(matches) > 1:
            errors.append(f"{name}: ambiguous name; isolate one visible mesh in the active view layer")
            continue
        obj = matches[0]
        if obj.library is not None:
            errors.append(f"{name}: directly linked object; FBX appends the library name. Use a local export object")
            continue
        targets.append(obj)
        evaluated = obj.evaluated_get(depsgraph)
        if obj.is_instancer or evaluated.is_instancer:
            errors.append(f"{name}: realize instances on an export copy first")
        elif name == render_name:
            if not evaluated.data.polygons:
                errors.append(f"{name}: evaluated render mesh has no faces")
        elif not pattern.fullmatch(name):
            errors.append(f"{name}: expected UCX_{render_name} with an optional numeric suffix")
        elif obj.data.shape_keys:
            errors.append(f"{name}: use a static collider mesh without shape keys")
        else:
            error = _hull_error(evaluated)
            if error:
                errors.append(f"{name}: {error}")
    result["passed"] = not errors
    return result, targets


def collision_report(render_name, collider_names):
    """Inspect named meshes in the active view layer and return a JSON-safe result."""
    report, _ = _preflight(render_name, collider_names)
    return report


def export_collision_fbx(render_name, collider_names, filepath):
    """Write a new binary FBX. User selection, active object and source meshes are preserved."""
    path = Path(filepath)
    if not path.is_absolute() or path.suffix.lower() != ".fbx" or not path.parent.is_dir():
        raise ValueError("Use an absolute .fbx path in an existing directory")
    if path.exists():
        raise FileExistsError(path)
    report, targets = _preflight(render_name, collider_names)
    if not report["passed"]:
        raise ValueError("\n".join(report["errors"]))
    # Stage in the destination directory so FBX relative texture references resolve there.
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".fbx", delete=False) as tmp:
        staged = Path(tmp.name)
    try:
        with bpy.context.temp_override(selected_objects=targets):
            status = bpy.ops.export_scene.fbx(
                filepath=str(staged), use_selection=True, object_types={"MESH"},
                bake_anim=False, use_mesh_modifiers=True, mesh_smooth_type="FACE",
                apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                axis_forward="-Z", axis_up="Y", path_mode="AUTO")
        with staged.open("rb") as fbx:
            if "FINISHED" not in status or fbx.read(23) != b"Kaydara FBX Binary  \x00\x1a\x00":
                raise RuntimeError("Blender did not write a binary FBX")
        # Both operations publish the complete file and fail if a concurrent writer won.
        if os.name == "nt":
            staged.rename(path)
        else:
            os.link(staged, path)
    finally:
        staged.unlink(missing_ok=True)
    return report
