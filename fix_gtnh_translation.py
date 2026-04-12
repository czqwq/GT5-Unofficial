#!/usr/bin/env python3
"""
fix_gtnh_translation.py
-----------------------
GTNH Translation-of-GTNH 汉化修复脚本

功能：
  1. 对比 en_US.lang 与 resources/zh_CN.lang + GregTech_zh_CN.lang(cfg)
  2. 将 resources/zh_CN.lang 中已确认重命名的废弃 key 替换为新 key
  3. 将旧的 gt.component.* key 替换为新的 gt.oreprefix.* key
  4. 输出完整差异报告（missing / stale / renamed）

使用方法：
  python3 fix_gtnh_translation.py \\
    --en      en_US.lang \\
    --res     "resources/GregTech(+16)[gregtech]/lang/zh_CN.lang" \\
    --cfg     GregTech.lang \\
    --out-res zh_CN.lang.fixed \\
    --out-cfg GregTech.lang.fixed \\
    --report  report.txt

依赖：Python 3.8+，无额外依赖
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Key rename table: stale_key → new_key  (None means key was removed)
# ---------------------------------------------------------------------------
RESOURCE_RENAMES = {
    # GT5U.item renames
    "GT5U.item.cable.eu_volt":         "GT5U.item.cable.loss.eu_volt",
    "GT5U.item.cable.swapped":         "GT5U.item.cable.swapped.s",
    "GT5U.item.pipe.swap":             "GT5U.item.pipe.swap.s",

    # GT5U.machines renames
    "GT5U.machines.workareaset":       "GT5U.machines.workareaset.s",

    # GT5U.infodata renames
    "GT5U.infodata.purification_plant.linked_units.status.online":
        "GT5U.infodata.purification_plant.linked_units.status.active",

    # GT5U.gui renames
    "GT5U.gui.button.drone_error":       "GT5U.gui.button.drone_status",
    "GT5U.gui.button.drone_showLocalName": "GT5U.gui.button.drone_searchoriname",
    "GT5U.gui.button.drone_outofrange":  None,   # removed
    "GT5U.gui.config.worldgen.end_asteroids": None,   # removed

    # GT5U.MBTT removals
    "GT5U.MBTT.HatchDots":             None,
    "GT5U.MBTT.Structure.Complex":     None,

    # GT5U machine mode removals
    "GT5U.MULTI_CANNER.mode.0":        None,
    "GT5U.MULTI_CANNER.mode.1":        None,
    "GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.0": None,
    "GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.1": None,

    # GT5U.machines removals
    "GT5U.machines.separatebus":       None,

    # gt.recipe renames/removals
    "gt.recipe.macerator_pulverizer":             None,
    "gt.recipe.macerator_pulverizer.description": None,
    "gt.recipe.slicer":                           None,
    "gt.recipe.slicer.description":               None,

    # gt.tileentity
    "gt.tileentity.energy_container_block.name":  None,
    "gt.tileentity.digital_chest.name":           None,
}

# ---------------------------------------------------------------------------
# gt.component.* → gt.oreprefix.* rename table (all 24 entries)
# ---------------------------------------------------------------------------
OREPREFIX_RENAMES = {
    "gt.component.dust":          "gt.oreprefix.material_dust",
    "gt.component.dustsmall":     "gt.oreprefix.small_pile_of_material_dust",
    "gt.component.dusttiny":      "gt.oreprefix.tiny_pile_of_material_dust",
    "gt.component.ingot":         "gt.oreprefix.material_ingot",
    "gt.component.hotingot":      "gt.oreprefix.hot_material_ingot",
    "gt.component.plate":         "gt.oreprefix.material_plate",
    "gt.component.platedouble":   "gt.oreprefix.double_material_plate",
    "gt.component.rod":           "gt.oreprefix.material_rod",
    "gt.component.rodlong":       "gt.oreprefix.long_material_rod",
    "gt.component.gear":          "gt.oreprefix.material_gear",
    "gt.component.smallgear":     "gt.oreprefix.small_material_gear",
    "gt.component.screw":         "gt.oreprefix.material_screw",
    "gt.component.bolt":          "gt.oreprefix.material_bolt",
    "gt.component.rotor":         "gt.oreprefix.material_rotor",
    "gt.component.ring":          "gt.oreprefix.material_ring",
    "gt.component.foil":          "gt.oreprefix.material_foil",
    "gt.component.plasmacell":    "gt.oreprefix.material_plasma_cell",
    "gt.component.cell":          "gt.oreprefix.material_cell",
    "gt.component.nugget":        "gt.oreprefix.material_nugget",
    "gt.component.spring":        "gt.oreprefix.material_spring",
    "gt.component.smallspring":   "gt.oreprefix.small_material_spring",
    "gt.component.finewire":      "gt.oreprefix.fine_material_wire",
    "gt.component.platedense":    "gt.oreprefix.dense_material_plate",
    "gt.component.platesuperdense": "gt.oreprefix.superdense_material_plate",
}


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_lang(path: Path):
    """Parse a standard .lang file, preserving order, comments, and blank lines."""
    lines = []
    kv = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            raw = line.rstrip("\n")
            lines.append(raw)
            stripped = raw.strip()
            if stripped.startswith("#") or "=" not in stripped or not stripped:
                continue
            k, _, v = stripped.partition("=")
            k = k.strip()
            if k:
                kv[k] = v
    return lines, kv


def parse_cfg_lang(path: Path):
    """Parse a Forge-cfg-style lang file (GregTech.lang / GregTech_zh_CN.lang)."""
    lines = []
    kv = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            raw = line.rstrip("\n")
            lines.append(raw)
            m = re.match(r'\s+S:"?([^"=\n]+?)"?\s*=\s*(.*)', raw)
            if m:
                k = m.group(1).strip()
                v = m.group(2).strip()
                if k:
                    kv[k] = v
    return lines, kv


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def fix_resource_lang(lines, kv, en_kv, all_renames, report_lines):
    """
    Apply renames to resources/zh_CN.lang lines.
    Returns new lines list.
    """
    new_lines = []
    renamed_count = 0
    removed_count = 0
    oreprefix_count = 0

    for raw in lines:
        stripped = raw.strip()
        # Not a key=value line
        if stripped.startswith("#") or "=" not in stripped or not stripped:
            new_lines.append(raw)
            continue

        k, _, v = stripped.partition("=")
        k = k.strip()

        # Apply gt.component.* → gt.oreprefix.* renames
        if k in OREPREFIX_RENAMES:
            new_k = OREPREFIX_RENAMES[k]
            indent = raw[: len(raw) - len(raw.lstrip())]
            new_lines.append(f"{indent}{new_k}={v}")
            report_lines.append(f"[OREPREFIX RENAME] {k} → {new_k}  (zh: {v})")
            oreprefix_count += 1
            continue

        # Apply GT5U / gt.recipe renames
        if k in all_renames:
            new_k = all_renames[k]
            if new_k is None:
                # Remove stale key (commented out)
                indent = raw[: len(raw) - len(raw.lstrip())]
                new_lines.append(f"#{indent}{k}={v}  # REMOVED (key no longer exists in en_US)")
                report_lines.append(f"[STALE REMOVED]  {k} = {v}")
                removed_count += 1
            else:
                indent = raw[: len(raw) - len(raw.lstrip())]
                en_new = en_kv.get(new_k, "[NOT IN EN_US]")
                new_lines.append(f"{indent}{new_k}={v}")
                report_lines.append(
                    f"[RENAMED]  {k} → {new_k}"
                    f"\n            zh: {v}"
                    f"\n            en: {en_new}"
                )
                renamed_count += 1
            continue

        new_lines.append(raw)

    report_lines.append(
        f"\n[resources/zh_CN.lang] Renames applied: {renamed_count}, "
        f"Stale removed: {removed_count}, oreprefix renames: {oreprefix_count}"
    )
    return new_lines


def fix_cfg_lang(lines, cfg_kv, en_kv, report_lines):
    """
    GregTech.lang cfg file currently has no known bad renames.
    This function just checks for stale keys and reports them.
    We do NOT modify the cfg file automatically (it's huge and format-sensitive).
    """
    en_keys = set(en_kv.keys())
    cfg_keys = set(cfg_kv.keys())

    # Check: how many en_US machine/casing keys are NOT in cfg (need to be added)
    missing_bm = sorted(
        k for k in en_keys if k.startswith("gt.blockmachines.") and k not in cfg_keys
    )
    missing_bc = sorted(
        k for k in en_keys if ("casings" in k or "foundry" in k) and k not in cfg_keys
    )

    report_lines.append(f"\n[GregTech.lang cfg] machine keys missing: {len(missing_bm)}")
    report_lines.append(f"[GregTech.lang cfg] casing keys missing:  {len(missing_bc)}")

    report_lines.append("\n=== Machines missing from GregTech.lang (need translation, add to cfg) ===")
    for k in missing_bm[:80]:
        report_lines.append(f"  {k} = {en_kv[k]}")
    if len(missing_bm) > 80:
        report_lines.append(f"  ... and {len(missing_bm)-80} more")

    report_lines.append("\n=== Casings/foundry missing from GregTech.lang ===")
    for k in missing_bc:
        report_lines.append(f"  {k} = {en_kv[k]}")

    return lines  # cfg not modified


def generate_full_report(en_kv, res_kv, cfg_kv, report_lines):
    """Generate comprehensive diff report."""
    en_keys  = set(en_kv.keys())
    res_keys = set(res_kv.keys())
    cfg_keys = set(cfg_kv.keys())

    missing_from_res = en_keys - res_keys
    completely_missing = missing_from_res - cfg_keys
    stale_in_res = res_keys - en_keys

    from collections import Counter
    cats_complete = Counter()
    for k in completely_missing:
        parts = k.split(".")
        cats_complete[parts[0] + "." + parts[1] if len(parts) >= 2 else parts[0]] += 1

    report_lines.append("\n" + "=" * 70)
    report_lines.append("FULL DIFF REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"en_US.lang total keys:                {len(en_keys)}")
    report_lines.append(f"resources/zh_CN.lang total keys:      {len(res_keys)}")
    report_lines.append(f"GregTech_zh_CN.lang (cfg) total keys: {len(cfg_keys)}")
    report_lines.append(f"Missing from resources (en has, res lacks): {len(missing_from_res)}")
    report_lines.append(f"  - covered by cfg (works via cfg):   {len(missing_from_res & cfg_keys)}")
    report_lines.append(f"  - COMPLETELY MISSING (no translation): {len(completely_missing)}")
    report_lines.append(f"Stale in resources (dead keys):       {len(stale_in_res)}")

    report_lines.append("\n--- Completely missing by category ---")
    for cat, n in sorted(cats_complete.items(), key=lambda x: -x[1]):
        report_lines.append(f"  {cat:<55} {n:>4}")

    report_lines.append("\n--- Stale keys in resources/zh_CN.lang ---")
    for k in sorted(stale_in_res):
        report_lines.append(f"  [STALE] {k} = {res_kv[k]}")

    report_lines.append("\n--- Completely missing keys (need new translation) ---")
    for k in sorted(completely_missing):
        report_lines.append(f"  [MISSING] {k} = {en_kv[k]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fix GTNH translation key mismatches")
    parser.add_argument("--en",      required=True, help="Path to en_US.lang")
    parser.add_argument("--res",     required=True, help="Path to resources/zh_CN.lang")
    parser.add_argument("--cfg",     required=True, help="Path to GregTech.lang (cfg format)")
    parser.add_argument("--out-res", default=None,  help="Output path for fixed zh_CN.lang (default: overwrite)")
    parser.add_argument("--out-cfg", default=None,  help="Output path for cfg report (default: print only)")
    parser.add_argument("--report",  default="translation_report.txt", help="Report output file")
    parser.add_argument("--dry-run", action="store_true", help="Only print report, don't write files")
    args = parser.parse_args()

    en_path  = Path(args.en)
    res_path = Path(args.res)
    cfg_path = Path(args.cfg)

    for p in [en_path, res_path, cfg_path]:
        if not p.exists():
            print(f"ERROR: File not found: {p}", file=sys.stderr)
            sys.exit(1)

    print(f"Parsing en_US.lang: {en_path}")
    _, en_kv = parse_lang(en_path)

    print(f"Parsing resources zh_CN.lang: {res_path}")
    res_lines, res_kv = parse_lang(res_path)

    print(f"Parsing GregTech.lang (cfg): {cfg_path}")
    cfg_lines, cfg_kv = parse_cfg_lang(cfg_path)

    report_lines = []
    all_renames = {**RESOURCE_RENAMES}

    # Fix resources/zh_CN.lang
    print("Applying fixes to resources/zh_CN.lang ...")
    new_res_lines = fix_resource_lang(res_lines, res_kv, en_kv, all_renames, report_lines)

    # Analyze cfg
    print("Analyzing GregTech.lang (cfg) ...")
    fix_cfg_lang(cfg_lines, cfg_kv, en_kv, report_lines)

    # Generate full report (uses ORIGINAL kv before fixes for accurate stale count)
    generate_full_report(en_kv, res_kv, cfg_kv, report_lines)

    # Write outputs
    report_path = Path(args.report)
    report_text = "\n".join(report_lines)

    if not args.dry_run:
        out_res = Path(args.out_res) if args.out_res else res_path
        with open(out_res, "w", encoding="utf-8") as f:
            f.write("\n".join(new_res_lines))
            if new_res_lines and new_res_lines[-1] != "":
                f.write("\n")
        print(f"Written fixed resources lang: {out_res}")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Written report: {report_path}")
    else:
        print("\n--- DRY RUN REPORT ---")
        print(report_text[:5000])
        print(f"\n(Full report would be {len(report_text)} chars)")

    # Print summary
    renamed = sum(1 for l in report_lines if l.startswith("[RENAMED]") or l.startswith("[OREPREFIX RENAME]"))
    removed = sum(1 for l in report_lines if l.startswith("[STALE REMOVED]"))
    print(f"\nSummary: {renamed} keys renamed, {removed} stale keys commented out")


if __name__ == "__main__":
    main()
