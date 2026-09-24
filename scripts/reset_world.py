"""Reset the Blender world to a neutral, known-good baseline.

Why: previous runs can leave the scene's world broken -- particularly an
`Environment Texture` node with `image=None` cascading into Background, which
produces a magenta-flooded render. Run this at the start of EVERY scene build,
before any composition work.

Usage (via mcp__blender__execute_blender_code):

    exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/reset_world.py").read())

Loading the file performs the reset and prints a confirmation. To override the
baseline (e.g. a brighter neutral for a studio look), call the function
directly instead:

    reset_world(color=(0.05, 0.05, 0.06, 1.0), strength=0.8)

If the user wants HDRI lighting, do it AFTER this runs -- load the actual .hdr
file and verify `env.image is not None`.
"""

import bpy

DEFAULT_COLOR = (0.04, 0.04, 0.05, 1.0)
DEFAULT_STRENGTH = 0.4


def reset_world(scene=None, color=DEFAULT_COLOR, strength=DEFAULT_STRENGTH):
    """Replace the world node tree with a single Background -> World Output pair."""
    scene = scene or bpy.context.scene
    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    for n in list(nodes):
        nodes.remove(n)

    output = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = color
    bg.inputs["Strength"].default_value = strength
    world.node_tree.links.new(bg.outputs["Background"], output.inputs["Surface"])

    return world


_world = reset_world()
print(f"world-reset: {_world.name} color={DEFAULT_COLOR} strength={DEFAULT_STRENGTH}")
