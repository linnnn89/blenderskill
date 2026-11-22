"""Run one scenario inside the factory-startup Blender process from test_handbook."""
import math
from pathlib import Path
import re
import runpy
import sys

import bpy


def recipe(root, manual, heading):
    path = root / manual / "MANUAL.md"
    section = path.read_text(encoding="utf-8").split("### " + heading, 1)[1].split("\n### ", 1)[0]
    block = re.search(r"^```python\n(.*?)\n```", section, re.M | re.S)
    exec(compile(block[1].replace("${COMMANDCODE_SKILL_DIR}", root.as_posix()), str(path), "exec"), {})


def recipes(root, temp):
    scene = bpy.context.scene
    camera = scene.camera
    original_engine = scene.render.engine
    materials = set(bpy.data.materials.keys())
    probe = runpy.run_path(str(root / "scripts/detect_blender_version.py"))
    info = probe["result"]
    assert info["layered_actions"] == ("layers" in bpy.types.Action.bl_rna.properties)
    assert info["has_mesh_auto_smooth"] == ("use_auto_smooth" in bpy.types.Mesh.bl_rna.properties)
    assert scene.render.engine == original_engine and set(bpy.data.materials.keys()) == materials

    recipe(root, "04-imaging/blender-cameras", "Recipe 5 ")
    pivot = scene.camera.parent
    scene.frame_set(60, subframe=0.75)
    assert math.isclose(pivot.rotation_euler.z, math.pi / 2, abs_tol=1e-5)
    scene.camera = camera
    scene.frame_set(1)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3)
    target = bpy.context.object
    target.name = "GEO-target"
    for frame, location in [(1, 0), (11, 10)]:
        target.location.z = location
        target.keyframe_insert(data_path="location", index=2, frame=frame)
    action = target.animation_data.action
    other = bpy.data.objects["Cube"]
    if hasattr(action, "slots"):
        # Two objects share an Action, but use different slots and interpolation.
        other.animation_data_create().action = action
        other.animation_data.action_slot = action.slots.new("OBJECT", "other")
        for frame, location in [(1, 0), (11, 10)]:
            other.location.z = location
            other.keyframe_insert(data_path="location", index=2, frame=frame)
    scene.frame_set(3)
    other_before = other.location.z
    recipe(root, "05-motion/blender-animation", "Recipe 3 ")
    scene.frame_set(1)
    scene.frame_set(3)
    assert math.isclose(target.location.z, 2, abs_tol=1e-5)
    assert math.isclose(other.location.z, other_before, abs_tol=1e-5)

    faces = len(target.data.polygons)
    recipe(root, "07-delivery/blender-export", "Recipe 2 ")
    assert 0 < len(target.data.polygons) < faces
    scene.frame_set(1)
    recipe(root, "04-imaging/blender-rendering", "Recipe 3 ")
    assert scene.render.engine == info["eevee_engine"]
    assert scene.eevee.taa_render_samples == 64
    if hasattr(scene.eevee, "fast_gi_method"):
        assert scene.eevee.use_raytracing and getattr(scene.eevee, "use_fast_gi", True)
        assert scene.eevee.fast_gi_method == "AMBIENT_OCCLUSION_ONLY"
        assert scene.eevee.ray_tracing_options.trace_max_roughness < 1
    # Render the configured engine at a small fixture resolution.
    scene.render.resolution_x = scene.render.resolution_y = 64
    scene.render.resolution_percentage = 100
    scene.eevee.taa_render_samples = 2
    image = temp / "eevee.png"
    scene.render.filepath = str(image)
    bpy.ops.render.render(write_still=True)
    pixels = bpy.data.images.load(str(image))
    assert tuple(pixels.size) == (64, 64)
    red = pixels.pixels[:][::4]
    assert max(red) - min(red) > 0.05
    print("RECIPES_OK", bpy.app.version_string)


def collision(root, temp):
    api = runpy.run_path(str(root / "07-delivery/unreal-export/scripts/ucx_export.py"))
    export = api["export_collision_fbx"]
    report = api["collision_report"]
    unrelated = bpy.context.object
    render_name = "SM_Prop"
    render = bpy.data.objects.new(render_name, unrelated.data.copy())
    bpy.context.collection.objects.link(render)
    names = ["UCX_SM_Prop_01", "UCX_SM_Prop_02"]
    for index, name in enumerate(names):
        hull = bpy.data.objects.new(name, unrelated.data.copy())
        hull.location.x = 4 * index
        bpy.context.collection.objects.link(hull)
    hull = bpy.data.objects[names[0]]
    box = hull.modifiers.new("Disconnected pieces", "ARRAY")
    box.relative_offset_displace = (2, 0, 0)
    path = temp / "static.fbx"

    def check_rejected(candidates, reason):
        rejected = report(render.name, candidates)
        assert not rejected["passed"] and any(reason in message for message in rejected["errors"]), rejected
        try:
            export(render.name, candidates, path)
        except ValueError:
            pass
        else:
            raise AssertionError("Export accepted invalid colliders")
        assert not path.exists()

    check_rejected(names, "disconnected")
    assert len(hull.data.vertices) == 8
    hull.modifiers.remove(box)
    check_rejected([unrelated.name], "expected UCX_")
    check_rejected([names[0], names[0]], "distinct")
    assert bpy.context.selected_objects == [unrelated]

    group = render.vertex_groups.new(name="Empty mask")
    mask = render.modifiers.new("Remove all faces", "MASK")
    mask.vertex_group = group.name
    check_rejected(names, "no faces")
    assert len(render.data.polygons) == 6
    render.modifiers.remove(mask)

    # A local and a linked object can have the same Blender name and different geometry/poses.
    render.location.y = 3
    library = temp / "same-names.blend"
    bpy.data.libraries.write(str(library), {render, hull})
    render.location.y = 0
    with bpy.data.libraries.load(str(library), link=True) as (_, linked):
        linked.objects = [render.name, hull.name]
    linked_render, linked_hull = linked.objects
    for obj in (linked_render, linked_hull):
        bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()
    check_rejected(names, f"{render_name}: ambiguous")
    render.hide_set(True)
    check_rejected(names, f"{hull.name}: ambiguous")
    linked_hull.hide_set(True)
    check_rejected(names, f"{render_name}: directly linked")
    linked_render.hide_set(True)
    render.hide_set(False)
    # FBX preserves the local object's name even when its mesh data is linked.
    render.data = linked_render.data
    assert render.library is None and render.data.library is not None

    hull.modifiers.new("Triangles", "TRIANGULATE")
    corner = hull.data.vertices[0]
    original = corner.co.copy()
    corner.co = -0.25 * original
    hull.data.update()
    check_rejected(names, "Non-convex")
    corner.co = original
    hull.data.update()
    result = export(render.name, names, path)
    assert result["passed"] and path.stat().st_size > 0
    assert bpy.context.selected_objects == [unrelated]
    assert bpy.context.view_layer.objects.active == unrelated
    assert len(hull.data.polygons) == 6 and len(hull.modifiers) == 1
    contents = path.read_bytes()
    try:
        export(render.name, names, path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Export overwrote an existing FBX")
    assert path.read_bytes() == contents

    bpy.ops.wm.read_factory_settings(use_empty=True)
    assert "FINISHED" in bpy.ops.import_scene.fbx(filepath=str(path))
    assert set(bpy.context.scene.objects.keys()) == {render_name, *names}
    assert math.isclose(bpy.data.objects[render_name].matrix_world.translation.y, 0, abs_tol=1e-4)
    assert len(bpy.data.objects[names[0]].data.polygons) == 12
    assert math.isclose(bpy.data.objects[names[1]].matrix_world.translation.x, 4, abs_tol=1e-4)
    print("COLLISION_OK", bpy.app.version_string)


if __name__ == "__main__":
    root_arg, temp_arg, case = sys.argv[sys.argv.index("--") + 1:]
    {"recipes": recipes, "collision": collision}[case](Path(root_arg), Path(temp_arg))
