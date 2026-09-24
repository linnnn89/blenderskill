"""Three focused regressions; Blender runs in a separate factory-startup process."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "01-orchestration/blender-skill-harmonizer/scripts/skill_graph_audit.py"
RECOVERY = ROOT / "01-orchestration/quality-refinement-autoloop/scripts"


def python_run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", timeout=30)


class HandbookTests(unittest.TestCase):
    def test_audit_uses_installed_structure_and_rejects_broken_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "SKILL.md").write_text("# Router", encoding="utf-8")
            group = root / "01-example"
            manual = group / "example/MANUAL.md"
            manual.parent.mkdir(parents=True)
            manual.write_text("---\nname: example\n---\n# Example\n", encoding="utf-8")
            index = group / "INDEX.md"
            index.write_text("`example/MANUAL.md`", encoding="utf-8")
            good = python_run(AUDIT, "--skill-root", root)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertEqual(json.loads(good.stdout)["manuals"], 1)
            manual.write_text(manual.read_text() + "`scripts/missing.py`\n", encoding="utf-8")
            broken = python_run(AUDIT, "--skill-root", root)
            self.assertEqual(broken.returncode, 2)
            self.assertTrue(any("scripts/missing.py" in e for e in json.loads(broken.stdout)["errors"]))
            index.write_text("`missing/MANUAL.md`", encoding="utf-8")
            missing = python_run(AUDIT, "--plugin-root", root)
            errors = json.loads(missing.stdout)["errors"]
            self.assertEqual(missing.returncode, 2)
            self.assertTrue(any("Unindexed manual" in e for e in errors))
            self.assertTrue(any("Missing index target" in e for e in errors))

    def test_recovery_stays_in_artifact_scope_and_release_layout_is_explicit(self):
        plan = RECOVERY / "ralph_autoloop_plan.py"
        result = python_run(plan, "--feedback", "same issue: texture stretched")
        self.assertEqual(result.returncode, 0, result.stderr)
        recovery = json.loads(result.stdout)
        self.assertEqual(recovery["mode"], "artifact_recovery")
        self.assertIn("repair_artifact", recovery["phases"])
        self.assertNotIn("patch_skill", recovery["phases"])
        self.assertEqual(recovery["max_unsuccessful_cycles"], 3)
        explicit = python_run(plan, "--feedback", "texture stretched", "--skill-maintenance")
        self.assertEqual(explicit.returncode, 0, explicit.stderr)
        self.assertIn("patch_skill", json.loads(explicit.stdout)["phases"])
        with tempfile.TemporaryDirectory() as tmp:
            release = python_run(RECOVERY / "release_readiness_check.py",
                                 "--repo-root", tmp, "--expected-version", "1.0.0")
            self.assertEqual(release.returncode, 2)
            self.assertFalse(json.loads(release.stdout)["passed"])
            self.assertIn("upstream plugin", json.loads(release.stdout)["error"])
            self.assertNotIn("Traceback", release.stderr)

    def test_blender_helpers_preserve_scene_and_limit_export_scope(self):
        executable = os.environ.get("BLENDER_EXECUTABLE") or shutil.which("blender")
        if not executable:
            installations = sorted(Path("C:/Program Files/Blender Foundation").glob("Blender */blender.exe"))
            executable = str(installations[-1]) if installations else None
        if not executable:
            self.skipTest("Set BLENDER_EXECUTABLE to run the isolated Blender integration test")
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            script = temp / "scene_check.py"
            script.write_text(BLENDER_SCENARIO, encoding="utf-8")
            env = dict(os.environ)
            for key in ("BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "BLENDER_USER_DATAFILES"):
                folder = temp / key
                folder.mkdir()
                env[key] = str(folder)
            result = subprocess.run(
                [executable, "--background", "--factory-startup", "--disable-autoexec",
                 "--python-exit-code", "1", "--python", str(script), "--", str(ROOT), str(temp)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("HANDBOOK_SCENE_CHECK_OK", result.stdout)
            print(result.stdout.strip())


BLENDER_SCENARIO = r"""
import bpy
import json
from pathlib import Path
import runpy
import struct
import sys

root, temp = map(Path, sys.argv[sys.argv.index('--') + 1:])
scene = bpy.context.scene
original_world = scene.world
original_nodes = [(node.name, node.type) for node in original_world.node_tree.nodes]
second_scene = bpy.data.scenes.new('unrelated-scene')
second_scene.world = original_world
bpy.ops.mesh.primitive_cube_add()
target = bpy.context.object
target.name = 'GEO-target'
target.scale = (2, 3, 4)
bpy.ops.mesh.primitive_cube_add()
other = bpy.context.object
other.name = 'GEO-unrelated'
other.scale = (5, 6, 7)
other.location = (8, 9, 10)
owned = bpy.data.materials.new('MAT-temporary')
unrelated = bpy.data.materials.new('MAT-unrelated')
protected = bpy.data.materials.new('MAT-keep')
protected.use_fake_user = True
snapshot = (len(bpy.data.worlds), len(bpy.data.materials), tuple(target.scale), tuple(other.scale))
helpers = {name: runpy.run_path(str(root / 'scripts' / (name + '.py')))
           for name in ('reset_world', 'apply_transforms', 'cleanup_unused')}
assert snapshot == (len(bpy.data.worlds), len(bpy.data.materials), tuple(target.scale), tuple(other.scale))
assert scene.world == original_world
assert [(n.name, n.type) for n in original_world.node_tree.nodes] == original_nodes

apply = helpers['apply_transforms']['apply_transforms']
selected = [o.name for o in bpy.context.selected_objects]
active = bpy.context.view_layer.objects.active
try:
    apply([target.name, 'not-present'], scale=True)
    raise AssertionError('Missing target was not rejected')
except ValueError:
    pass
assert tuple(target.scale) == (2, 3, 4)
other.animation_data_create()
try:
    apply([target.name, other.name], scale=True)
    raise AssertionError('Animation target was not rejected')
except ValueError:
    pass
assert tuple(target.scale) == (2, 3, 4)
other.animation_data_clear()
assert apply([target.name], scale=True) == [target.name]
assert tuple(target.scale) == (1, 1, 1)
assert tuple(target.dimensions) == (4, 6, 8)
assert tuple(other.scale) == (5, 6, 7)
assert tuple(other.location) == (8, 9, 10)
assert [o.name for o in bpy.context.selected_objects] == selected
assert bpy.context.view_layer.objects.active == active

cleanup = helpers['cleanup_unused']['cleanup_unused']
candidates = {'materials': ['MAT-temporary', 'MAT-keep']}
assert cleanup(candidates) == {'materials': 1}
assert bpy.data.materials.get('MAT-temporary') is not None
assert cleanup(candidates, dry_run=False) == {'materials': 1}
assert bpy.data.materials.get('MAT-temporary') is None
assert bpy.data.materials.get('MAT-unrelated') == unrelated
assert bpy.data.materials.get('MAT-keep') == protected

new_world = helpers['reset_world']['reset_world'](scene=scene)
assert scene.world == new_world and new_world != original_world
assert second_scene.world == original_world
assert [(n.name, n.type) for n in original_world.node_tree.nodes] == original_nodes

# Exercise the target-only export workflow and inspect the GLB's actual scene nodes.
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True)
bpy.context.view_layer.objects.active = target
output = temp / 'target.glb'
result = bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True)
assert 'FINISHED' in result
blob = output.read_bytes()
assert blob[:4] == b'glTF'
length, kind = struct.unpack_from('<II', blob, 12)
assert kind == 0x4E4F534A
payload = json.loads(blob[20:20 + length])
assert [node['name'] for node in payload['nodes']] == ['GEO-target']
assert tuple(other.scale) == (5, 6, 7)
print('HANDBOOK_SCENE_CHECK_OK Blender=' + bpy.app.version_string)
"""

if __name__ == "__main__":
    unittest.main()
