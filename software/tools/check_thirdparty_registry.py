#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-SA-4.0
# Copyright 2026 noknok (Christopher Houben)
"""check_thirdparty_registry.py - DEV-251: keep thirdparty-boards.json, the manifest schema and the
brain library noknok_thirdparty in sync. Standard library only; the library is READ as text (ast),
never imported or run.

  python software/tools/check_thirdparty_registry.py [--lib DIR] [--registry FILE] [--schema FILE]

--lib DIR  folder holding noknok_thirdparty.py and noknok_tp_<type>.py (brain-Pico software/lib once
           DEV-248 has landed). Default: first of ../brain-Pico/software/lib, ../brain-Pico/software next
           to this repo. Without a library the registry <-> schema part still runs and the library part
           is skipped with a warning (exit 0); pass --require-lib to make that an error.

Checks: (1) schema definitions.thirdPartyType.enum == registry boards; (2) every board has addresses,
name and identification; (3) library REGISTRY types == registry boards, per type the driver file exists,
its ADDRESSES equal the registry addresses and its PULLUP_REMOVABLE equals pullups.removable.
Exit 0 = in sync, 1 = drift, 2 = cannot run.
"""
import argparse, ast, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))


def hexaddrs(lst):
    return sorted(int(a, 16) for a in lst)


def _value(node):
    """ast.literal_eval, plus tuple(range(a, b)) / list(range(a, b)) with constant arguments."""
    try:
        return ast.literal_eval(node)
    except ValueError:
        pass
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("tuple", "list")
            and len(node.args) == 1 and isinstance(node.args[0], ast.Call)
            and isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == "range"):
        try:
            return tuple(range(*[ast.literal_eval(a) for a in node.args[0].args]))
        except ValueError:
            return None
    return None


def literal(tree, name):
    """Module-level NAME = <literal> in an ast tree, or None."""
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return _value(n.value)
    return None


def class_attr(tree, name):
    for c in tree.body:
        if isinstance(c, ast.ClassDef):
            for n in c.body:
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
                    return _value(n.value)
    return None


def check(registry_path, schema_path, lib, require_lib):
    errors, warnings = [], []
    reg = json.load(open(registry_path, encoding="utf-8"))
    boards = reg.get("boards", {})
    schema = json.load(open(schema_path, encoding="utf-8"))
    enum = schema.get("definitions", {}).get("thirdPartyType", {}).get("enum", [])
    if sorted(enum) != sorted(boards):
        errors.append("schema thirdPartyType %s != registry boards %s" % (sorted(enum), sorted(boards)))
    for t, b in boards.items():
        for k in ("name", "addresses", "identification", "pullups", "capabilities"):
            if k not in b:
                errors.append("registry %s: missing %r" % (t, k))
    if not lib:
        (errors if require_lib else warnings).append("no library folder found: library part skipped (DEV-248)")
        return errors, warnings
    core = os.path.join(lib, "noknok_thirdparty.py")
    if not os.path.isfile(core):
        (errors if require_lib else warnings).append("%s not found: library part skipped" % core)
        return errors, warnings
    lreg = literal(ast.parse(open(core, encoding="utf-8").read()), "REGISTRY") or ()
    ltypes = {t: addrs for t, addrs, _auto in lreg}
    if sorted(ltypes) != sorted(boards):
        errors.append("library REGISTRY types %s != registry boards %s" % (sorted(ltypes), sorted(boards)))
    for t, b in boards.items():
        want = hexaddrs(b.get("addresses", []))
        if t in ltypes and sorted(ltypes[t]) != want:
            errors.append("%s: library REGISTRY addresses %s != registry %s" % (
                t, [hex(a) for a in sorted(ltypes[t])], [hex(a) for a in want]))
        drv = os.path.join(lib, "noknok_tp_%s.py" % t)
        if not os.path.isfile(drv):
            errors.append("%s: driver file noknok_tp_%s.py missing in the library" % (t, t))
            continue
        tree = ast.parse(open(drv, encoding="utf-8").read())
        got = class_attr(tree, "ADDRESSES")
        if got is None or sorted(got) != want:
            errors.append("%s: driver ADDRESSES %s != registry %s" % (
                t, None if got is None else [hex(a) for a in sorted(got)], [hex(a) for a in want]))
        rem = class_attr(tree, "PULLUP_REMOVABLE")
        if rem is not None and bool(rem) != bool(b.get("pullups", {}).get("removable")):
            errors.append("%s: driver PULLUP_REMOVABLE %s != registry pullups.removable %s" % (
                t, rem, b.get("pullups", {}).get("removable")))
    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lib")
    ap.add_argument("--registry", default=os.path.join(ROOT, "software", "thirdparty-boards.json"))
    ap.add_argument("--schema", default=os.path.join(ROOT, "software", "product-manifest.schema.json"))
    ap.add_argument("--require-lib", action="store_true")
    a = ap.parse_args()
    lib = a.lib
    if not lib:
        for c in ("../brain-Pico/software/lib", "../brain-Pico/software"):
            p = os.path.normpath(os.path.join(ROOT, c))
            if os.path.isfile(os.path.join(p, "noknok_thirdparty.py")):
                lib = p
                break
    try:
        errors, warnings = check(a.registry, a.schema, lib, a.require_lib)
    except (OSError, ValueError) as e:
        print("cannot run: %s" % e)
        return 2
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("DRIFT:", e)
    print("thirdparty registry: %s" % ("IN SYNC" if not errors else "%d problem(s)" % len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
