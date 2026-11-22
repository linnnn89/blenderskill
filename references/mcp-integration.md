# MCP Integration

The Blender MCP transport, install, client wiring, safe mode, telemetry, and connection troubleshooting live in the separate **`blender-mcp`** skill. Use that skill when the problem is the connection or the MCP surface.

The community project publishes **`mcp-for-blender`**. Both community and Blender Lab installations may appear under a client alias such as `blender`. Identify them from the advertised tools. [Community repository](https://github.com/ahujasid/mcp-for-blender)

---

## Choose the connection for this task

Honor the user's selected backend. Otherwise prefer Blender Lab for shared operations when it is connected to the intended scene. Use the community backend for requested provider features it actually advertises. Check the live tool list and make a read-only query for the scene, blend filepath and Blender version before editing. Keep subsequent calls on that instance. For a Finisher task, use the NIUA manual and its health check.

```python
import bpy
result = {"scene": bpy.context.scene.name, "blend": bpy.data.filepath, "version": bpy.app.version_string}
print(result)
```

| Operation | Blender Lab | Community `mcp-for-blender` 2.3.1 | Older community servers, when advertised |
|-----------|-------------|------------------------------------|------------------------------------------|
| Inspect scene | `get_objects_summary()` | `get_scene_info(fields=["settings"])` | `get_scene_info()` |
| Inspect object | `get_object_detail_summary(name=...)` | `get_scene_info(query=..., fields=["size", "details", "modifiers"])` | `get_object_info(object_name=...)` |
| Run Blender Python | `execute_blender_code(code=...)` | `execute_blender_code(code=...)` | `execute_blender_code(code=...)` |
| Inspect an image | `get_screenshot_of_area_as_image(area_ui_type="VIEW_3D")` for a GUI area | `look(mode="camera")` for a quick render, `look(image="Render Result")` for the last render | `get_viewport_screenshot` |
| Find/import provider assets | Inspect configured capabilities | `get_addon_status()`, then `search_assets(source=...)` and `import_asset(source=..., id=...)` | Provider-specific calls below |

Community `query` matches a substring. Verify the exact returned name before acting. Use `fields` and `limit` to bound large-scene reads. Check provider availability and the requested asset scope before importing. The community 2.3.1 default `look` shading produces a low-sample render. If it falls back to the plain viewport, the response includes a note. [Community tool definitions](https://github.com/ahujasid/mcp-for-blender/blob/a5a8acf2c6/src/blender_mcp/server.py)

For portable Python, assign a JSON-safe dict to `result` and also print it. On Lab, inspect the outer `status` and any status in `result`. The Lab render tool `render_viewport_to_path(output_path=...)` uses the requested basename in Blender's scratch directory. Inspect the returned `result.filepath`. For an exact destination, render through Python with the agreed filepath. [Blender Lab tool source](https://projects.blender.org/lab/blender_mcp/src/commit/dbbf836ad4b1025f14a2b3b504c43903f39e0b04/mcp/blmcp/tools)

On a community timeout, Blender may still be executing on its main thread. Wait, query the same instance and inspect the named objects or output. Resume only the part still missing. A refused connection requires a transport check on the selected endpoint. [Community timeout handling](https://github.com/ahujasid/mcp-for-blender/commit/b36cf67169)

Execution rules for generated Python are in `${COMMANDCODE_SKILL_DIR}/references/code-execution-rules.md`.

---

## Legacy community asset tools

These examples and the provider-specific generation tools below describe older installations. In 2.3.1 use the consolidated tools above, or `generate_3d(provider=...)` for an explicitly requested generator.

### Poly Haven — HDRIs, textures, and models

Free CC0 library. Preferred source for production-quality environments, PBR textures, and pre-built models.

| Tool | Purpose |
|------|---------|
| `mcp__blender__search_polyhaven_assets` | Search the Poly Haven catalog |
| `mcp__blender__download_polyhaven_asset` | Download and import an asset by slug |

**Key behaviours** (from addon source):
- **Models import from `.blend`** (lossless); glTF/FBX are lossy fallbacks used only when the `.blend` was authored in a newer Blender than the running version.
- **Textures** download only the maps that wire to Principled BSDF: Diffuse, Rough, Metal, Displacement, nor_gl. AO, spec, anisotropy maps are skipped to keep downloads small.
- **HDRIs** default to `.hdr` format; `.exr` also available.
- Timeouts: API 10s connect / 30s read; file downloads 10s / 60s.
- Search results capped at 20 (max 50).

**Typical usage:**
```python
# Search for a forest HDRI
mcp__blender__search_polyhaven_assets(query="forest", type="hdris")

# Download and apply
mcp__blender__download_polyhaven_asset(slug="forest_slope", type="hdris", resolution="2k")
```

### Sketchfab — Community 3D models

Large catalog of user-uploaded models. Requires API key for downloads.

| Tool | Purpose |
|------|---------|
| `mcp__blender__search_sketchfab_models` | Search the Sketchfab catalog |
| `mcp__blender__download_sketchfab_model` | Download and import a model by UID |

**Notes:**
- API credentials can be set persistently in the addon preferences.
- Downloaded models may use non-Principled materials; rebuild if export is needed.

### Poly Pizza — Low-poly models

Curated low-poly / stylized models. Good for game assets and quick prototyping.

| Tool | Purpose |
|------|---------|
| `mcp__blender__search_polypizza_models` | Search with optional category and licence filters |
| `mcp__blender__download_polypizza_model` | Download and import a model by ID |

**Known issue — Cloudflare CDN blocking:**
Poly Pizza's CDN (`static.poly.pizza`) uses Cloudflare bot protection. Downloads from datacenter/VPN/cloud IPs get a 403 HTML challenge instead of the GLB file. This is **not** an API key problem. Workarounds:
1. Retry from a residential IP connection.
2. Download the `.glb` manually from `https://poly.pizza` and import via File → Import → glTF 2.0.

**Category IDs** (0–11): passed as integers. Licence IDs: 0 = CC-BY, 1 = CC0.

---

## AI 3D generation tools

### Hyper3D Rodin — Text/image to 3D

Generate 3D models from text descriptions or reference images using the Rodin API.

| Tool | Purpose |
|------|---------|
| `mcp__blender__generate_hyper3d_model_via_text` | Generate a 3D model from a text prompt |
| `mcp__blender__generate_hyper3d_model_via_image` | Generate a 3D model from a reference image |

**Notes:**
- Free trial available with key `vibecoding`.
- Results are stylized meshes, not production topology. Use as a starting point, then retopologize.
- API credentials can be stored persistently in addon preferences.

### Hunyuan3D — Tencent's 3D generation

Another AI model generation option.

| Tool | Purpose |
|------|---------|
| `mcp__blender__generate_hunyuan3d_model` | Generate a 3D model via Hunyuan3D |

---

## When to use asset tools vs. manual modeling

| Situation | Approach |
|-----------|----------|
| User asks for a "human" / "character" / "face" | Use asset tools for a base mesh, then chain materials + lighting |
| Need realistic environment backdrop | Poly Haven HDRIs or models |
| Quick prototype / game jam style | Poly Pizza low-poly models |
| Specific branded/custom object | Manual modeling via `02-modeling/` manuals |
| "Make a 3D model from this description" | Try Hyper3D Rodin text-to-3D, then refine |

---

## Historical community connection limits (verify against the running server)

| Parameter | Value | Source |
|-----------|-------|--------|
| Max snapshot objects | 4000 | `MAX_SNAPSHOT_OBJECTS` in addon.py |
| Max snapshot selected | 1000 | `MAX_SNAPSHOT_SELECTED` in addon.py |
| Default port | 9876 | Configurable via `BLENDER_PORT` env var |
| Code execution timeout | 180 s | Per-call limit |
| Protocol version | 9 | `ADDON_PROTOCOL_VERSION` in addon.py |
