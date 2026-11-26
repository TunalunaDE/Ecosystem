# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""nk_cad.py - small CadQuery helpers for noknok product housings (exploration, Nov 2026).

Module data (board size, mounting holes, clearances, window) comes from each module repo's
`mechanical/housing.json` (spec: Ecosystem mechanical/housing-profile.md). Values are copied here
with the date they were read; a module change means re-reading its housing.json.

Coordinates of a module are "payload view": origin = bottom-left corner of the PCB looking at the
side the user touches, x right, y up. A face plate is built in a LOCAL frame (x right, y up the
slope, z OUT of the face); `to_desk` rotates it onto the slanted face of a wedge.
"""
import math
import cadquery as cq

PCB_T = 1.6
M25_PILOT = 2.4       # pilot for an M2.5 self-tapping steel screw in PLA: fit coupon 20 Nov 2026 (2.0-2.3 would not take the screw, 2.4 holds)
M25_CLEAR = 2.7       # clearance hole for an M2.5 screw
M25_HEAD = 4.8        # countersink diameter for an M2.5 pan/cheese head

# --- modules (payload view, mm) - source: module repos mechanical/housing.json, read 20 Nov 2026 ---
MODULES = {
    "knob": dict(w=20, h=20, ct=6.0, cb=3.0,
                 holes=[(2.25, 2.25), (17.75, 17.75)],
                 feature=("round", 10.0, 10.25, 7.5)),            # shaft/bushing hole d7.5 at (10, 10.25)
    "led_button": dict(w=20, h=20, ct=4.5, cb=3.0,
                       holes=[(2.25, 2.25), (17.75, 17.75)],
                       feature=("rect", 10.0, 10.0, 16.4, 16.2)),  # switch body 15.9 x 15.7 + clearance
    "buzzer": dict(w=20, h=20, ct=3.0, cb=3.0,
                   holes=[(2.25, 2.25), (17.75, 17.75)],
                   feature=("grille", 10.0, 10.0, 8.5)),           # MLT-8530 sound port d8.5
    "display": dict(w=40, h=30, ct=1.0, cb=3.0,
                    holes=[(2.25, 2.25), (2.25, 27.75), (37.75, 2.25), (37.75, 27.75)],
                    feature=("rect", 19.8, 15.0, 37.5, 18.4)),     # window frames the whole glass
}
PICOHUB = dict(w=80, h=40, ct=18.0, cb=3.5,
               holes=[(2.25, 2.25), (77.75, 2.25), (2.25, 37.75), (77.75, 37.75)],
               usb_power=(68.0, 2.84))                              # J1 USB-C, opens on the S edge


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2.0).extrude(z1 - z0)


def union(*ws):
    out = ws[0]
    for w in ws[1:]:
        out = out.union(w)
    return out


def hex_grille(cx, cy, z0, z1, hole_d, pitch, radius):
    """Hex pattern of round holes inside a circle of `radius` (for the buzzer's sound port)."""
    pts = []
    rows = int(radius / (pitch * 0.866)) + 1
    for j in range(-rows, rows + 1):
        for i in range(-rows - 1, rows + 2):
            x = cx + (i + 0.5 * (j % 2)) * pitch
            y = cy + j * pitch * 0.866
            if math.hypot(x - cx, y - cy) <= radius - hole_d / 2:
                pts.append((x, y))
    out = None
    for (x, y) in pts:
        c = cyl(x, y, z0, z1, hole_d)
        out = c if out is None else out.union(c)
    return out


def to_desk(w, theta_deg, front_height):
    """Local face frame -> desk frame: tilt about X by theta, front edge at (y=0, z=front_height)."""
    return w.rotate((0, 0, 0), (1, 0, 0), theta_deg).translate((0, 0, front_height))


def to_mesh(shape, path_stl, tol=0.02, ang=0.1):
    cq.exporters.export(shape, path_stl, tolerance=tol, angularTolerance=ang)


def volume(w):
    return sum(s.Volume() for s in w.solids().vals())
