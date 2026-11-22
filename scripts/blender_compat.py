"""Runtime helpers shared by Blender animation and rendering recipes."""


def action_fcurves(owner):
    """Yield curves for the owner's assigned Action slot, including legacy Actions."""
    anim = owner.animation_data
    if not anim or not anim.action:
        return
    action = anim.action
    if not getattr(action, "is_action_layered", False):
        yield from getattr(action, "fcurves", ())
        return
    if anim.action_slot is None:
        return
    for layer in action.layers:
        for strip in layer.strips:
            if strip.type == "KEYFRAME":
                bag = strip.channelbag(anim.action_slot)
                if bag is not None:
                    yield from bag.fcurves


def configure_eevee(scene):
    """Apply the handbook preset, reporting unavailable switches on this build."""
    # The built-in EEVEE identifier is the static default of the engine RNA enum.
    engine = scene.render.bl_rna.properties["engine"].default
    if engine not in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
        raise ValueError(f"Unknown built-in EEVEE identifier: {engine}")
    scene.render.engine = engine
    eevee = scene.eevee
    unavailable = []
    for name, value in {
        "taa_render_samples": 64, "taa_samples": 16,
        "use_gtao": True, "gtao_distance": 0.2, "use_bloom": True,
        "use_ssr": True, "use_ssr_refraction": True, "use_volumetric_lights": True,
    }.items():
        if hasattr(eevee, name):
            setattr(eevee, name, value)
        else:
            unavailable.append(name)

    ao = "GTAO" if hasattr(eevee, "use_gtao") else None
    if hasattr(eevee, "use_raytracing"):
        eevee.use_raytracing = True
    method = eevee.bl_rna.properties.get("fast_gi_method")
    if ao is None and method and "AMBIENT_OCCLUSION_ONLY" in method.enum_items:
        # Blender 4.2 has the method but no separate Fast GI enable switch.
        if hasattr(eevee, "use_fast_gi"):
            eevee.use_fast_gi = True
        eevee.fast_gi_method = "AMBIENT_OCCLUSION_ONLY"
        eevee.fast_gi_distance = 0.2
        # At 1 all roughnesses are ray traced and Fast GI never contributes.
        options = eevee.ray_tracing_options
        if options.trace_max_roughness == 1:
            options.trace_max_roughness = 0.5
        ao = "Fast GI"

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    return {"engine": engine, "ambient_occlusion": ao, "unavailable_legacy_options": unavailable}
