"""Remove orphan data blocks to keep .blend files lean.

Blender accumulates unused materials, meshes, images, and node groups
as you iterate. Run this before export to avoid shipping dead weight.

Usage (via mcp__blender__execute_blender_code):

    exec(open(r"${COMMANDCODE_SKILL_DIR}/scripts/cleanup_unused.py").read())

Loading the file runs the cleanup and prints a summary. To preview
without deleting, call cleanup_unused(dry_run=True).
"""

import bpy


def cleanup_unused(dry_run=False):
    """Purge orphan data blocks. Returns a dict of {category: count}."""
    categories = [
        ("materials", bpy.data.materials),
        ("meshes", bpy.data.meshes),
        ("images", bpy.data.images),
        ("node_groups", bpy.data.node_groups),
        ("textures", bpy.data.textures),
        ("curves", bpy.data.curves),
        ("armatures", bpy.data.armatures),
        ("cameras", bpy.data.cameras),
        ("lights", bpy.data.lights),
        ("worlds", bpy.data.worlds),
        ("actions", bpy.data.actions),
    ]

    removed = {}
    for name, collection in categories:
        orphans = [item for item in collection if item.users == 0]
        removed[name] = len(orphans)
        if not dry_run:
            for item in orphans:
                collection.remove(item)

    return removed


_result = cleanup_unused()
_total = sum(_result.values())
_nonzero = {k: v for k, v in _result.items() if v > 0}
_mode = "removed" if _total > 0 else "nothing to clean"
print(f"cleanup-unused: {_mode} — total={_total} {_nonzero if _nonzero else ''}")
