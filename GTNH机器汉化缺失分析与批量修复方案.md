# GTNH 机器与机器方块汉化缺失分析与批量修复方案

## 一、翻译系统架构（关键前提）

GTNH 中的 GregTech 汉化由**两套互补的系统**共同提供，理解这一点是排查问题的基础：

```
┌──────────────────────────────────────────────────────┐
│  优先级 ①（高）：MC 标准 lang 系统 (txloader 加载)    │
│  文件：resources/GregTech[gregtech]/lang/zh_CN.lang  │
│  用途：GT5U.* / achievement.* / fluid.* / gt.component.* 等 │
└──────────────────────┬───────────────────────────────┘
                       │ 若 key 不在此文件中，则向下查找
┌──────────────────────▼───────────────────────────────┐
│  优先级 ②（低）：GTLanguageManager cfg 系统           │
│  文件：config/GregTech_zh_CN.lang（由 GregTech.lang 安装）│
│  用途：gt.blockmachines.* / gt.blockcasings.* 等机器名 │
└──────────────────────┬───────────────────────────────┘
                       │ 若两者都没有
┌──────────────────────▼───────────────────────────────┐
│  兜底：英文原文（en_US.lang）                          │
│  结果：显示英文，即"汉化不全"                           │
└──────────────────────────────────────────────────────┘
```

**GTPreLoad.java** 初始化逻辑（已确认）：
```java
// 玩家语言为 zh_CN 时
String l10nFileName = "GregTech_zh_CN.lang";
File l10nFile = new File(languageDir, l10nFileName);
if (l10nFile.isFile()) {
    GTLanguageManager.sEnglishFile = new Configuration(l10nFile); // 使用 cfg 翻译
} else {
    // 找不到 GregTech_zh_CN.lang，回退英文！
    GTLanguageManager.sEnglishFile = new Configuration(new File(languageDir, "GregTech.lang"));
    GTLanguageManager.isEN_US = true;
}
```

---

## 二、三方数据对比总览

对比对象：
- **GT5-Unofficial** `src/main/resources/assets/gregtech/lang/en_US.lang`（当前英文原文，7203 个 key）
- **Translation-of-GTNH** `resources/GregTech[gregtech]/lang/zh_CN.lang` + `resources/GregTech(+16)[gregtech]/lang/zh_CN.lang`（合并后 3592 个 key）
- **Translation-of-GTNH** `GregTech.lang`（cfg 格式，安装为 `GregTech_zh_CN.lang`，68865 个 key）

| 指标 | 数量 |
|------|------|
| en_US.lang 总 key 数 | **7203** |
| resources/zh_CN.lang 总 key 数 | **3592** |
| GregTech.lang (cfg) 总 key 数 | **68865** |
| en_US 中未出现在 resources/ 的 key | **3870** |
| 其中：cfg 中有翻译（会正常显示） | **1177** |
| 其中：两者都没有（**完全未翻译**） | **2693** |
| resources/ 中已失效的废弃 key (stale) | **259** |

---

## 三、完全缺失翻译的分类统计（2693 个）

> **完全缺失** = 既不在 `resources/zh_CN.lang`，也不在 `GregTech_zh_CN.lang (cfg)` 中

| 类别 | 缺失数量 | 说明 |
|------|----------|------|
| `gt.item.*` | **1338** | 电路板、食物、盖板、电池等物品名称 |
| `GT5U.gui.*` | **218** | GUI 按钮、文字、配置面板标签 |
| `gt.blockmachines.*` | **197** | 新增多方块机器和基础机器 tooltip |
| `gt.oreprefix.*` | **169** | 材料前缀（详见 `GTNH汉化显示不全分析与修改建议.md`） |
| `GT5U.tooltip.*` | **138** | 物品/机器提示文字 |
| `GT5U.chat.*` | **104** | 聊天栏消息 |
| `gt.circuitcomponent.*` | **69** | 电路组件名称 |
| `GT5U.scanner.*` | **51** | 扫描仪信息 |
| `GT5U.waila.*` | **50** | WAILA/TOP 模组显示文字 |
| `GT5U.machines.*` | **45** | 机器 GUI 文字 |
| `gt.book.*` | **24** | 书本内容 |
| `GT5U.power_goggles_config.*` | **23** | 动力护目镜配置 |
| `gt.recipe.*` | **20** | 配方名称（见下节） |
| `GT5U.multiblock.*` | **19** | 多方块机器状态文字 |
| `gt.foundrycasings.*` | **14** | 铸造厂外壳方块 |
| `gt.multiblock.*` | **14** | 多方块结构描述 |
| `gt.blockcasings12.*` | **8** | 新增外壳方块（焦炭窑砖等） |
| `gt.blockcasings13.*` | **10** | 新增外壳方块 |
| 其他 | ~300 | 杂项 |

---

## 四、机器方块（gt.blockmachines）问题详解

### 4.1 通过 cfg 正常工作的机器（590 个）

这些机器名称 **en_US.lang 有，resources/zh_CN.lang 没有，但 GregTech_zh_CN.lang (cfg) 中有中文翻译**，正常情况下会从 cfg 读取正确显示。

**前提条件**：`GregTech_zh_CN.lang` 文件必须正确安装在 `config/GregTech/` 目录下。

示例：
```
gt.blockmachines.basicmachine.alloysmelter.tier.01.name
  en_US: Basic Alloy Smelter
  cfg zh: 基础合金炉    ✓ 正常

gt.blockmachines.basicmachine.accelerator.tier.01.name
  en_US: Basic World Accelerator
  cfg zh: 基础世界加速器  ✓ 正常
```

### 4.2 完全缺失翻译的机器（197 个）

这些机器既不在 resources/ 也不在 cfg 中，**会显示英文**。主要是**新增机器**：

#### 新增多方块机器（完全无翻译）
| 机器类型 | 代表 key | 英文名 |
|----------|---------|--------|
| 粒子加速器/LHC | `gt.blockmachines.multimachine.beamcrafting.LHC.*` | Large Hadron Collider |
| 铸造厂模块 | `gt.blockmachines.multimachine.foundry.*` | Foundry |
| 净化单元相关 GUI | `GT5U.gui.multimachine.purificationunit*` | Clarifier / Ozonation 等 |

#### 新增基础机器 Tooltip（完全无翻译，16 个）
| key | 英文原文（摘要） |
|-----|---------------|
| `gt.blockmachines.basicmachine.accelerator.tooltip` | World Accelerator 详细说明 |
| `gt.blockmachines.basicmachine.maglev.tooltip` | MagLev 磁悬浮引导装置说明 |
| `gt.blockmachines.basicmachine.microtransmitter.tooltip` | 无线能量传输说明 |
| `gt.blockmachines.basicmachine.miner.tooltip` | 矿机详细参数说明 |
| `gt.blockmachines.basicmachine.pump.tooltip` | 抽水机详细参数说明 |
| `gt.blockmachines.basicmachine.teleporter.tooltip` | 传送机说明 |
| `gt.blockmachines.basicmachine.betterjukebox.tooltip.*` | 高级点唱机说明（多条） |
| `gt.blockmachines.basicmachine.seismicprospector.tooltip` | 地震勘探仪说明 |
| `gt.blockmachines.basicmachine.mobrep.tooltip` | 驱怪装置说明 |

### 4.3 外壳方块（gt.blockcasings）问题

| | en_US | resources/zh_CN | cfg |
|-|-------|-----------------|-----|
| gt.blockcasings | 29 | **2** | 27 ✓ |
| gt.blockcasings2~13 (各16~8个) | 208总计 | 极少 | 大部分在 cfg |
| gt.foundrycasings | 14 | 0 | **0** ❌ |
| gt.blockcasings12 | 11 | 0 | **3** ❌缺8 |
| gt.blockcasings13 | 15 | 0 | **5** ❌缺10 |

**焦炭窑砖**等新外壳完全未翻译：
```
gt.blockcasings12.0.name = Coke Oven Bricks
gt.blockcasings12.1.name = Nanochip Mesh Interface Casing
gt.blockcasings12.13.name = Mixer Casing
```

---

## 五、废弃（Stale）Key 和已知重命名列表

### 5.1 resources/zh_CN.lang 中的废弃 key（259 个）

这些 key 在翻译文件中有中文，但当前 en_US.lang 中已不存在，翻译**永远不会被调用**。

#### 关键重命名（stale → new key）

| 旧 key（废弃） | 新 key（当前） | 中文翻译（可沿用） | en_US 新值 |
|---------------|---------------|------------------|-----------|
| `GT5U.item.cable.eu_volt` | `GT5U.item.cable.loss.eu_volt` | 伏 | `%s EU-Volt` |
| `GT5U.item.cable.swapped` | `GT5U.item.cable.swapped.s` | 线缆交换： | `Cable swapped: %s` |
| `GT5U.item.pipe.swap` | `GT5U.item.pipe.swap.s` | 管道交换： | `Pipe swapped: %s` |
| `GT5U.machines.workareaset` | `GT5U.machines.workareaset.s` | 工作区域设置为 | `Work Area set to %sx%s` |
| `GT5U.infodata.purification_plant.linked_units.status.online` | `GT5U.infodata.purification_plant.linked_units.status.active` | 在线 | `Active` |
| `GT5U.gui.button.drone_error` | `GT5U.gui.button.drone_status` | 按§3关机状态§r排序 | `Sort by §3shutdown status` |
| `GT5U.gui.button.drone_showLocalName` | `GT5U.gui.button.drone_searchoriname` | 显示本地化名称 | `Also search original name` |
| `GT5U.MULTI_CANNER.mode.0` | （已删除） | 装罐机 | — |
| `GT5U.MULTI_CANNER.mode.1` | （已删除） | 流体灌装机 | — |
| `GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.0` | （已删除） | 切割机 | — |
| `GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.1` | （已删除） | 切片机 | — |
| `GT5U.MBTT.HatchDots` | （已删除） | （点：%s） | — |
| `GT5U.MBTT.Structure.Complex` | （已删除） | 结构太复杂了！ | — |

#### gt.recipe 重命名

| 旧 key（废弃） | 新 key（当前） | 说明 |
|---------------|---------------|------|
| `gt.recipe.macerator_pulverizer` | （已删除） | 研磨机/粉碎机 |
| `gt.recipe.macerator_pulverizer.description` | （已删除） | 粉碎你的矿物 |
| `gt.recipe.slicer` | （已删除） | 食材切片机 |
| `gt.recipe.slicer.description` | （已删除） | 生活的片段 |

#### gt.component.* 废弃 key（24 个）

详见 `GTNH汉化显示不全分析与修改建议.md`，全部应替换为 `gt.oreprefix.*`。

---

## 六、新增但完全未翻译的配方名（20 个）

```
gt.recipe.beamcrafter            = Beam Crafter
gt.recipe.cable                  = Cable Coating
gt.recipe.cablecoater.description = Coating Cables
gt.recipe.cauldron               = Cauldron
gt.recipe.cokeoven               = Coke Oven
gt.recipe.drawerframer           = Drawer Framer
gt.recipe.foundry_modules        = Foundry Module Components
gt.recipe.large_hadron_collider  = Large Hadron Collider
gt.recipe.nanochip.assemblymatrix       = Nanochip Assembly Matrix
gt.recipe.nanochip.biologicalcoordinator = Accelerated Biological Coordinator
gt.recipe.nanochip.boardprocessor       = Full-Board Immersion Device
gt.recipe.nanochip.conversion           = Nanochip Conversion Complex
gt.recipe.nanochip.cuttingchamber       = Nanoprecision Cutting Chamber
gt.recipe.nanochip.encasementwrapper    = Nanometer Encasement Wrapper
gt.recipe.nanochip.etchingarray         = Ultra-high Energy Etching Array
gt.recipe.nanochip.opticalorganizer     = Optically Optimized Organizer
gt.recipe.nanochip.smdprocessor         = Part Preparation Apparatus
gt.recipe.nanochip.superconductorsplitter = Superconductive Strand Splitter
gt.recipe.nanochip.wiretracer           = Nanoprecision Wire Tracer
```

---

## 七、批量检测与替换脚本

请参阅本目录下的 **`fix_gtnh_translation.py`** 脚本，功能包括：

1. 自动对比 `en_US.lang` 与两个翻译文件，输出完整 diff 报告
2. 自动将废弃 key 替换为新 key（重命名修复）
3. 输出完全缺失的 key 清单（需要人工翻译）

**使用方式：**
```bash
python3 fix_gtnh_translation.py \
  --en    path/to/en_US.lang \
  --res   "path/to/resources/GregTech(+16)[gregtech]/lang/zh_CN.lang" \
  --cfg   path/to/GregTech.lang \
  --out-res   path/to/zh_CN.lang.fixed \
  --out-cfg   path/to/GregTech.lang.fixed \
  --report    path/to/report.txt
```

---

## 八、修复优先级建议

| 优先级 | 操作 | 影响范围 |
|--------|------|---------|
| 🔴 最高 | 将 `resources/zh_CN.lang` 中 27 个 GT5U stale key 按上表重命名 | 线缆/管道/无人机/工作区域显示修复 |
| 🔴 最高 | 将 `gt.component.*` 24 个替换为 `gt.oreprefix.*`（见上一份 MD） | 所有材料物品名称（锡锭、铜粉等） |
| 🟠 高 | 在 `resources/zh_CN.lang` 中补充 `gt.oreprefix.*` 169 条 | 材料物品前缀 |
| 🟡 中 | 在 `GregTech.lang (cfg)` 中补充新增机器翻译（197 条缺失） | 新机器显示英文 |
| 🟡 中 | 补充 `gt.blockcasings12` `gt.blockcasings13` `gt.foundrycasings` | 新外壳方块 |
| 🟢 低 | 补充 `GT5U.gui.*`（218 条）、`GT5U.tooltip.*`（138 条） | GUI 按钮和提示 |
| 🟢 低 | 补充 `gt.recipe.*` 新增 20 条配方名 | NEI 配方面板 |

---

## 九、需修改的文件

| 仓库 | 文件 | 操作 |
|------|------|------|
| [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) | `resources/GregTech[gregtech]/lang/zh_CN.lang` | 修复 stale key，补充 oreprefix |
| [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) | `resources/GregTech(+16)[gregtech]/lang/zh_CN.lang` | 同上 |
| [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) | `GregTech.lang` | 补充新机器、新外壳、新配方翻译 |
