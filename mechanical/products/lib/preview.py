# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""preview.py - tiny software renderer (matplotlib, painter's algorithm) for STL sanity checks,
and printability analysis (overhang area, bed fit) with trimesh."""
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def load(path):
    m = trimesh.load(path, force="mesh")
    return m


def rot(elev, azim):
    e, a = np.radians(elev), np.radians(azim)
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return rx @ rz


def _raster(meshes, colors, R, ctr, ext, px, light):
    """Orthographic z-buffer rasteriser. Returns an RGB image (px x px, white background)."""
    img = np.ones((px, px, 3))
    zb = np.full((px, px), -1e9)
    sc = px / (2 * ext)
    for mi, m in enumerate(meshes):
        tri = (m.triangles - ctr) @ R.T
        nrm = m.face_normals @ R.T
        base = np.array(colors[mi] if colors else (0.75, 0.55, 0.95), float)
        shade = np.clip(nrm @ light, 0, 1) * 0.6 + 0.4
        sx = tri[:, :, 0] * sc + px / 2
        sy = px / 2 - tri[:, :, 1] * sc
        for k in range(len(tri)):
            if nrm[k, 2] < -0.05:          # back face (camera looks down -Z', faces point +Z')
                continue
            x, y, z = sx[k], sy[k], tri[k, :, 2]
            x0, x1 = int(max(0, np.floor(x.min()))), int(min(px - 1, np.ceil(x.max())))
            y0, y1 = int(max(0, np.floor(y.min()))), int(min(px - 1, np.ceil(y.max())))
            if x1 < x0 or y1 < y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(d) < 1e-12:
                continue
            l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
            l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not inside.any():
                continue
            zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            upd = inside & (zz > sub)
            sub[upd] = zz[upd]
            img[y0:y1 + 1, x0:x1 + 1][upd] = base * shade[k]
    return img


def render(meshes, path_png, views=((25, -35), (90, 0), (0, 0)), titles=None, colors=None, size=5.0, px=620):
    """meshes: list of trimesh; views: (elev, azim): elev 90 = looking straight down, 0 = from the side."""
    allv = np.vstack([m.vertices for m in meshes])
    ctr = (allv.max(0) + allv.min(0)) / 2
    ext = (allv.max(0) - allv.min(0)).max() / 2 * 1.05
    light = np.array([0.35, -0.45, 0.82]); light /= np.linalg.norm(light)
    fig, axes = plt.subplots(1, len(views), figsize=(size * len(views), size))
    axes = np.atleast_1d(axes)
    for ax, (el, az), i in zip(axes, views, range(len(views))):
        R = rot(el - 90, az)
        img = _raster(meshes, colors, R, ctr, ext, px, light)
        ax.imshow(img); ax.axis("off")
        if titles:
            ax.set_title(titles[i], fontsize=9)
    fig.savefig(path_png, dpi=100, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box_mesh(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0),
                                transform=trimesh.transformations.translation_matrix(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def cut(mesh, origin, normal):
    """Keep the part of the mesh on the negative side of the plane (capped)."""
    return trimesh.intersections.slice_mesh_plane(mesh, plane_normal=-np.array(normal, float), plane_origin=origin, cap=True)


def overhang_report(mesh, max_deg=47.0, bed_tol=0.05):
    """Area of faces that face downward more steeply than max_deg from vertical-wall
    (i.e. need support), excluding faces lying on the bed. Mesh must be in print pose (z up)."""
    n = mesh.face_normals
    a = mesh.area_faces
    zmin = mesh.bounds[0][2]
    cz = mesh.triangles_center[:, 2]
    # angle between the face normal and straight down; walls = 90 deg; overhang when angle < 90 - max_deg...
    down = -n[:, 2]                              # 1 = facing straight down
    on_bed = (cz < zmin + bed_tol) & (down > 0.99)
    limit = np.cos(np.radians(90.0 - max_deg))   # faces whose |down| component exceeds this are overhangs
    over = (down > limit) & ~on_bed
    return dict(overhang_area=float(a[over].sum()), total_area=float(a.sum()),
                bed_area=float(a[on_bed].sum()), worst=float(down[~on_bed].max() if (~on_bed).any() else 0))
