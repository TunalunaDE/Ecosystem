# SPDX-License-Identifier: MIT
# Copyright 2026 noknok (Christopher Houben)
"""check_print.py - quick printability check of the STL files (they are already in print pose).

    python lib/check_print.py            # all STL in focus-timer/out and quiz-buzzers/out

Reports per file: watertight, bounding box, and the area of downward-facing surfaces that lean more than
45 degrees from vertical (overhang) and sit above the bed (z > 0.1). Overhang area is reported in total and
the largest connected patches (area, size, height) are listed so a bridge can be told from a real problem.
"""
import glob, os, sys
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
LIMIT = 45.0       # degrees from vertical; a face normal pointing down by more than this is an overhang


def check(path):
    m = trimesh.load(path)
    n = m.face_normals
    ang = np.degrees(np.arccos(np.clip(-n[:, 2], -1, 1)))          # angle between face normal and straight down
    zmin = m.triangles[:, :, 2].min(axis=1)
    # overhang: normal points down more than (90-LIMIT) from the horizontal, i.e. ang < 90 - LIMIT ... but ang is measured from DOWN
    over = (ang < 90.0 - LIMIT) & (zmin > 0.1)
    area = m.area_faces[over].sum()
    print("%-38s watertight=%s  bbox=%s  overhang>45deg: %.1f mm2" % (
        os.path.basename(path), m.is_watertight, np.round(m.extents, 1), area))
    if area > 0:
        sub = m.submesh([np.where(over)[0]], append=False)
        comps = sub[0].split(only_watertight=False) if hasattr(sub[0], "split") else []
        rows = sorted(((c.area, c.bounds) for c in comps), key=lambda r: -r[0])[:6]
        for a, b in rows:
            print("      patch %.1f mm2  size %s  z %.1f-%.1f" % (a, np.round(b[1] - b[0], 1), b[0][2], b[1][2]))


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "..", "*", "out", "*.stl")))
    for f in files:
        if os.path.basename(f).startswith("_"):
            continue
        check(f)
