# Intent → Sub-skill Routing

The router's core job is routing. Read the request, decide which manuals are needed, read each manual's `MANUAL.md`, and follow its patterns. Multiple intents in one request = chain multiple manuals.

---

## Primary routing table

| User intent (paraphrased) | Load these sub-skills | Order |
|--------------------------|----------------------|-------|
| "Make a 3D model of X" | `blender-modeling` | 1st |
| "From this wireframe drawing" | `wireframe-to-3d` | 1st |
| "Use these materials / make it look like X" | `blender-materials` | After modeling |
| "Light it / studio setup / cinematic" | `blender-lighting` | After geometry exists |
| "Hero shot / camera angle / DoF" | `blender-cameras` | After lighting |
| "Render it / produce an image" | `blender-rendering` | Last visual step |
| "Animate / move / rotate over time" | `blender-animation` | After geometry |
| "Export as glTF / FBX / OBJ / for web / for Unity" | `blender-export` | Final step |
| "Set up a scene / production-quality result" | `blender-pro-workflow` | First — guides everything |
| "I'm new / not sure where to start" | `blender-pro-workflow` | First |
| "This is sub-par / still wrong / same issue again" | `quality-refinement-autoloop`, then `blender-skill-harmonizer` | First — learn, sanitize, patch, then retry |
| "Match these templates / wireframes / textures exactly" | `reference-to-3d` first, then `blender-skill-harmonizer` when several skills conflict | First — establish source-of-truth gates |

### Multi-intent example

"Model a sword with materials, light it dramatically, and export as glTF" →

1. `blender-pro-workflow` (sequencing strategy)
2. `blender-modeling` (sword geometry)
3. `blender-materials` (steel + leather grip)
4. `blender-lighting` (dramatic 1-point or rim setup)
5. `blender-export` (glTF settings)

---

## Reference-locked work (source-of-truth gating)

When fidelity to a supplied source matters more than a plausible result, start in `08-reference-locked/` with `reference-to-3d`. Use `mascot-logo-reconstruction` when the request is a mascot, logo, or brand avatar. Load `blender-skill-harmonizer` only when several reference/UV/fit/repair skills conflict or a staged/parallel plan is needed. Then use the fit skills.

| Signal in the request | Route to |
|----------------------|----------|
| "must match this template / character sheet / mascot sheet" | `reference-to-3d` (or `mascot-logo-reconstruction` for mascot/logo/brand) |
| "fit this texture pack 1:1 / textures look stretched" | `blender-uv-texturing`, `atlas-uv-fitting` |
| "compare against the template, adjust until it fits" | `multiview-fit-loop` |
| Front/side/back/top views contradict each other | `multiview-constraint-solver` (decide feasibility **before** rebuilding) |
| Bbox/IoU passes but landmarks (eyes, leaf tips, shell corners) are off | `landmark-fit-repair` |
| Touching/overlapping parts must be separated before meshing | `source-part-segmentation` |
| Silhouette must follow an extracted 2D contour exactly | `contour-to-mesh` |
| Sidewalls or back caps render plain | `closed-surface-uv-coverage` |
| "too bright / desaturated / wrong hue / wrong glow" vs a source image | `reference-look-calibration` |
| "wrong number of visible parts" / part count must be exact | `reference-analysis-validator` |
| "it does not look like the reference" after a build | `fit-repair-optimizer`, then the specific repair skill |

Do not declare a 1:1 reconstruction complete without `reference-analysis-validator` or `qa-review` passing.

---

## Edge cases and deliberate redirects

| Situation | Do this |
|-----------|---------|
| Request contains "human" / "character" / "face" / "person" | Pure primitives produce a silhouette, **not** a face. Use the asset-generation MCP tools (`download_polyhaven_asset`, `download_sketchfab_model`, `generate_hyper3d_model_via_text`) for a base mesh, then chain materials + lighting + render. Load `character-artist` for proportions. Do NOT claim a sphere-with-features looks human. |
| Elongated subject (sword, spike, pole) | Orient the broad axis toward the camera — see `blender-modeling` "Critical: axis orientation for elongated objects". |
| Scene already contains objects | Operate on them. Do **not** delete unless asked. Only a lone default cube is safe to delete. |
| Ambiguous single request | Ask **one** question, then proceed with sensible defaults. |
| Request spans modeling + lighting + materials + export | `blender-pro-workflow` first, so the sequencing is owned by one skill rather than improvised. |
| Request is a knowledge question ("how does subsurf work?") | Answer directly. Do not drive Blender. |
| Request is outside Blender's strengths (CAD precision, engineering CFD) | Redirect politely — see "What this handbook is NOT for" in the entry `SKILL.md`. |

---

## Precedence rules

1. `blender-skill-harmonizer` owns activation precedence and conflict policy whenever two or more skills want to act on the same artifact.
2. `quality-refinement-autoloop` runs **before** further product work when output was rejected or an issue is recurring — learn and sanitize first, then retry.
3. A reference-locked request outranks generic production workflow: fidelity gates are not optional extras.
4. When no rule applies, use `${COMMANDCODE_SKILL_DIR}/references/assembly-order.md` as the default sequence.
