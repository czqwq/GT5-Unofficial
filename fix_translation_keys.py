#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTNH 汉化仓库 Key 一键修复脚本
============================
用法: 在 Translation-of-GTNH 仓库根目录下运行
    python3 fix_translation_keys.py [--dry-run] [--report report.txt]

参数:
    --dry-run    只检测问题，不修改文件，仅输出报告
    --report     指定报告输出文件路径（默认: fix_report.txt）

功能:
    1. 自动将旧 key 重命名为新 key（保留现有中文翻译）
    2. 用英文原文填充缺失的新 key（标记 # TODO: 待翻译）
    3. 将纯废弃 key（无对应新 key）注释掉
    4. 生成详细修改报告

支持的模组:
    bartworks, detravscannermod, ggfab, goodgenerator, gregtech,
    gtneioreplugin, gtnhintergalactic, gtnhlanth, ic2, kekztech,
    kubatech, miscutils, spiceoflife, stevescarts, tectech

源码: https://github.com/czqwq/GT5-Unofficial
汉化: https://github.com/Kiwi233/Translation-of-GTNH
"""

import os
import sys
import re
import argparse
from collections import OrderedDict
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# 重命名规则定义
# 格式: (旧 key, 新 key)  — 旧 key 的翻译值会被保留并写入新 key
# ──────────────────────────────────────────────────────────────────────────────

RENAMES = {
    "gregtech": [
        # gt.component.* → gt.oreprefix.*  （核心修复，解决 BlackMetal 螺栓等问题）
        ("gt.component.dust",              "gt.oreprefix.material_dust"),
        ("gt.component.dustsmall",         "gt.oreprefix.small_pile_of_material_dust"),
        ("gt.component.dusttiny",          "gt.oreprefix.tiny_pile_of_material_dust"),
        ("gt.component.ingot",             "gt.oreprefix.material_ingot"),
        ("gt.component.hotingot",          "gt.oreprefix.hot_material_ingot"),
        ("gt.component.plate",             "gt.oreprefix.material_plate"),
        ("gt.component.platedouble",       "gt.oreprefix.double_material_plate"),
        ("gt.component.rod",               "gt.oreprefix.material_rod"),
        ("gt.component.rodlong",           "gt.oreprefix.long_material_rod"),
        ("gt.component.gear",              "gt.oreprefix.material_gear"),
        ("gt.component.smallgear",         "gt.oreprefix.small_material_gear"),
        ("gt.component.screw",             "gt.oreprefix.material_screw"),
        ("gt.component.bolt",              "gt.oreprefix.material_bolt"),
        ("gt.component.rotor",             "gt.oreprefix.material_rotor"),
        ("gt.component.ring",              "gt.oreprefix.material_ring"),
        ("gt.component.foil",              "gt.oreprefix.material_foil"),
        ("gt.component.plasmacell",        "gt.oreprefix.material_plasma_cell"),
        ("gt.component.cell",              "gt.oreprefix.material_cell"),
        ("gt.component.nugget",            "gt.oreprefix.material_nugget"),
        ("gt.component.spring",            "gt.oreprefix.material_spring"),
        ("gt.component.smallspring",       "gt.oreprefix.small_material_spring"),
        ("gt.component.finewire",          "gt.oreprefix.fine_material_wire"),
        ("gt.component.platedense",        "gt.oreprefix.dense_material_plate"),
        ("gt.component.platesuperdense",   "gt.oreprefix.superdense_material_plate"),
        # GT5U.* key 改名
        ("GT5U.item.cable.eu_volt",                                "GT5U.item.cable.loss.eu_volt"),
        ("GT5U.item.cable.swapped",                                "GT5U.item.cable.swapped.s"),
        ("GT5U.item.pipe.swap",                                    "GT5U.item.pipe.swap.s"),
        ("GT5U.machines.workareaset",                              "GT5U.machines.workareaset.s"),
        ("GT5U.gui.button.drone_error",                            "GT5U.gui.button.drone_status"),
        ("GT5U.gui.button.drone_showLocalName",                    "GT5U.gui.button.drone_showLocalName.s"),
        ("GT5U.gui.button.drone_outofrange",                       "GT5U.gui.button.drone_outofrange.s"),
        ("GT5U.gui.config.worldgen.end_asteroids",                 None),  # 已删除
        ("GT5U.gui.text.insufficient",                             "GT5U.gui.text.generator_structure_incomplete"),
        ("GT5U.infodata.purification_plant.linked_units.status.online", "GT5U.infodata.purification_plant.linked_units.status.active"),
        ("GT5U.machines.advdebugstructurewriter.gui.highlight.tooltip", None),  # 已删除
        ("GT5U.machines.advdebugstructurewriter.gui.origin",       None),
        ("GT5U.machines.advdebugstructurewriter.gui.print.tooltip", None),
        ("GT5U.machines.advdebugstructurewriter.gui.size",         None),
        ("GT5U.machines.advdebugstructurewriter.gui.transpose.tooltip", None),
        ("GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.0",                 None),  # 机器已删除
        ("GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.1",                 None),
        ("GT5U.MBTT.HatchDots",                                    None),  # 格式变更，无直接替代
        ("GT5U.MBTT.Structure.Complex",                            None),  # 已删除
        ("GT5U.MULTI_CANNER.mode.0",                               None),  # 机器已删除
        ("GT5U.MULTI_CANNER.mode.1",                               None),
    ],
    "gtneioreplugin": [
        # gtnop.world.* 首字母大写 → 全小写
        ("gtnop.world.Anubis",      "gtnop.world.anubis"),
        ("gtnop.world.Asteroids",   "gtnop.world.asteroids"),
        ("gtnop.world.BarnardC",    "gtnop.world.barnarda2"),
        ("gtnop.world.BarnardE",    "gtnop.world.barnarda4"),
        ("gtnop.world.BarnardF",    "gtnop.world.barnarda5"),
        ("gtnop.world.Callisto",    "gtnop.world.callisto"),
        ("gtnop.world.CentauriA",   "gtnop.world.centauribb"),
        ("gtnop.world.Ceres",       "gtnop.world.ceres"),
        ("gtnop.world.Deimos",      "gtnop.world.deimos"),
        ("gtnop.world.Enceladus",   "gtnop.world.enceladus"),
        ("gtnop.world.Europa",      "gtnop.world.europa"),
        ("gtnop.world.Ganymede",    "gtnop.world.ganymed"),
        ("gtnop.world.Haumea",      "gtnop.world.haumea"),
        ("gtnop.world.Horus",       "gtnop.world.horus"),
        ("gtnop.world.Io",          "gtnop.world.iojupiter"),
        ("gtnop.world.Kuiperbelt",  "gtnop.world.kuiperbelt"),
        ("gtnop.world.Maahes",      "gtnop.world.maahes"),
        ("gtnop.world.MakeMake",    "gtnop.world.makemake"),
        ("gtnop.world.Mars",        "gtnop.world.mars"),
        ("gtnop.world.MehenBelt",   "gtnop.world.asteroidbeltmehen"),
        ("gtnop.world.Mercury",     "gtnop.world.mercury"),
        ("gtnop.world.Miranda",     "gtnop.world.miranda"),
        ("gtnop.world.Moon",        "gtnop.world.moon"),
        ("gtnop.world.Neper",       "gtnop.world.neper"),
        ("gtnop.world.Oberon",      "gtnop.world.oberon"),
        ("gtnop.world.Phobos",      "gtnop.world.phobos"),
        ("gtnop.world.Pluto",       "gtnop.world.pluto"),
        ("gtnop.world.Proteus",     "gtnop.world.proteus"),
        ("gtnop.world.Ross128b",    "gtnop.world.ross128b"),
        ("gtnop.world.Ross128ba",   "gtnop.world.ross128ba"),
        ("gtnop.world.Seth",        "gtnop.world.seth"),
        ("gtnop.world.TcetiE",      "gtnop.world.tcetie"),
        ("gtnop.world.Titan",       "gtnop.world.titan"),
        ("gtnop.world.Triton",      "gtnop.world.triton"),
        ("gtnop.world.Twilight",    "gtnop.world.TwilightForest"),
        ("gtnop.world.VegaB",       "gtnop.world.vega1"),
        ("gtnop.world.Venus",       "gtnop.world.venus"),
    ],
    "gtnhintergalactic": [
        # 提示方块描述格式改变：WithXDot → WithHintNumberX
        ("ig.elevator.structure.AnyBaseCasingWith1Dot", "ig.elevator.structure.AnyBaseCasingWithHintNumber1"),
        ("ig.elevator.structure.AnyBaseCasingWith2Dot", "ig.elevator.structure.AnyBaseCasingWithHintNumber2"),
        ("ig.elevator.structure.AnyBaseCasingWith3Dot", "ig.elevator.structure.AnyBaseCasingWithHintNumber3"),
    ],
    "gtnhlanth": [
        # 提示方块格式改变
        ("gtnhlanth.tt.hintdot",    "gtnhlanth.tt.hintNumber"),
        ("beamline.particleinput",  None),  # 已删除
    ],
    "ggfab": [
        # typo 修复: busses → buses
        ("ggfab.gui.advassline.shutdown.input_busses", "ggfab.gui.advassline.shutdown.input_buses"),
        ("ggfab.recipe.toolcast", None),  # 配方分类已删除
    ],
    "miscutils": [
        # typo 修复: Busses → Buses
        ("interaction.separateBusses.enabled",  "interaction.separateBuses.enabled"),
        ("interaction.separateBusses.disabled", "interaction.separateBuses.disabled"),
        # 已删除的物品（GT++ 农业系统移除）
        ("item.FertileManureSlurry.name",        None),
        ("item.Fertiliser.name",                 None),
        ("item.ManureSlurry.name",               None),
        ("item.RawWaste.name",                   None),
        ("item.UN18Fertiliser.name",             None),
        ("item.UN32Fertiliser.name",             None),
        ("item.itemDustManureByproducts.name",   None),
        ("item.itemDustSmallDirt.name",          None),
        ("item.itemDustSmallManureByproducts.name", None),
        ("item.itemDustSmallUN18Fertiliser.name", None),
        ("item.itemDustSmallUN32Fertiliser.name", None),
        ("item.itemDustTinyManureByproducts.name", None),
        ("item.itemDustTinyUN18Fertiliser.name", None),
        ("item.itemDustTinyUN32Fertiliser.name", None),
        ("item.itemDustUN18Fertiliser.name",     None),
        ("item.itemDustUN32Fertiliser.name",     None),
        ("item.BasicGenericChemItem.29.name",    None),
        ("item.BasicGenericChemItem.30.name",    None),
        ("item.BasicGenericChemItem.31.name",    None),
        ("item.BasicGenericChemItem.32.name",    None),
        ("tile.blockPestKiller.name",            None),
        ("tile.blockPooCollector.0.name",        None),
        ("tile.blockPooCollector.8.name",        None),
        ("tile.blockPooCollector.name",          None),
        ("tile.blockProjectBench.name",          None),
        ("container.pestkiller",                 None),
        ("misc.BatchModeTextOff",                None),
        ("misc.BatchModeTextOn",                 None),
        ("gtpp.gui.crop_harvestor.tooltip.water", None),
        ("gtpp.infodata.multi_block.total_time", None),
        ("gtpp.infodata.multi_block.total_time.0", None),
        ("gtpp.infodata.multi_block.total_time.in_ticks", None),
    ],
    "tectech": [
        # 拼写/命名修复
        ("gt.3blockcasingsTT.2.name",                        "gt.blockcasingsTT.2.name"),
        # 多行 desc 合并为单行 desc
        ("gt.blockmachines.hatch.dynamomulti.desc.0",        "gt.blockmachines.hatch.dynamomulti.desc"),
        ("gt.blockmachines.hatch.dynamomulti.desc.1",        None),
        ("gt.blockmachines.hatch.energymulti.desc.0",        "gt.blockmachines.hatch.energymulti.desc"),
        ("gt.blockmachines.hatch.energymulti.desc.1",        None),
        ("gt.blockmachines.hatch.energymulti.desc.2",        None),
        ("gt.blockmachines.hatch.energymulti.desc.3",        None),
        ("gt.blockmachines.hatch.dynamotunnel.desc.0",       "gt.blockmachines.hatch.dynamotunnel.desc"),
        ("gt.blockmachines.hatch.dynamotunnel.desc.1",       None),
        ("gt.blockmachines.hatch.energytunnel.desc.0",       "gt.blockmachines.hatch.energytunnel.desc"),
        ("gt.blockmachines.hatch.energytunnel.desc.1",       None),
        # Debug 结构打印机已移至 gregtech 主模组（key 相同，这里只是删除 tectech 中的重复）
        ("gt.blockmachines.debug.tt.writer.name",            None),
        ("gt.blockmachines.debug.tt.writer.desc.0",         None),
        ("gt.blockmachines.debug.tt.writer.desc.1",         None),
        ("gt.blockmachines.debug.tt.writer.desc.2",         None),
        # 老版激光仓系列（dynamotunnel2-7 / energytunnel2-7）已重构，tier.XX.name 全部废弃
        # 共 46 条，通过 stale_prefixes 处理（见下方 STALE_PREFIXES）
    ],
    "bartworks": [
        # 旧版 HTGR 相关 key 已迁移到 kubatech，在 bartworks 中废弃
        ("BW.infoData.htgr.coolant",            None),
        ("BW.infoData.htgr.fuel_amount",         None),
        ("BW.infoData.htgr.fuel_type",           None),
        ("BW.infoData.htgr.fuel_type.none",      None),
        ("BW.infoData.htgr.fuel_type.triso",     None),
        ("BW.infoData.htgr.mode",                None),
        ("BW.infoData.htgr.mode.emptying",       None),
        ("BW.infoData.htgr.mode.normal",         None),
        ("BW.infoData.htgr.progress",            None),
        ("misc.BatchModeTextOff",                None),
        ("misc.BatchModeTextOn",                 None),
        ("tooltip.bw.high_temp_gas_cooled_reactor.material", None),
        ("tooltip.bw.item.circuit.imprint",      None),
        ("tooltip.bw.item.circuit.sliced",       None),
        ("tooltip.bw.item.circuit.tagged",       None),
    ],
}

# 通过前缀批量废弃的 key（整个前缀下的 key 全部废弃）
STALE_PREFIXES = {
    "tectech": [
        "gt.blockmachines.hatch.dynamotunnel2.tier.",
        "gt.blockmachines.hatch.dynamotunnel3.tier.",
        "gt.blockmachines.hatch.dynamotunnel4.tier.",
        "gt.blockmachines.hatch.dynamotunnel5.tier.",
        "gt.blockmachines.hatch.dynamotunnel6.tier.",
        "gt.blockmachines.hatch.dynamotunnel7.tier.",
        "gt.blockmachines.hatch.energytunnel2.tier.",
        "gt.blockmachines.hatch.energytunnel3.tier.",
        "gt.blockmachines.hatch.energytunnel4.tier.",
        "gt.blockmachines.hatch.energytunnel5.tier.",
        "gt.blockmachines.hatch.energytunnel6.tier.",
        "gt.blockmachines.hatch.energytunnel7.tier.",
    ],
}

# 翻译文件路径模板
TRANS_PATH_TEMPLATE = "resources/GregTech(+16)[{mod}]/lang/zh_CN.lang"

# 英文原版 lang 文件路径（用于获取新 key 的英文原文填充缺失翻译）
# 这些文件来自 GT5-Unofficial 的 src/main/resources/assets/
# 如果你在本地有 GT5-Unofficial 仓库，可以指定路径
EN_LANG_BASE = None  # 设置为 GT5-Unofficial/src/main/resources/assets 路径可启用英文填充


def parse_lang_file(path):
    """解析 .lang 文件，返回有序字典和原始行列表"""
    lines = []
    kv = OrderedDict()
    if not os.path.exists(path):
        return lines, kv
    with open(path, encoding="utf-8", errors="replace") as f:
        raw_lines = f.readlines()
    for line in raw_lines:
        stripped = line.rstrip("\n")
        lines.append(stripped)
        s = stripped.strip()
        if s and not s.startswith("#") and "=" in s:
            k, _, v = s.partition("=")
            kv[k.strip()] = v.strip()
    return lines, kv


def parse_en_lang(mod):
    """尝试读取英文原版 lang 文件"""
    if EN_LANG_BASE is None:
        return {}
    p = os.path.join(EN_LANG_BASE, mod, "lang", "en_US.lang")
    _, kv = parse_lang_file(p)
    return kv


def apply_fixes(mod, lines, kv, renames, stale_prefixes, en_kv, dry_run, report_lines):
    """对单个模组的 lang 文件应用修复"""
    stats = {"renamed": 0, "commented_out": 0, "already_new": 0, "added": 0}

    # 建立 rename 映射：old_key → new_key
    rename_map = {}
    delete_set = set()
    for old, new in renames:
        if new is None:
            delete_set.add(old)
        else:
            rename_map[old] = new

    # 收集所有旧 key（用于检测 stale prefix）
    stale_prefix_list = stale_prefixes.get(mod, [])

    new_lines = []
    already_added_new_keys = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue

        k, _, v = stripped.partition("=")
        k = k.strip()
        v_part = "=" + v  # 保留原始值部分

        # 检查是否在 delete_set 中
        if k in delete_set:
            report_lines.append(f"  [DELETE] {mod}: {k}")
            stats["commented_out"] += 1
            if not dry_run:
                new_lines.append(f"# [REMOVED] {line}")
            else:
                new_lines.append(line)
            continue

        # 检查是否匹配 stale prefix
        is_stale_prefix = any(k.startswith(p) for p in stale_prefix_list)
        if is_stale_prefix:
            report_lines.append(f"  [DELETE-PREFIX] {mod}: {k}")
            stats["commented_out"] += 1
            if not dry_run:
                new_lines.append(f"# [REMOVED] {line}")
            else:
                new_lines.append(line)
            continue

        # 检查是否需要重命名
        if k in rename_map:
            new_k = rename_map[k]
            # 检查新 key 是否已存在
            if new_k in kv:
                report_lines.append(f"  [SKIP-RENAME] {mod}: {k} → {new_k} (新 key 已存在)")
                stats["already_new"] += 1
                new_lines.append(line)
            else:
                report_lines.append(f"  [RENAME] {mod}: {k} → {new_k}")
                stats["renamed"] += 1
                if not dry_run:
                    new_lines.append(f"# [RENAMED FROM] {line}")
                    new_lines.append(f"{new_k}={v.strip()}")
                else:
                    new_lines.append(line)
                already_added_new_keys.add(new_k)
            continue

        new_lines.append(line)

    # 在文件末尾追加缺失的翻译（来自英文原版）
    if en_kv and not dry_run:
        current_keys = set(kv.keys()) | already_added_new_keys
        missing_new = [
            nk for ok, nk in rename_map.items()
            if nk not in current_keys and ok not in kv
        ]
        if missing_new:
            new_lines.append("")
            new_lines.append("# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            new_lines.append("# 以下为新增 key，需要人工翻译（当前显示英文原文）")
            new_lines.append("# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for nk in sorted(missing_new):
                if nk in en_kv:
                    new_lines.append(f"# TODO: 待翻译")
                    new_lines.append(f"{nk}={en_kv[nk]}")
                    stats["added"] += 1
                    report_lines.append(f"  [ADD-TODO] {mod}: {nk} = {en_kv[nk][:60]}")

    return new_lines, stats


def fix_mod(mod, trans_folder, renames, stale_prefixes, dry_run, verbose, report_lines):
    """修复单个模组的翻译文件"""
    path = os.path.join(TRANS_PATH_TEMPLATE.format(mod=trans_folder.split("[")[1].rstrip("]")))
    # 实际路径
    folder_name = None
    for d in os.listdir("resources"):
        if f"[{mod}]" in d or f"[{trans_folder.split('[')[1]}" in d:
            check = os.path.join("resources", d, "lang", "zh_CN.lang")
            if os.path.exists(check):
                folder_name = d
                path = check
                break

    if folder_name is None:
        # Try exact folder name
        exact = f"resources/GregTech(+16)[{mod}]/lang/zh_CN.lang"
        if os.path.exists(exact):
            path = exact
        else:
            report_lines.append(f"[WARN] 找不到模组文件: {mod}")
            return None, None

    lines, kv = parse_lang_file(path)
    en_kv = parse_en_lang(mod)
    mod_report = []

    new_lines, stats = apply_fixes(
        mod, lines, kv, renames, stale_prefixes, en_kv, dry_run, mod_report
    )

    if verbose:
        for r in mod_report:
            print(r)

    report_lines.extend(mod_report)
    return path, new_lines, stats


def main():
    parser = argparse.ArgumentParser(
        description="GTNH 汉化仓库 Key 一键修复脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="只检测问题，不修改文件")
    parser.add_argument("--report", default="fix_report.txt",
                        help="报告文件路径 (默认: fix_report.txt)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="输出详细日志")
    parser.add_argument("--en-lang-base", default=None,
                        help="GT5-Unofficial/src/main/resources/assets 路径（用于英文原文填充）")
    parser.add_argument("--mod", default=None,
                        help="只处理指定模组（如: gregtech, tectech）")
    args = parser.parse_args()

    global EN_LANG_BASE
    if args.en_lang_base:
        EN_LANG_BASE = args.en_lang_base

    # 检查是否在正确目录
    if not os.path.exists("resources"):
        print("❌ 错误: 请在 Translation-of-GTNH 仓库根目录下运行此脚本")
        print("   当前目录缺少 resources/ 文件夹")
        sys.exit(1)

    mode_str = "【试运行模式，不修改文件】" if args.dry_run else "【修复模式】"
    print(f"\n{'='*60}")
    print(f"GTNH 汉化 Key 修复脚本 {mode_str}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    report_lines = [
        f"GTNH 汉化 Key 修复报告",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"运行模式: {'试运行（不修改文件）' if args.dry_run else '修复模式'}",
        "=" * 60,
        "",
    ]

    total_stats = {"renamed": 0, "commented_out": 0, "already_new": 0, "added": 0}

    # 模组映射: domain_name → 翻译仓库文件夹名（不含前缀）
    MODS_TO_FIX = {
        "gregtech":         "gregtech",
        "gtneioreplugin":   "gtneioreplugin",
        "gtnhintergalactic":"gtnhintergalactic",
        "gtnhlanth":        "gtnhlanth",
        "ggfab":            "ggfab",
        "miscutils":        "miscutils",
        "tectech":          "tectech",
        "bartworks":        "bartworks",
        "goodgenerator":    "goodgenerator",
        "kubatech":         "kubatech",
    }

    if args.mod:
        if args.mod not in MODS_TO_FIX:
            print(f"❌ 未知模组: {args.mod}")
            print(f"   可用模组: {', '.join(MODS_TO_FIX.keys())}")
            sys.exit(1)
        mods = {args.mod: MODS_TO_FIX[args.mod]}
    else:
        mods = MODS_TO_FIX

    results = []
    for mod, folder in mods.items():
        if mod not in RENAMES and mod not in STALE_PREFIXES:
            if args.verbose:
                print(f"⏭  {mod}: 无需修改")
            continue

        renames = RENAMES.get(mod, [])
        stale_pref = STALE_PREFIXES.get(mod, [])

        # 优先使用 GregTech(+16)[mod] 路径，这是新版汉化包目录
        preferred = f"resources/GregTech(+16)[{mod}]/lang/zh_CN.lang"
        zh_path = preferred if os.path.exists(preferred) else None

        if zh_path is None:
            # 回退：遍历 resources 目录，精确匹配 [mod] 后缀（排除 VisualProspecting 等前缀不同的目录）
            for d in sorted(os.listdir("resources")):
                # 必须以 GregTech 开头且以 [mod] 结尾，避免误匹配
                if (d.startswith("GregTech") and d.endswith(f"[{mod}]")):
                    candidate = os.path.join("resources", d, "lang", "zh_CN.lang")
                    if os.path.exists(candidate):
                        zh_path = candidate
                        break

        if not os.path.exists(zh_path):
            report_lines.append(f"[WARN] 找不到文件: {zh_path}")
            print(f"⚠️  {mod}: 找不到翻译文件 {zh_path}")
            continue

        lines, kv = parse_lang_file(zh_path)
        en_kv = {}
        if EN_LANG_BASE:
            en_path = os.path.join(EN_LANG_BASE, mod, "lang", "en_US.lang")
            _, en_kv = parse_lang_file(en_path)

        mod_report = [f"", f"── 模组: {mod} ──", f"   文件: {zh_path}"]
        new_lines, stats = apply_fixes(
            mod, lines, kv, renames, {mod: stale_pref},
            en_kv, args.dry_run, mod_report
        )

        mod_report.append(
            f"   统计: 重命名={stats['renamed']}, 注释废弃={stats['commented_out']}, "
            f"已存在新key={stats['already_new']}, 新增TODO={stats['added']}"
        )
        report_lines.extend(mod_report)

        for k in ["renamed", "commented_out", "already_new", "added"]:
            total_stats[k] += stats[k]

        results.append((mod, zh_path, new_lines, stats))

        status = "✅" if (stats["renamed"] + stats["commented_out"] + stats["added"]) > 0 else "⏭ "
        print(
            f"{status} {mod:<20} 重命名:{stats['renamed']:3d}  "
            f"废弃注释:{stats['commented_out']:3d}  "
            f"新增TODO:{stats['added']:3d}"
        )

    # 写入修改后的文件
    if not args.dry_run:
        print(f"\n正在写入修改...")
        for mod, path, new_lines, stats in results:
            # 备份原文件
            backup = path + ".bak"
            if not os.path.exists(backup):
                import shutil
                shutil.copy2(path, backup)
            # 写入新文件
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
                if new_lines and new_lines[-1] != "":
                    f.write("\n")
            print(f"  ✍️  已写入: {path}")

    # 汇总
    print(f"\n{'='*60}")
    print(f"修复汇总:")
    print(f"  Key 重命名（翻译已保留）: {total_stats['renamed']}")
    print(f"  废弃 Key 注释掉         : {total_stats['commented_out']}")
    print(f"  新增 TODO 待翻译 Key    : {total_stats['added']}")
    print(f"{'='*60}")

    if args.dry_run:
        print("\n⚠️  试运行模式：以上均未实际修改文件")
        print(f"   去掉 --dry-run 参数后重新运行以应用修复")

    report_lines.extend([
        "",
        "=" * 60,
        "汇总",
        f"  Key 重命名（翻译已保留）: {total_stats['renamed']}",
        f"  废弃 Key 注释掉         : {total_stats['commented_out']}",
        f"  新增 TODO 待翻译 Key    : {total_stats['added']}",
    ])

    with open(args.report, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"\n📄 详细报告已保存至: {args.report}")


if __name__ == "__main__":
    main()
