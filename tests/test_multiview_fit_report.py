import json
from importlib.util import find_spec
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "08-reference-locked" /
          "multiview-fit-loop/scripts/multiview_fit_report.py")


@unittest.skipUnless(find_spec("cv2") and find_spec("numpy"), "Requires OpenCV and NumPy")
class MultiviewFitReportTests(unittest.TestCase):
    def setUp(self):
        import cv2
        import numpy as np

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        blank = np.zeros((64, 64), dtype=np.uint8)
        render = blank.copy()
        render[20:44, 20:44] = 255
        smaller = blank.copy()
        smaller[24:40, 24:40] = 255
        images = {
            "template": 255 - render, "render": render,
            "blank-template": 255 - blank, "blank-render": blank,
            "shifted": np.roll(render, 8, axis=1), "smaller": smaller,
        }
        for name, image in images.items():
            self.assertTrue(cv2.imwrite(str(self.root / f"{name}.png"), image))

    def run_report(self, **images):
        with tempfile.TemporaryDirectory(dir=self.root) as tmp:
            out = Path(tmp) / "fit.json"
            overlays = Path(tmp) / "overlays"
            args = [sys.executable, str(SCRIPT), "--out", str(out), "--overlay-dir", str(overlays)]
            for option, image in images.items():
                args.extend(["--" + option.replace("_", "-"), str(self.root / f"{image}.png")])
            run = subprocess.run(args, capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["schema"], "multiview_fit_report.v1")
            self.assertEqual(json.loads(run.stdout), report["summary"])
            self.assertEqual({p.name for p in overlays.glob("*.png")},
                             {f"{view}_fit_overlay.png" for view in report["views"]})
            return report

    def assert_summary(self, report, centers, sizes):
        self.assertEqual(report["summary"], {
            "all_bbox_centers_pass": centers,
            "all_bbox_sizes_pass_5pct": sizes,
            "all_views_pass_first_pass": centers and sizes,
        })

    def test_empty_side_masks_fail_even_when_front_matches(self):
        for template, render in [("blank-template", "render"), ("template", "blank-render"),
                                 ("blank-template", "blank-render")]:
            with self.subTest(template=template, render=render):
                report = self.run_report(front_template="template", front_render="render",
                                         side_template=template, side_render=render)
                self.assertTrue(report["views"]["front"]["pass_bbox_center_1p5pct"])
                self.assertTrue(report["views"]["front"]["pass_bbox_size_5pct"])
                side = report["views"]["side"]
                self.assertEqual(side["reference_bbox"] is None, template == "blank-template")
                self.assertEqual(side["render_bbox"] is None, render == "blank-render")
                self.assertEqual(side["iou"], 0.0)
                self.assertNotIn("pass_bbox_center_1p5pct", side)
                self.assertNotIn("pass_bbox_size_5pct", side)
                self.assert_summary(report, False, False)

    def test_center_and_size_checks_remain_independent(self):
        for render, centers, sizes, iou in [("render", True, True, 1.0),
                                           ("shifted", False, True, 0.5),
                                           ("smaller", True, False, 4 / 9)]:
            with self.subTest(render=render):
                report = self.run_report(front_template="template", front_render="render",
                                         side_template="template", side_render=render)
                self.assertEqual(set(report["views"]), {"front", "side"})
                self.assertAlmostEqual(report["views"]["side"]["iou"], iou)
                self.assert_summary(report, centers, sizes)

    def test_only_complete_pairs_are_compared(self):
        for optional in [{}, {"side_template": "template"}, {"side_render": "render"}]:
            with self.subTest(optional=optional):
                report = self.run_report(front_template="template", front_render="render", **optional)
                self.assertEqual(set(report["views"]), {"front"})
                self.assert_summary(report, True, True)
        report = self.run_report()
        self.assertEqual(report["views"], {})
        self.assert_summary(report, False, False)
