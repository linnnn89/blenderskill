"""Detect Blender runtime version and API feature flags.

Run this at the start of a session or when encountering unexpected API behavior.
It probes current environment quirks and prints a structured JSON status.

Usage (via mcp__blender__execute_blender_code):

    exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/detect_blender_version.py").read())
"""

import json
import bpy


def detect_environment():
    version_tuple = bpy.app.version
    version_str = bpy.app.version_string

    # Read the compiled-in engine identifier without switching the active renderer.
    engine_name = bpy.types.RenderSettings.bl_rna.properties["engine"].default
    has_layered_actions = "layers" in bpy.types.Action.bl_rna.properties

    # 3. Disabled / special BSDF inputs
    disabled_inputs = []
    temp_mat = bpy.data.materials.new("_temp_compat_probe")
    try:
        if temp_mat.node_tree is None:
            temp_mat.use_nodes = True
        bsdf = temp_mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            disabled_inputs = [inp.name for inp in bsdf.inputs if not inp.enabled]
    finally:
        bpy.data.materials.remove(temp_mat)

    # 4. Mesh auto-smooth
    has_mesh_auto_smooth = "use_auto_smooth" in bpy.types.Mesh.bl_rna.properties

    info = {
        "version": list(version_tuple),
        "version_string": version_str,
        "eevee_engine": engine_name,
        "layered_actions": has_layered_actions,
        "disabled_bsdf_inputs": disabled_inputs,
        "has_mesh_auto_smooth": has_mesh_auto_smooth,
    }
    return info


result = detect_environment()
print(f"blender-env-detect: {json.dumps(result)}")
