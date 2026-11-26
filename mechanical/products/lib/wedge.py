# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""wedge.py - parametric noknok "desk wedge": a PicoHub flat inside, a slanted face carrying modules.

Two printed parts:
  shell  - walls + slanted face plate (cut-outs for the modules, bosses for their M2.5 screws,
           4 corner bosses for the base screws, USB-C power slot and vents in the back wall)
  base   - bottom plate with 4 PicoHub standoffs, 4 countersunk screw holes, feet recesses, vents

Print the shell FACE DOWN (print_pose) - every wall then leans 30 degrees from vertical, so no
support is needed. The base prints flat.
"""
import math
import cadquery as cq
from nk_cad import (box, cyl, union, hex_grille, to_desk, MODULES, PICOHUB, PCB_T,
                    M25_PILOT, M25_CLEAR, M25_HEAD)


class Wedge:
    def __init__(self, layout, W=92.0, D=64.0, HF=20.0, TH=30.0, WALL=1.6, TF=2.0, BP=3.0,
                 hub_y0=15.0, fillet=4.0, vent_x=(-12, -4, 4, 12, 20, 28), jst_ports=()):
        self.layout = layout          # list of (module key, ox, oy): PCB origin in face-local coords
        self.W, self.D, self.HF, self.TH = W, D, HF, TH
        self.WALL, self.TF, self.BP = WALL, TF, BP
        self.hub_y0, self.fillet = hub_y0, fillet
        self.vent_x = vent_x          # x of the vertical vent slots in the back wall
        self.jst_ports = jst_ports    # PicoHub Qwiic ports (board coords) whose cable leaves through the back wall
        self.tan = math.tan(math.radians(TH))
        self.cos = math.cos(math.radians(TH))
        self.sin = math.sin(math.radians(TH))
        self.HB = HF + D * self.tan   # back height

    # ---- plane helpers ---------------------------------------------------------------------
    def zface(self, y):               # outer face height at depth y
        return self.HF + y * self.tan

    def zunder(self, y, skin=None):   # underside of the face plate (skin = thickness measured on the normal)
        return self.zface(y) - (self.TF if skin is None else skin) / self.cos

    def yz_prism(self, pts, half_x):
        return cq.Workplane("YZ").polyline(pts).close().extrude(half_x, both=True)

    # ---- hub -------------------------------------------------------------------------------
    def hub_xy(self, hx, hy):
        """PicoHub board coords -> desk X, Y. Hub is turned 180 degrees: its N edge (Qwiic ports)
        faces the front, its S edge (USB-C power) faces the back wall."""
        return (40.0 - hx, self.hub_y0 + 40.0 - hy)

    def hub_z0(self):                 # underside of the hub PCB
        return self.BP + PICOHUB["cb"]

    # ---- parts -----------------------------------------------------------------------------
    def shell(self):
        W, D, HF, WALL, TF, BP = self.W, self.D, self.HF, self.WALL, self.TF, self.BP
        outer = self.yz_prism([(0, 0), (0, HF), (D, self.HB), (D, 0)], W / 2)
        # round the 4 vertical corners; chamfer (not round) the edge around the slanted face: the shell
        # prints face down and a rounded edge on the bed would overhang by ~2 mm in the first layers
        outer = outer.edges("|Z").fillet(self.fillet)
        face_dir = cq.selectors.DirectionMinMaxSelector(cq.Vector(0, -self.sin, self.cos), True)
        outer = outer.faces(face_dir).chamfer(1.2)
        cav = self.yz_prism([(WALL, -1), (WALL, self.zunder(WALL)), (D - WALL, self.zunder(D - WALL)),
                             (D - WALL, -1)], W / 2 - WALL)
        body = outer.cut(cav)

        # corner bosses for the base screws (limited to stay 0.8 mm under the outer face)
        limit = self.yz_prism([(0, -1), (0, self.zunder(0, 0.8)), (D, self.zunder(D, 0.8)), (D, -1)], W / 2)
        # centres 3.0 from the wall with r 3.2: the boss overlaps the wall by 0.2 mm (a boss exactly tangent to a wall
        # makes a non-manifold edge in the mesh)
        self.base_screws = [(sx * (W / 2 - WALL - 3.0), WALL + 3.0) for sx in (-1, 1)] + [(sx * 38.5, D - WALL - 3.0) for sx in (-1, 1)]
        for (x, y) in self.base_screws:
            boss = cyl(x, y, BP, self.HB, 6.4).intersect(limit)
            boss = boss.cut(cyl(x, y, BP - 0.1, BP + 9.0, M25_PILOT))
            body = body.union(boss)

        # face plate features (local frame, then tilted onto the face)
        adds, cuts = None, None
        for (key, ox, oy) in self.layout:
            m = MODULES[key]
            # bosses under the plate: from the underside down to the PCB top, pilot hole from below
            for (hx, hy) in m["holes"]:
                x, y = ox + hx, oy + hy
                h = m["ct"] + 0.4                       # 0.4 mm into the plate for a solid joint
                boss = cyl(x, y, -TF - m["ct"], -TF + 0.4, 5.8)
                pil = cyl(x, y, -TF - m["ct"] - 0.1, min(-TF - m["ct"] + 6.0, -0.6), M25_PILOT)
                boss = boss.cut(pil)
                adds = boss if adds is None else adds.union(boss)
            kind = m["feature"]
            if kind[0] == "round":
                c = cyl(ox + kind[1], oy + kind[2], -TF - 1, 1, kind[3])
            elif kind[0] == "rect":
                c = box(ox + kind[1] - kind[3] / 2, ox + kind[1] + kind[3] / 2,
                        oy + kind[2] - kind[4] / 2, oy + kind[2] + kind[4] / 2, -TF - 1, 1)
            else:                                        # grille
                c = hex_grille(ox + kind[1], oy + kind[2], -TF - 1, 1, 1.5, 2.2, kind[3] / 2)
            cuts = c if cuts is None else cuts.union(c)
        body = body.union(to_desk(adds, self.TH, self.HF))
        body = body.cut(to_desk(cuts, self.TH, self.HF))

        # back wall: USB-C power slot at the hub's J1, vent slots
        jx, jy = self.hub_xy(*PICOHUB["usb_power"])
        zc = self.hub_z0() + PCB_T + 1.6                # centre of the USB-C mouth
        body = body.cut(box(jx - 7.5, jx + 7.5, D - WALL - 1, D + 1, zc - 4.5, zc + 4.5))
        for x in self.vent_x:
            body = body.cut(box(x - 1.0, x + 1.0, D - WALL - 1, D + 1, BP + 6, BP + 42))   # tall: warm air collects under the face (DEV-146)
        for (px, py) in self.jst_ports:                 # JST-SH cable exits (S edge ports J5/J6 face the back wall)
            x, _ = self.hub_xy(px, py)
            zq = self.hub_z0() + PCB_T + 1.6
            body = body.cut(box(x - 3.8, x + 3.8, D - WALL - 1, D + 1, zq - 2.3, zq + 2.3))
        return body

    def base(self):
        W, D, WALL, BP = self.W, self.D, self.WALL, self.BP
        c = 0.25                                        # clearance to the shell walls
        b = box(-(W / 2 - WALL - c), W / 2 - WALL - c, WALL + c, D - WALL - c, 0, BP)
        for (x, y) in self.base_screws:                  # countersunk screw holes
            b = b.cut(cyl(x, y, -1, BP + 1, M25_CLEAR))
            b = b.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y).circle(M25_HEAD / 2)
                      .workplane(offset=1.62).circle(M25_CLEAR / 2).loft())      # head recess on the BOTTOM face
        # PicoHub standoffs (pilot holes from the top, blind)
        for (hx, hy) in PICOHUB["holes"]:
            x, y = self.hub_xy(hx, hy)
            st = cyl(x, y, BP - 0.1, BP + PICOHUB["cb"], 5.8).cut(cyl(x, y, BP - 1.8, BP + PICOHUB["cb"] + 0.1, M25_PILOT))
            b = b.union(st)
        # feet recesses (self-adhesive rubber feet, d10 x 1.0)
        # 0.5 mm deep: a 1 mm foot then stands 0.5 mm proud and really lifts the case; positions keep clear of the screw heads
        for (x, y) in ((-34, 12), (34, 12), (-30, D - 11), (30, D - 11)):
            b = b.cut(cyl(x, y, -0.1, 0.5, 10.4))
        # vents under the hub
        y0 = self.hub_y0 + 12
        for x in (-30, -22, -14, 14, 22, 30):
            b = b.cut(box(x - 1.25, x + 1.25, y0, y0 + 16, -1, BP + 1))
        return b

    # ---- ghosts for the collision check ------------------------------------------------------
    def ghosts(self):
        g = {}
        W = PICOHUB["w"]
        hx0, hy0 = self.hub_xy(80, 40)                   # hub board spans X [-40,40], Y [hub_y0, hub_y0+40]
        z0 = self.hub_z0()
        g["hub_low"] = box(-40, 40, self.hub_y0, self.hub_y0 + 40, z0 + 0.01, z0 + PCB_T + 5.0)   # PCB + sockets
        xa, ya = self.hub_xy(52.37, 30.46)                                                         # plugged-in Pico 2 W
        xb, yb = self.hub_xy(1.37, 9.46)
        g["hub_pico"] = box(xa, xb, ya, yb, z0 + PCB_T, z0 + PCB_T + PICOHUB["ct"])
        for i, (key, ox, oy) in enumerate(self.layout):
            m = MODULES[key]
            z_top = -self.TF - m["ct"]
            slab = box(ox, ox + m["w"], oy, oy + m["h"], z_top - PCB_T - m["cb"], z_top)
            g["%s_%d" % (key, i)] = to_desk(slab, self.TH, self.HF)
        return g
