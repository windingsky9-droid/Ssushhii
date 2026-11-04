"""
Duo Display: a cinematic two-player nameplate stage for Blender 4.2 LTS.

Builds the whole scene from code (no assets besides an optional font), then
renders one or more camera shots with Cycles. Every name, colour and shot is
a command-line argument, so the same file renders a private version with
real names and a public, brand-only version.

Run headless:

    blender -b --factory-startup --python duo_display.py -- \
        --left SUSHIR --right STUDIO \
        --font fonts/ChakraPetch-Bold.ttf --font-sub fonts/ChakraPetch-SemiBold.ttf \
        --shots hero,left,right --out renders/ --prefix sushir-studio

What is in the scene:
  * two hex-pedestal display monoliths angled toward the camera
  * extruded, bevelled 3D names with an emissive face and metal sides
  * HUD dressing: corner brackets, underline, status pips, subtitle
  * floating wireframe "cores" joined by an energy arc (the team-up link)
  * glossy floor with a fading emissive grid, light-strip back wall
  * thin volumetric haze lit by coloured spotlights (god rays)
  * bokeh dust, depth of field, AgX "Punchy" grade, bloom + lens dispersion
"""

import argparse
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector


# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description="Render the Duo Display stage.")
    p.add_argument("--left", default="SUSHIR", help="Name on the left display")
    p.add_argument("--right", default="STUDIO", help="Name on the right display")
    p.add_argument("--left-sub", default="REAL-TIME 3D")
    p.add_argument("--right-sub", default="CYCLES RENDER")
    p.add_argument("--left-color", default="00E1FF", help="Hex colour, left")
    p.add_argument("--right-color", default="FF8A1F", help="Hex colour, right")
    p.add_argument("--link-color", default="B9A6FF", help="Hex colour of the team-up arc")
    p.add_argument("--font", default="", help="TTF/OTF for the names")
    p.add_argument("--font-sub", default="", help="TTF/OTF for subtitles")
    p.add_argument("--shots", default="hero", help="Comma list: hero,left,right,wide")
    p.add_argument("--out", default="renders", help="Output folder")
    p.add_argument("--prefix", default="duo-display", help="Output file prefix")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--percent", type=int, default=100, help="Resolution percentage")
    p.add_argument("--samples", type=int, default=128)
    p.add_argument("--no-volume", action="store_true", help="Skip the haze (much faster)")
    p.add_argument("--save-blend", default="", help="Also save the scene to this .blend")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--pack", action="store_true", help="Pack fonts into the saved .blend")
    p.add_argument("--stage", type=int, default=6,
                   help="Build stage 1-6: blockout, materials, light, set dressing, atmosphere, lens + grade")
    p.add_argument("--sample-ladder", default="",
                   help="Comma list of sample counts, e.g. 1,4,16,64: renders the first shot once per count, no denoise")
    p.add_argument("--no-denoise", action="store_true")
    return p.parse_args(argv)


# Build stage, set from --stage. Each stage adds one layer of upgrades:
#   1 blockout (clay)  2 materials  3 lighting  4 set dressing
#   5 atmosphere (haze, god rays)   6 lens + grade (DOF, AgX Punchy, bloom, streaks)
STAGE = 6

STAGE_NAMES = {
    1: "Blockout",
    2: "Materials",
    3: "Lighting",
    4: "Set dressing",
    5: "Atmosphere",
    6: "Lens + grade",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def hex_to_linear(hex_code, alpha=1.0):
    """'#00E1FF' -> linear-light RGBA tuple, ready for shader inputs."""
    h = hex_code.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (lin(srgb[0]), lin(srgb[1]), lin(srgb[2]), alpha)


def mix_rgba(a, b, t):
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(4))


def link_object(obj, parent=None):
    bpy.context.scene.collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def mesh_object(name, bm, material=None, parent=None):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if material is not None:
        mesh.materials.append(material)
    return link_object(obj, parent)


def box(name, size, location=(0, 0, 0), material=None, parent=None, bevel=0.0):
    bm = bmesh.new()
    scale = Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(location) @ scale)
    obj = mesh_object(name, bm, material, parent)
    if bevel > 0:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    return obj


def hex_prism(name, radius, depth, location=(0, 0, 0), material=None, parent=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=6,
        radius1=radius, radius2=radius, depth=depth,
        matrix=Matrix.Translation(location) @ Matrix.Rotation(math.radians(30), 4, "Z"),
    )
    obj = mesh_object(name, bm, material, parent)
    if bevel > 0:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
    return obj


def cylinder(name, radius, depth, location=(0, 0, 0), material=None, parent=None, segments=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius, radius2=radius, depth=depth,
        matrix=Matrix.Translation(location),
    )
    obj = mesh_object(name, bm, material, parent)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def hex_ring(name, radius, thickness, location, material, parent=None, rotation=(0, 0, 0)):
    """A glowing hexagonal tube ring (a six-sided torus)."""
    bpy.ops.mesh.primitive_torus_add(
        major_segments=6, minor_segments=6,
        major_radius=radius, minor_radius=thickness,
        location=(0, 0, 0), rotation=(0, 0, 0),
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    # Move from the active collection into the scene root so parenting is simple.
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    link_object(obj, parent)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    return obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def new_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    return mat, nodes, mat.node_tree.links, out


def mat_emission(name, color, strength):
    mat, nodes, links, out = new_material(name)
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = color
    em.inputs["Strength"].default_value = strength
    links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def mat_metal(name, color=(0.06, 0.065, 0.075, 1.0), roughness=0.3):
    mat, nodes, links, out = new_material(name)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = roughness
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def mat_text_side(name, glow_color):
    """Polished dark metal that picks up a faint edge glow."""
    mat, nodes, links, out = new_material(name)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.05, 0.055, 0.06, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.18
    bsdf.inputs["Emission Color"].default_value = glow_color
    bsdf.inputs["Emission Strength"].default_value = 0.35
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def mat_screen(name, color):
    """Dark glass screen with holographic scanlines and an upward glow."""
    mat, nodes, links, out = new_material(name)
    coord = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(coord.outputs["Object"], sep.inputs["Vector"])

    # Scanlines: sin(z * k) -> thin bright bands.
    k = nodes.new("ShaderNodeMath")
    k.operation = "MULTIPLY"
    k.inputs[1].default_value = 140.0
    links.new(sep.outputs["Z"], k.inputs[0])
    sine = nodes.new("ShaderNodeMath")
    sine.operation = "SINE"
    links.new(k.outputs[0], sine.inputs[0])
    lines = nodes.new("ShaderNodeMapRange")
    lines.inputs["From Min"].default_value = 0.82
    lines.inputs["From Max"].default_value = 1.0
    lines.inputs["To Min"].default_value = 0.0
    lines.inputs["To Max"].default_value = 0.26
    links.new(sine.outputs[0], lines.inputs["Value"])

    # Vertical wash: brighter toward the top of the panel.
    wash = nodes.new("ShaderNodeMapRange")
    wash.inputs["From Min"].default_value = -0.9
    wash.inputs["From Max"].default_value = 0.9
    wash.inputs["To Min"].default_value = 0.004
    wash.inputs["To Max"].default_value = 0.07
    links.new(sep.outputs["Z"], wash.inputs["Value"])

    total = nodes.new("ShaderNodeMath")
    total.operation = "ADD"
    links.new(lines.outputs[0], total.inputs[0])
    links.new(wash.outputs[0], total.inputs[1])

    glass = nodes.new("ShaderNodeBsdfPrincipled")
    glass.inputs["Base Color"].default_value = (0.004, 0.005, 0.007, 1.0)
    glass.inputs["Roughness"].default_value = 0.12
    glass.inputs["Coat Weight"].default_value = 1.0
    glass.inputs["Coat Roughness"].default_value = 0.03
    glass.inputs["Emission Color"].default_value = color
    links.new(total.outputs[0], glass.inputs["Emission Strength"])
    links.new(glass.outputs["BSDF"], out.inputs["Surface"])
    return mat


def mat_floor(name, grid_color):
    """Glossy black floor with an emissive grid that fades with distance."""
    mat, nodes, links, out = new_material(name)
    coord = nodes.new("ShaderNodeTexCoord")
    brick = nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.squash = 1.0
    brick.inputs["Color1"].default_value = (0, 0, 0, 1)
    brick.inputs["Color2"].default_value = (0, 0, 0, 1)
    brick.inputs["Mortar"].default_value = (1, 1, 1, 1)
    brick.inputs["Scale"].default_value = 1.25
    brick.inputs["Mortar Size"].default_value = 0.012
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    links.new(coord.outputs["Object"], brick.inputs["Vector"])

    dist = nodes.new("ShaderNodeVectorMath")
    dist.operation = "LENGTH"
    links.new(coord.outputs["Object"], dist.inputs[0])
    fade = nodes.new("ShaderNodeMapRange")
    fade.inputs["From Min"].default_value = 2.0
    fade.inputs["From Max"].default_value = 14.0
    fade.inputs["To Min"].default_value = 1.0
    fade.inputs["To Max"].default_value = 0.0
    links.new(dist.outputs["Value"], fade.inputs["Value"])

    mask = nodes.new("ShaderNodeMath")
    mask.operation = "MULTIPLY"
    links.new(brick.outputs["Color"], mask.inputs[0])
    links.new(fade.outputs[0], mask.inputs[1])
    strength = nodes.new("ShaderNodeMath")
    strength.operation = "MULTIPLY"
    strength.inputs[1].default_value = 1.6
    links.new(mask.outputs[0], strength.inputs[0])

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.006, 0.007, 0.009, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.16
    bsdf.inputs["Emission Color"].default_value = grid_color
    links.new(strength.outputs[0], bsdf.inputs["Emission Strength"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def mat_haze(name, density):
    mat, nodes, links, out = new_material(name)
    vol = nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.8, 0.85, 1.0, 1.0)
    vol.inputs["Density"].default_value = density
    vol.inputs["Anisotropy"].default_value = 0.4
    links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return mat


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------

def _bake_text(name, body, font_path, extrude, bevel, spacing):
    """Bevelled text at size 1.0, baked to a mesh. Returns the mesh."""
    curve = bpy.data.curves.new(name=name, type="FONT")
    curve.body = body
    if font_path and os.path.isfile(font_path):
        curve.font = bpy.data.fonts.load(font_path, check_existing=True)
    curve.size = 1.0
    curve.extrude = extrude
    curve.bevel_depth = bevel
    curve.bevel_resolution = 3
    curve.space_character = spacing
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    tmp = bpy.data.objects.new(name + "_curve", curve)
    bpy.context.scene.collection.objects.link(tmp)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(depsgraph))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(curve)
    mesh.name = name
    return mesh


def _extent(mesh):
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    return (max(xs) - min(xs), max(ys) - min(ys),
            (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)


def fit_scale(bodies, font_path, max_w, max_h, extrude=0.07, bevel=0.012, spacing=1.04):
    """One scale that fits every body in the box, so both names share a letter height."""
    scales = []
    for i, body in enumerate(bodies):
        mesh = _bake_text(f"_measure{i}", body, font_path, extrude, bevel, spacing)
        w, h, _, _ = _extent(mesh)
        scales.append(min(max_w / max(w, 1e-6), max_h / max(h, 1e-6)))
        bpy.data.meshes.remove(mesh)
    return min(scales)


def text_mesh(name, body, font_path, scale, extrude, bevel, spacing,
              front_mat, side_mat, parent, location):
    """Bevelled 3D text with an emissive face and metal sides, centred and
    stood up facing -Y (toward the camera)."""
    mesh = _bake_text(name, body, font_path, extrude, bevel, spacing)
    mesh.materials.append(front_mat)
    mesh.materials.append(side_mat)
    for poly in mesh.polygons:
        poly.material_index = 0 if poly.normal.z > 0.6 else 1

    _, _, cx, cy = _extent(mesh)
    s = scale
    mesh.transform(Matrix.Diagonal((s, s, s, 1.0)) @ Matrix.Translation((-cx, -cy, 0)))

    obj = bpy.data.objects.new(name, mesh)
    link_object(obj, parent)
    obj.location = location
    obj.rotation_euler = (math.radians(90), 0, 0)
    return obj


# ---------------------------------------------------------------------------
# One display monolith
# ---------------------------------------------------------------------------

def build_display(tag, name, subtitle, color, x, yaw_deg, fonts, mats, scales):
    root = bpy.data.objects.new(f"{tag}_root", None)
    link_object(root)
    root.location = (x, 0, 0)
    root.rotation_euler = (0, 0, math.radians(yaw_deg))

    glow = mat_emission(f"{tag}_glow", color, 14.0)
    glow_soft = mat_emission(f"{tag}_glow_soft", color, 4.0)
    sub_col = mix_rgba(color, (1, 1, 1, 1), 0.65)
    sub_glow = mat_emission(f"{tag}_sub", sub_col, 3.0)
    screen = mat_screen(f"{tag}_screen", color)
    side = mat_text_side(f"{tag}_text_side", color)
    metal, metal_dark = mats["metal"], mats["metal_dark"]

    # Pedestal: stacked hex prisms with glowing seams.
    hex_prism(f"{tag}_ped_base", 1.05, 0.22, (0, 0, 0.11), metal_dark, root, bevel=0.02)
    hex_prism(f"{tag}_ped_seam", 0.99, 0.025, (0, 0, 0.235), glow, root)
    hex_prism(f"{tag}_ped_top", 0.92, 0.2, (0, 0, 0.345), metal, root, bevel=0.015)
    hex_prism(f"{tag}_ped_cap", 0.86, 0.02, (0, 0, 0.455), glow_soft, root)
    if STAGE >= 4:
        hex_ring(f"{tag}_floor_ring", 1.42, 0.018, (0, 0, 0.02), glow, root)
        hex_ring(f"{tag}_floor_ring2", 1.72, 0.008, (0, 0, 0.012), glow_soft, root)

    # Column up to the panel.
    cylinder(f"{tag}_column", 0.11, 0.8, (0, 0.05, 0.86), metal, root)
    cylinder(f"{tag}_column_glow", 0.118, 0.04, (0, 0.05, 0.9), glow, root)

    # Panel: back plate, screen, glowing frame.
    pw, ph, pz = 3.05, 1.78, 2.14
    box(f"{tag}_backplate", (pw + 0.16, 0.12, ph + 0.16), (0, 0.06, pz), metal_dark, root, bevel=0.025)
    box(f"{tag}_screen", (pw, 0.02, ph), (0, -0.01, pz), screen, root)
    t = 0.022
    box(f"{tag}_frame_top", (pw + 0.04, 0.03, t), (0, -0.025, pz + ph / 2 + t / 2), glow, root)
    box(f"{tag}_frame_bot", (pw + 0.04, 0.03, t), (0, -0.025, pz - ph / 2 - t / 2), glow, root)

    if STAGE >= 4:
        # HUD corner brackets.
        arm, bt = 0.32, 0.03
        for sx in (-1, 1):
            for sz in (-1, 1):
                cx, cz = sx * (pw / 2 - 0.12), pz + sz * (ph / 2 - 0.12)
                box(f"{tag}_br_h_{sx}{sz}", (arm, 0.02, bt), (cx - sx * (arm / 2 - bt / 2), -0.035, cz), glow, root)
                box(f"{tag}_br_v_{sx}{sz}", (bt, 0.02, arm), (cx, -0.035, cz - sz * (arm / 2 - bt / 2)), glow, root)

        # Status pips, top-left.
        for i in range(3):
            box(f"{tag}_pip{i}", (0.06, 0.02, 0.06),
                (-pw / 2 + 0.34 + i * 0.1, -0.035, pz + ph / 2 - 0.3), glow_soft if i else glow, root)

    # Name, underline, subtitle.
    text_mesh(f"{tag}_name", name, fonts["name"], scales["name"], 0.07, 0.012, 1.04,
              glow, side, root, (0, -0.075, pz + 0.12))
    if STAGE >= 4:
        box(f"{tag}_underline", (pw - 0.9, 0.02, 0.016), (0, -0.04, pz - 0.36), glow, root)
    text_mesh(f"{tag}_sub", subtitle, fonts["sub"], scales["sub"], 0.01, 0.002, 1.6,
              sub_glow, sub_glow, root, (0, -0.05, pz - 0.58))

    bpy.context.view_layer.update()
    world_core = root.matrix_world @ Vector((0, 0, 3.72))
    if STAGE < 4:
        return root, world_core

    # Floating wireframe core + orbit ring above the panel.
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.3, matrix=Matrix.Translation((0, 0, 0)))
    core = mesh_object(f"{tag}_core", bm, glow, root)
    core.location = (0, 0, 3.72)
    core.rotation_euler = (math.radians(18), math.radians(12), math.radians(25))
    wire = core.modifiers.new("wire", "WIREFRAME")
    wire.thickness = 0.022
    wire.use_even_offset = True
    hex_ring(f"{tag}_orbit", 0.55, 0.009, (0, 0, 3.72), glow_soft, root,
             rotation=(math.radians(72), 0, math.radians(20)))

    # Coloured god-ray spotlight behind and above (stage 3+, so stage 4 always has it).
    spot = bpy.data.lights.new(f"{tag}_spot", type="SPOT")
    spot.energy = 2200
    spot.color = color[:3]
    spot.spot_size = math.radians(38)
    spot.spot_blend = 0.4
    spot.shadow_soft_size = 0.12
    spot_obj = link_object(bpy.data.objects.new(f"{tag}_spot", spot), root)
    spot_obj.location = (0, 2.6, 6.2)
    look_at(spot_obj, (0, -1.6, 0))  # both points are in the root's local space
    return root, world_core


def add_display_spot(tag, root, color):
    """Stage 3 only: the coloured spot without the stage 4 set dressing."""
    spot = bpy.data.lights.new(f"{tag}_spot", type="SPOT")
    spot.energy = 2200
    spot.color = color[:3]
    spot.spot_size = math.radians(38)
    spot.spot_blend = 0.4
    spot.shadow_soft_size = 0.12
    spot_obj = link_object(bpy.data.objects.new(f"{tag}_spot", spot), root)
    spot_obj.location = (0, 2.6, 6.2)
    look_at(spot_obj, (0, -1.6, 0))


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

def build_scene(args):
    random.seed(args.seed)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    left_c = hex_to_linear(args.left_color)
    right_c = hex_to_linear(args.right_color)
    link_c = hex_to_linear(args.link_color)
    grid_c = mix_rgba(left_c, right_c, 0.5)

    mats = {
        "metal": mat_metal("metal", (0.11, 0.12, 0.13, 1.0), 0.28),
        "metal_dark": mat_metal("metal_dark", (0.035, 0.038, 0.045, 1.0), 0.38),
    }
    fonts = {"name": args.font, "sub": args.font_sub or args.font}

    # World: near-black, slightly blue.
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.0025, 0.003, 0.005, 1.0)
    bg.inputs["Strength"].default_value = 1.0

    # Floor.
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40.0)
    mesh_object("floor", bm, mat_floor("floor", grid_c))

    # Displays, angled inward like an open book. Both names share one scale.
    scales = {
        "name": fit_scale([args.left, args.right], fonts["name"], 2.5, 0.62),
        "sub": fit_scale([args.left_sub, args.right_sub], fonts["sub"], 1.5, 0.15,
                         extrude=0.01, bevel=0.002, spacing=1.6),
    }
    root_l, core_l = build_display("left", args.left, args.left_sub, left_c, -2.25, 14, fonts, mats, scales)
    root_r, core_r = build_display("right", args.right, args.right_sub, right_c, 2.25, -14, fonts, mats, scales)
    bpy.context.view_layer.update()
    if STAGE == 3:
        add_display_spot("left", root_l, left_c)
        add_display_spot("right", root_r, right_c)

    def area(name, energy, size, loc, target, color):
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = energy
        light.size = size
        light.color = color
        obj = link_object(bpy.data.objects.new(name, light))
        obj.location = loc
        look_at(obj, target)
        return obj

    if STAGE <= 2:
        # Stages 1-2: a single soft key so form and materials read on their own.
        area("key", 900 if STAGE == 1 else 420, 6.0, (-4.5, -7.0, 6.5), (0, 0, 1.6), (0.92, 0.95, 1.0))
        if STAGE == 1:
            bg.inputs["Color"].default_value = (0.03, 0.033, 0.04, 1.0)
            clay = bpy.data.materials.new("clay")
            clay.use_nodes = True
            pb = clay.node_tree.nodes["Principled BSDF"]
            pb.inputs["Base Color"].default_value = (0.52, 0.54, 0.57, 1.0)
            pb.inputs["Roughness"].default_value = 0.55
            for obj in scene.objects:
                for slot in getattr(obj, "material_slots", []):
                    slot.material = clay
        return scene

    if STAGE >= 4:
        build_dressing(scene, args, mats, core_l, core_r, left_c, right_c, link_c)

    # Key, fill and centre lights.
    area("key", 420, 5.0, (-4.5, -7.0, 6.5), (0, 0, 1.6), (0.85, 0.9, 1.0))
    area("fill", 160, 6.0, (5.5, -6.0, 2.0), (0, 0, 1.4), (1.0, 0.86, 0.75))
    area("rim", 260, 9.0, (0, 6.0, 4.0), (0, 0, 2.0), (0.7, 0.75, 1.0))
    top = bpy.data.lights.new("top", type="SPOT")
    top.energy = 1800
    top.spot_size = math.radians(30)
    top.spot_blend = 0.6
    top.color = (0.9, 0.92, 1.0)
    top_obj = link_object(bpy.data.objects.new("top", top))
    top_obj.location = (0, -1.0, 7.5)
    look_at(top_obj, (0, -1.0, 0))

    # Haze for god rays.
    if STAGE >= 5 and not args.no_volume:
        box("haze", (30, 26, 11), (0, 0.5, 5.4), mat_haze("haze", 0.009))

    return scene


def build_dressing(scene, args, mats, core_l, core_r, left_c, right_c, link_c):
    """Stage 4: the team-up arc, crystal, light-strip wall and dust."""
    # Team-up link: an energy arc from core to core through a centre crystal.
    link_glow = mat_emission("link_glow", link_c, 9.0)
    apex = Vector((0, -0.55, 4.25))
    curve = bpy.data.curves.new("link_arc", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.013
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(2)
    for bp, co in zip(spline.bezier_points, (core_l, apex, core_r)):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    arc = link_object(bpy.data.objects.new("link_arc", curve))
    arc.data.materials.append(link_glow)

    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.17)
    crystal = mesh_object("link_crystal", bm, mat_emission("crystal", mix_rgba(link_c, (1, 1, 1, 1), 0.4), 16.0))
    crystal.location = apex
    crystal.rotation_euler = (0.3, 0.5, 0.2)

    # Back wall with vertical light strips (become bokeh with DOF).
    box("back_wall", (34, 0.4, 14), (0, 9.5, 7), mats["metal_dark"])
    palette = [left_c, right_c, (0.9, 0.92, 1.0, 1.0), link_c]
    for i in range(-10, 11):
        if abs(i) < 1:
            continue
        h = random.uniform(2.5, 8.0)
        col = palette[(i + 10) % len(palette)]
        strength = random.uniform(0.8, 2.2)
        mat = mat_emission(f"strip_mat_{i}", col, strength)
        box(f"strip_{i}", (0.07, 0.05, h), (i * 1.55, 9.25, h / 2 + random.uniform(0.0, 2.5)), mat)

    # Dust motes.
    bm = bmesh.new()
    for _ in range(420):
        pos = Vector((random.uniform(-7.5, 7.5), random.uniform(-5.0, 7.0), random.uniform(0.2, 5.8)))
        r = random.uniform(0.004, 0.013)
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation(pos))
    mesh_object("dust", bm, mat_emission("dust", (1.0, 0.95, 0.9, 1.0), 2.5))


# ---------------------------------------------------------------------------
# Render setup
# ---------------------------------------------------------------------------

SHOTS = {
    #        camera location        look-at target        lens f-stop exposure bloom-mix
    "hero": ((0.0, -10.6, 1.45),  (0.0, 0.0, 2.25),     30, 3.2,  0.10,   -0.35),
    "left": ((-3.35, -5.5, 1.85), (-2.25, 0.0, 2.2),    50, 2.2, -0.70,   -0.62),
    "right": ((3.35, -5.5, 1.85), (2.25, 0.0, 2.2),     50, 2.2, -0.70,   -0.62),
    "wide": ((0.0, -15.5, 6.2),   (0.0, 0.0, 1.9),      28, 5.6,  0.00,   -0.40),
}


def setup_render(scene, args):
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "CPU"
    cy.samples = args.samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = not args.no_denoise
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 6
    cy.diffuse_bounces = 2
    cy.glossy_bounces = 3
    cy.transmission_bounces = 2
    cy.volume_bounces = 0
    cy.transparent_max_bounces = 4
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    cy.volume_step_rate = 2.5
    cy.volume_max_steps = 256
    scene.render.use_persistent_data = True

    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = args.percent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"

    scene.view_settings.view_transform = "AgX"
    looks = ("AgX - Punchy", "Punchy", "None") if STAGE >= 6 else ("None",)
    for look in looks:
        try:
            scene.view_settings.look = look
            break
        except TypeError:
            continue
    scene.view_settings.exposure = 0.0

    cam_data = bpy.data.cameras.new("camera")
    cam = link_object(bpy.data.objects.new("camera", cam_data))
    scene.camera = cam
    if STAGE < 6:
        scene.use_nodes = False
        scene.render.use_compositing = False
        return cam, None

    # Compositor: bloom + a touch of lens dispersion.
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    rl = tree.nodes.new("CompositorNodeRLayers")
    glare = tree.nodes.new("CompositorNodeGlare")
    try:
        glare.glare_type = "BLOOM"
    except TypeError:
        glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.threshold = 0.9
    glare.size = 8
    glare.mix = -0.35
    streaks = tree.nodes.new("CompositorNodeGlare")  # anamorphic-style flare
    streaks.glare_type = "STREAKS"
    streaks.quality = "HIGH"
    streaks.streaks = 2
    streaks.angle_offset = 0.0
    streaks.fade = 0.88
    streaks.threshold = 3.0
    streaks.mix = -0.82
    lens = tree.nodes.new("CompositorNodeLensdist")
    lens.inputs["Dispersion"].default_value = 0.012
    comp = tree.nodes.new("CompositorNodeComposite")
    tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"], streaks.inputs["Image"])
    tree.links.new(streaks.outputs["Image"], lens.inputs["Image"])
    tree.links.new(lens.outputs["Image"], comp.inputs["Image"])
    scene.render.use_compositing = True
    return cam, glare


def render_shots(scene, cam, glare, args):
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for shot in [s.strip() for s in args.shots.split(",") if s.strip()]:
        loc, target, lens, fstop, exposure, bloom_mix = SHOTS[shot]
        if glare is not None:
            scene.view_settings.exposure = exposure
            glare.mix = bloom_mix
        cam.location = loc
        look_at(cam, target)
        cam.data.lens = lens
        cam.data.dof.use_dof = STAGE >= 6
        cam.data.dof.focus_distance = (Vector(target) - Vector(loc)).length
        cam.data.dof.aperture_fstop = fstop
        path = os.path.join(out_dir, f"{args.prefix}-{shot}.png")
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        written.append(path)
        print(f"[duo-display] wrote {path}", flush=True)
    return written


def render_ladder(scene, cam, glare, args):
    """Render the first shot at rising sample counts with no denoiser, so the
    frames show Cycles converging from noise to the final image."""
    shot = [s.strip() for s in args.shots.split(",") if s.strip()][0]
    counts = [int(c) for c in args.sample_ladder.split(",") if c.strip()]
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    out = args.prefix
    for n in counts:
        scene.cycles.samples = n
        args.prefix = f"{out}-spp{n:04d}"
        args.shots = shot
        render_shots(scene, cam, glare, args)
    args.prefix = out


def main():
    global STAGE
    args = parse_args()
    STAGE = max(1, min(6, args.stage))
    print(f"[duo-display] stage {STAGE}: {STAGE_NAMES[STAGE]}", flush=True)
    scene = build_scene(args)
    cam, glare = setup_render(scene, args)
    if args.save_blend:
        cam.location, cam.data.lens = SHOTS["hero"][0], SHOTS["hero"][2]
        look_at(cam, SHOTS["hero"][1])
        os.makedirs(os.path.dirname(os.path.abspath(args.save_blend)), exist_ok=True)
        if args.pack:
            bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save_blend))
        print(f"[duo-display] saved {args.save_blend}", flush=True)
    if args.sample_ladder:
        render_ladder(scene, cam, glare, args)
    else:
        render_shots(scene, cam, glare, args)


if __name__ == "__main__":
    main()
