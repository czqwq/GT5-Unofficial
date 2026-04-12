# GTNH 全模组汉化 Key 对比分析报告

> **分析时间：** 2026-04  
> **源仓库：** [czqwq/GT5-Unofficial](https://github.com/czqwq/GT5-Unofficial) (`src/main/resources/assets/*/lang/en_US.lang`)  
> **汉化仓库：** [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) (`resources/GregTech(+16)[*]/lang/zh_CN.lang`)

---

## 一、问题根因总结

游戏内出现 **"BlackMetal 螺栓"**、**"BlackMetal Bolt"** 等中英混杂显示，根本原因是：

**mod 代码重构时批量重命名了 lang key，但汉化仓库的 `zh_CN.lang` 文件仍使用旧 key，导致游戏找不到对应翻译而回退显示英文原文。**

主要存在三类问题：

| 问题类型 | 说明 | 影响范围 |
|---------|------|---------|
| **Key 重命名** | 旧 key 仍在 zh_CN.lang 中，新 key 没有翻译 | 全部模组均有 |
| **Key 纯新增** | 新版本新增了功能/方块，尚无翻译 | 部分模组 |
| **Key 已删除** | zh_CN.lang 中存在英文原版已删除的 key（无害但冗余） | 全部模组均有 |

---

## 二、各模组翻译覆盖率概览

| 模组 | en_US key 数 | zh_CN key 数 | 缺失 | 废弃(stale) | 覆盖率 |
|-----|-------------|-------------|------|------------|-------|
| bartworks | 255 | 255 | **15** | 15 | 94.1% |
| detravscannermod | 36 | 36 | 0 | 0 | ✅ 100% |
| ggfab | 29 | 30 | **1** | 2 | 96.6% |
| goodgenerator | 529 | 520 | **9** | 0 | 98.3% |
| **gregtech** | **7203** | **3181** | **4279** | **257** | ⚠️ 40.6% |
| gtneioreplugin | 95 | 81 | **51** | 37 | 46.3% |
| gtnhintergalactic | 404 | 393 | **14** | 3 | 96.5% |
| gtnhlanth | 167 | 145 | **24** | 2 | 85.6% |
| ic2 | 27 | 27 | 0 | 0 | ✅ 100% |
| kekztech | 131 | 131 | 0 | 0 | ✅ 100% |
| kubatech | 234 | 211 | **23** | 0 | 90.2% |
| miscutils | 3945 | 3807 | **172** | 34 | 95.6% |
| spiceoflife | 1 | 1 | 0 | 0 | ✅ 100% |
| stevescarts | 1 | 1 | 0 | 0 | ✅ 100% |
| tectech | 1861 | 1854 | **68** | 61 | 96.3% |

> **注意：** gregtech 的 40.6% 覆盖率并非真实翻译覆盖率。  
> 机器名称（`gt.blockmachines.*`，788条）由 `GregTech_zh_CN.lang`（CFG 格式）单独提供，  
> 该文件在 `Translation-of-GTNH/GregTech.lang` 中，有 3304 条机器翻译，覆盖率较好。  
> 真正的 gregtech 问题集中在 `gt.oreprefix.*`（材料物品名）被整体重命名。

---

## 三、最严重问题：`gt.component.*` → `gt.oreprefix.*` 全面重命名

这是导致 **"BlackMetal 螺栓"** 等中英混杂显示的核心原因。

**GT5-Unofficial 将所有材料物品前缀的 key 从 `gt.component.*` 改名为 `gt.oreprefix.*`，但汉化仓库仍使用旧 key。**

### 影响范围
所有材料物品（黑铁、钢铁、铜、金、铝……所有材料的螺栓、锭、板、杆等）在游戏中显示英文。

### 完整映射表（24 条）

| 旧 Key（已失效） | 新 Key（当前有效） | 现有中文翻译 |
|---------------|-----------------|------------|
| `gt.component.dust` | `gt.oreprefix.material_dust` | %s粉 |
| `gt.component.dustsmall` | `gt.oreprefix.small_pile_of_material_dust` | 小堆%s粉 |
| `gt.component.dusttiny` | `gt.oreprefix.tiny_pile_of_material_dust` | 小撮%s粉 |
| `gt.component.ingot` | `gt.oreprefix.material_ingot` | %s锭 |
| `gt.component.hotingot` | `gt.oreprefix.hot_material_ingot` | 热%s锭 |
| `gt.component.plate` | `gt.oreprefix.material_plate` | %s板 |
| `gt.component.platedouble` | `gt.oreprefix.double_material_plate` | 双重%s板 |
| `gt.component.rod` | `gt.oreprefix.material_rod` | %s杆 |
| `gt.component.rodlong` | `gt.oreprefix.long_material_rod` | 长%s杆 |
| `gt.component.gear` | `gt.oreprefix.material_gear` | %s齿轮 |
| `gt.component.smallgear` | `gt.oreprefix.small_material_gear` | 小型%s齿轮 |
| `gt.component.screw` | `gt.oreprefix.material_screw` | %s螺丝 |
| `gt.component.bolt` | `gt.oreprefix.material_bolt` | %s螺栓 |
| `gt.component.rotor` | `gt.oreprefix.material_rotor` | %s转子 |
| `gt.component.ring` | `gt.oreprefix.material_ring` | %s环 |
| `gt.component.foil` | `gt.oreprefix.material_foil` | %s箔 |
| `gt.component.plasmacell` | `gt.oreprefix.material_plasma_cell` | %s等离子体单元 |
| `gt.component.cell` | `gt.oreprefix.material_cell` | %s单元 |
| `gt.component.nugget` | `gt.oreprefix.material_nugget` | %s粒 |
| `gt.component.spring` | `gt.oreprefix.material_spring` | %s弹簧 |
| `gt.component.smallspring` | `gt.oreprefix.small_material_spring` | 小型%s弹簧 |
| `gt.component.finewire` | `gt.oreprefix.fine_material_wire` | 细%s导线 |
| `gt.component.platedense` | `gt.oreprefix.dense_material_plate` | 致密%s板 |
| `gt.component.platesuperdense` | `gt.oreprefix.superdense_material_plate` | 超致密%s板 |

### 新增的 gt.oreprefix.* key（无旧版对应，需要新增翻译）

以下 key 是 GT5-Unofficial 新增的，在旧版 `gt.component.*` 中完全没有对应，需要补充翻译：

```
gt.oreprefix.material                  = %s
gt.oreprefix.material_bar              = %s Bar
gt.oreprefix.material_buzzsaw_blade    = %s Buzzsaw Blade
gt.oreprefix.material_casing           = %s Casing
gt.oreprefix.material_chainsaw_tip     = %s Chainsaw Tip
gt.oreprefix.material_chip             = %s Chip
gt.oreprefix.material_crystal          = %s Crystal
gt.oreprefix.material_crystal_plate    = %s Crystal Plate
gt.oreprefix.material_crystal_powder   = %s Crystal Powder
gt.oreprefix.material_drill_tip        = %s Drill Tip
gt.oreprefix.material_file_head        = %s File Head
gt.oreprefix.material_frame_box        = %s Frame Box
gt.oreprefix.material_hammer_head      = %s Hammer Head
gt.oreprefix.material_ice              = %s Ice
gt.oreprefix.material_infused_stone    = %s Infused Stone
gt.oreprefix.material_lens             = %s Lens
gt.oreprefix.material_nanites          = %s Nanites
gt.oreprefix.material_ore              = %s Ore
gt.oreprefix.material_pane             = %s Pane
gt.oreprefix.material_plank            = %s Plank
gt.oreprefix.material_plasma           = %s Plasma
gt.oreprefix.material_powder           = %s Powder
gt.oreprefix.material_pulp             = %s Pulp
gt.oreprefix.material_round            = %s Round
gt.oreprefix.material_saw_blade        = %s Saw Blade
gt.oreprefix.material_sheet            = %s Sheet
gt.oreprefix.material_sheetmetal       = %s Sheetmetal
gt.oreprefix.material_stick            = %s Stick
gt.oreprefix.material_turbine_blade    = %s Turbine Blade
gt.oreprefix.material_wrench_tip       = %s Wrench Tip
gt.oreprefix.block_of_material         = Block of %s
gt.oreprefix.hot_material_ingot        = Hot %s Ingot
gt.oreprefix.long_material_rod         = Long %s Rod
gt.oreprefix.long_material_stick       = Long %s Stick
gt.oreprefix.short_material_stick      = Short %s Stick
gt.oreprefix.quadruple_material_plate  = Quadruple %s Plate
gt.oreprefix.quintuple_material_plate  = Quintuple %s Plate
# ... 以及管道、导线、矿石、等离子等大量新增 key（共 169 条，参见 en_US.lang）
```

---

## 四、各模组详细 Key 变更清单

### 4.1 bartworks（缺失 15 条，废弃 15 条）

#### 新增 key（需翻译）
```
BW.chat.diode.max_amps = Max Amps: %s
BW.chat.thtr.cannot_change_mode = THTR mode cannot be changed while the machine is running.
BW.chat.thtr.running_in.emptying = THTR is now running in emptying mode.
BW.chat.thtr.running_in.normal = THTR is now running in normal Operation.
chat.proxy.reverse.false = §aRegular§r Recipe Order
chat.proxy.reverse.true = §dReversed§r Recipe Order
gt.oreprefix.bolted_material_casing = Bolted %s Casing
gt.oreprefix.rebolted_material_casing = Rebolted %s Casing
item.CircuitParts.Imprint.name = Circuit Imprint
item.CircuitParts.ImprintBoard.name = Imprint supporting Board
item.CircuitParts.RawImprintBoard.name = Raw Imprint supporting Board
item.CircuitParts.Sliced.name = Sliced Circuit
item.CircuitParts.Wrap.name = Wrap of %s
tooltip.item.CircuitParts.ImprintBoard = A Board needed for Circuit Imprints
tooltip.item.CircuitParts.RawImprintBoard = A Raw Board needed for Circuit Imprints
```

#### 废弃 key（旧 key，可安全删除）
```
# HTGR 相关 key 已迁移到 kubatech 模组
BW.infoData.htgr.*     → 已移至 kubatech
misc.BatchModeTextOff  → 已移至其他模组
misc.BatchModeTextOn   → 已移至其他模组
tooltip.bw.*           → 已重命名
```

---

### 4.2 ggfab（缺失 1 条，废弃 2 条）

#### Key 重命名（typo 修复：busses → buses）
| 旧 Key | 新 Key | 中文翻译（可沿用） |
|--------|--------|-----------------|
| `ggfab.gui.advassline.shutdown.input_busses` | `ggfab.gui.advassline.shutdown.input_buses` | §4输入总线数量过少，无法支持当前配方 |

#### 已删除 key
```
ggfab.recipe.toolcast  （工具铸造机配方分类已被移除）
```

---

### 4.3 goodgenerator（缺失 9 条）

全部为新增 key，需新增翻译：
```
gg.chat.ae_modes.no_access = NO_ACCESS
gg.chat.ae_modes.read = READ
gg.chat.ae_modes.read_write = READ_WRITE
gg.chat.ae_modes.write = WRITE
gg.chat.antimatter_generator.wireless_mode.disable = Wireless network mode disabled..
gg.chat.antimatter_generator.wireless_mode.enable = Wireless network mode enabled.
gg.chat.antimatter_generator.wireless_mode.enable.hint = Wireless only works with UMV Superconductor Base or better.
gg.chat.antimatter_output_hatch.front_face_input.disable = Front face input disabled.
gg.chat.antimatter_output_hatch.front_face_input.enable = Front face input enabled
```

---

### 4.4 gregtech（缺失 4279 条，废弃 257 条）

#### 核心问题（已在第三节详述）
- `gt.component.*`（24条）→ `gt.oreprefix.*`（169条）全面重命名

#### 机器名称 key（`gt.blockmachines.*`）
- 机器名称通过 `GregTech_zh_CN.lang`（CFG 格式）提供，该文件相对完整（3304条 vs 788条 en_US）
- 部分新增描述性 key 仍然缺失（约 198 条新机器描述），详见 `GregTech.lang` 对比

#### 代表性缺失 key（GT5U.gui / GT5U.chat 类）
```
GT5U.DECAY_WAREHOUSE.mode.exporting = Exporting
GT5U.DECAY_WAREHOUSE.mode.normal = Normal
GT5U.GTPP_MULTI_STEAM_FURNACE.mode.* (3条)
GT5U.MBTT.CokeOvenHatch = Coke Oven Hatch
GT5U.MBTT.ControlHatch = Control Hatch
GT5U.MBTT.HatchHint = (Hint: %s)
GT5U.MBTT.InputBus.WithFormat = Input Bus (%s)
GT5U.MBTT.InputHatch.WithFormat = Input Hatch (%s)
GT5U.MBTT.LensHousing = Lens Housing
GT5U.MBTT.StructureBy = Structure by
GT5U.MBTT.Tiers.ComponentAssemblyLineCasing = Component Assembly Line Casing
GT5U.MBTT.Tiers.Glass = Glass
GT5U.MBTT.Tiers.Turbine = Sum of Turbine
GT5U.MBTT.pHSensorHatch = pH Sensor Hatch
GT5U.MULTI_LHC.mode.0 = Accelerator
GT5U.MULTI_LHC.mode.1 = Collider
GT5U.RESEARCH_STATION.mode.* (2条)
... 共 4279 条
```

#### 废弃 key（代表性）
```
GT5U.GTPP_MULTI_CUTTING_MACHINE.mode.0/1  （机器已移除）
GT5U.MBTT.HatchDots = （点：%s）           （格式改变）
GT5U.MBTT.Structure.Complex               （已删除）
GT5U.MULTI_CANNER.mode.0/1               （已移除）
GT5U.gui.button.drone_error              （已重命名）
GT5U.gui.button.drone_outofrange         （已重命名）
GT5U.gui.config.worldgen.end_asteroids   （已移除）
GT5U.gui.text.insufficient               （已重命名）
GT5U.infodata.purification_plant.linked_units.status.online  （已重命名）
GT5U.item.cable.eu_volt                  （已重命名）
GT5U.item.cable.swapped                  （已重命名）
GT5U.item.pipe.swap                      （已重命名）
GT5U.machines.advdebugstructurewriter.*  （已重构）
GT5U.machines.separatebus               （已重命名）
GT5U.machines.stocking_bus.hatch_warning （已重命名）
GT5U.machines.workareaset               （已重命名）
```

---

### 4.5 gtneioreplugin（缺失 51 条，废弃 37 条）

#### 关键重命名：世界名称全部改为小写

所有 `gtnop.world.*` key 从首字母大写改为全小写，共 **28 条**：

| 旧 Key（废弃） | 新 Key（有效） | 中文翻译（可沿用） |
|-------------|-------------|----------------|
| `gtnop.world.Anubis` | `gtnop.world.anubis` | 阿努比斯 |
| `gtnop.world.Asteroids` | `gtnop.world.asteroids` | 小行星带 |
| `gtnop.world.BarnardC` | `gtnop.world.barnarda2` | 巴纳德C |
| `gtnop.world.BarnardE` | `gtnop.world.barnarda4` | 巴纳德E |
| `gtnop.world.BarnardF` | `gtnop.world.barnarda5` | 巴纳德F |
| `gtnop.world.Callisto` | `gtnop.world.callisto` | 木卫四 |
| `gtnop.world.CentauriA` | `gtnop.world.centauribb` | 半人马Bb |
| `gtnop.world.Ceres` | `gtnop.world.ceres` | 谷神星 |
| `gtnop.world.Deimos` | `gtnop.world.deimos` | 火卫二 |
| `gtnop.world.Enceladus` | `gtnop.world.enceladus` | 土卫二 |
| `gtnop.world.Europa` | `gtnop.world.europa` | 木卫二 |
| `gtnop.world.Ganymede` | `gtnop.world.ganymed` | 木卫三 |
| `gtnop.world.Haumea` | `gtnop.world.haumea` | 妊神星 |
| `gtnop.world.Horus` | `gtnop.world.horus` | 荷鲁斯 |
| `gtnop.world.Io` | `gtnop.world.iojupiter` | 木卫一 |
| `gtnop.world.Kuiperbelt` | `gtnop.world.kuiperbelt` | 柯伊伯带 |
| `gtnop.world.Maahes` | `gtnop.world.maahes` | 马赫斯 |
| `gtnop.world.MakeMake` | `gtnop.world.makemake` | 鸟神星 |
| `gtnop.world.Mars` | `gtnop.world.mars` | 火星 |
| `gtnop.world.MehenBelt` | `gtnop.world.asteroidbeltmehen` | 迈罕带 |
| `gtnop.world.Mercury` | `gtnop.world.mercury` | 水星 |
| `gtnop.world.Miranda` | `gtnop.world.miranda` | 天卫五 |
| `gtnop.world.Moon` | `gtnop.world.moon` | 月球 |
| `gtnop.world.Neper` | `gtnop.world.neper` | 奈佩里 |
| `gtnop.world.Oberon` | `gtnop.world.oberon` | 天卫四 |
| `gtnop.world.Phobos` | `gtnop.world.phobos` | 火卫一 |
| `gtnop.world.Pluto` | `gtnop.world.pluto` | 冥王星 |
| `gtnop.world.Proteus` | `gtnop.world.proteus` | 海卫八 |
| `gtnop.world.Ross128b` | `gtnop.world.ross128b` | 罗斯128b |
| `gtnop.world.Ross128ba` | `gtnop.world.ross128ba` | 罗斯128ba |
| `gtnop.world.Seth` | `gtnop.world.seth` | 赛特 |
| `gtnop.world.TcetiE` | `gtnop.world.tcetie` | 鲸鱼座T星E |
| `gtnop.world.Titan` | `gtnop.world.titan` | 土卫六 |
| `gtnop.world.Triton` | `gtnop.world.triton` | 海卫一 |
| `gtnop.world.Twilight` | `gtnop.world.TwilightForest` | 暮色森林 |
| `gtnop.world.VegaB` | `gtnop.world.vega1` | 织女一B |
| `gtnop.world.Venus` | `gtnop.world.venus` | 金星 |

#### 新增 key（需翻译）
```
gtnop.gui.nei.chance.value = %s%%
gtnop.gui.nei.fluidAmount.value = %s-%s
gtnop.tier.0~10 = T0: %s ... T10: %s  (11条)
gtnop.world.dimensionDarkWorld = The Toxic Everglades
```

---

### 4.6 gtnhintergalactic（缺失 14 条，废弃 3 条）

#### Key 重命名（提示方块描述格式改变）

| 旧 Key（废弃） | 新 Key（有效） | 中文翻译（可沿用） |
|-------------|-------------|----------------|
| `ig.elevator.structure.AnyBaseCasingWith1Dot` | `ig.elevator.structure.AnyBaseCasingWithHintNumber1` | 任意太空电梯基座机械方块(提示方块：1号) |
| `ig.elevator.structure.AnyBaseCasingWith2Dot` | `ig.elevator.structure.AnyBaseCasingWithHintNumber2` | 任意太空电梯基座机械方块(提示方块：2号) |
| `ig.elevator.structure.AnyBaseCasingWith3Dot` | `ig.elevator.structure.AnyBaseCasingWithHintNumber3` | 任意太空电梯基座机械方块(提示方块：3号) |

#### 新增 key（需翻译）
```
gt.blockcasingsSE.0.name = Space Elevator Base Casing
gt.blockcasingsSE.1.name = Space Elevator Support Structure
gt.blockcasingsSE.2.name = Space Elevator Internal Structure
gt.blockcasingsSEMotor.0~4.name = Space Elevator Motor MK-I~MK-V (5条)
ig.asteroid.NetherOreAsteroid = Nether ore
ig.asteroid.spaceOreAsteroid = Space Ore
ig.siphon.structure.HatchRequirement = Must have exactly §61§7 of each hatch!
```

---

### 4.7 gtnhlanth（缺失 24 条，废弃 2 条）

#### Key 重命名

| 旧 Key（废弃） | 新 Key（有效） | 中文翻译（可沿用） |
|-------------|-------------|----------------|
| `gtnhlanth.tt.hintdot` | `gtnhlanth.tt.hintNumber` | 提示方块：%s号 |

> `beamline.particleinput`（输入粒子信息：）已被删除，无对应新 key。

#### 新增 key（需翻译）
```
# GUI 状态文字
GT5U.gui.text.gtnhlanth.inputinterrupt = Input Beam must not be interrupted or changed!
GT5U.gui.text.gtnhlanth.noparticle = Particle absent (rate is 0)!
GT5U.gui.text.gtnhlanth.toolowenergy = Below Required Energy!
GT5U.gui.text.gtnhlanth.wrongparticle = Incorrect Particle!
# 粒子束工艺参数
beamcrafting.amount_A = Amount 1
beamcrafting.amount_B = Amount 2
beamcrafting.energy_A = min Energy 1
beamcrafting.energy_B = min Energy 2
# 机器方块
gt.blockmachines.beamline_pipe.name = Beamline Pipe
# 粒子名称（全部未翻译）
particle.electron_neutrino = Electron Neutrino
particle.eta = Eta
particle.graviton = Graviton
particle.higgs = Higgs Boson
particle.jpsi = J/Psi
particle.lambda = lambda
particle.muon = Muon
particle.muon_neutrino = Muon Neutrino
particle.omega = Omega
particle.tau = Tau
particle.tau_neutrino = Tau Neutrino
particle.upsilon = Upsilon
particle.wboson = W Boson
particle.zboson = Z Boson
```

---

### 4.8 kubatech（缺失 23 条）

全部为新增 key。HTGR（高温气冷反应堆）相关功能从 bartworks 迁移到 kubatech，需新增翻译：

```
# 熔炉外壳（新增材料等级）
defc.casing.7.name = Naquadah Alloy Fusion Casing
defc.casing.8.name = Bloody Ichorium Fusion Casing
defc.casing.9.name = Draconium Fusion Casing
defc.casing.10.name = Wyvern Fusion Casing
defc.casing.11.name = Awakened Draconium Fusion Casing
defc.casing.12.name = Chaotic Fusion Casing
# HTGR 燃料物品
item.htgr_item.0.name = TRISO Fuel Mixture (%s)
item.htgr_item.1.name = Incomplete BISO Fuel (%s)
item.htgr_item.2.name = Incomplete TRISO Fuel (%s)
item.htgr_item.3.name = TRISO Fuel (%s)
item.htgr_item.4.name = Burned Out TRISO Fuel (%s)
# HTGR 机器界面
kubatech.htgrrecipes = High Temperature Gas Reactor
kubatech.gui.text.time_line = Time: %s secs
kubatech.gui.text.usage_line = Usage: %s EU/t
kubatech.infodata.htgr.burned_fuel = Burned Fuel:
kubatech.infodata.htgr.burned_fuel_entry = §f- §b%s §fx §6%s%% to output
kubatech.infodata.htgr.coolant_per_tick = Coolant per tick: §6%sL
kubatech.infodata.htgr.fuel_supply = Fill level %s out of %s
kubatech.infodata.htgr.helium_supply = Helium Supply: §6%sL
kubatech.infodata.htgr.stored_fuel = Stored Fuel:
kubatech.infodata.htgr.stored_fuel_entry = §f- §b%s §fx §6%s
kubatech.infodata.htgr.water_per_tick = Water per tick: §6%sL
kubatech.tooltip.htgr_material = Material for High Temperature Gas-cooled Reactor
```

---

### 4.9 miscutils（缺失 172 条，废弃 34 条）

#### Key 重命名

| 旧 Key（废弃） | 新 Key（有效） | 中文翻译（可沿用） |
|-------------|-------------|----------------|
| `interaction.separateBusses.enabled` | `interaction.separateBuses.enabled` | 输入总线已独立 |
| `interaction.separateBusses.disabled` | `interaction.separateBuses.disabled` | 输入总线未独立 |

#### 废弃 key（物品已删除）
```
item.FertileManureSlurry.name, item.Fertiliser.name, item.ManureSlurry.name,
item.RawWaste.name, item.UN18Fertiliser.name, item.UN32Fertiliser.name,
item.itemDust*Fertiliser.name, item.BasicGenericChemItem.29~32.name,
tile.blockPestKiller.name, tile.blockPooCollector.*.name,
tile.blockProjectBench.name, container.pestkiller,
misc.BatchModeTextOff, misc.BatchModeTextOn
```

#### 新增 key 分类

| 类别 | 数量 | 说明 |
|-----|------|------|
| `gtplusplus.blockcasings.*` | 69 | 新增 GT++ 机械方块（casings 2-6系列、管道齿轮系列）|
| `gtpp.book.*` | 35 | 书本内容（手册页面） |
| `gtplusplus.blockspecialcasings.*` | 28 | 特殊机械方块 |
| `miscutils.blockcasings.*` | 16 | miscutils 专用机械方块 |
| `gtplusplus.blocktieredcasings.*` | 10 | 分级机械方块 |
| `gtpp.tiered_tank.*` | 9 | 分级储液罐系统 |
| `interaction.separateBuses.*` | 2 | 已重命名（见上方） |
| 其他 | 3 | GT5U.infodata、gtpp.recipe、gtpp.nei |

---

### 4.10 tectech（缺失 68 条，废弃 61 条）

#### Key 重命名

| 旧 Key（废弃） | 新 Key（有效） | 中文翻译（可沿用） |
|-------------|-------------|----------------|
| `gt.3blockcasingsTT.2.name` | `gt.blockcasingsTT.2.name` | 计算机散热风扇 |
| `gt.blockmachines.hatch.dynamomulti.desc.0` | `gt.blockmachines.hatch.dynamomulti.desc` | （desc.0 + desc.1 合并） |
| `gt.blockmachines.hatch.energymulti.desc.0` | `gt.blockmachines.hatch.energymulti.desc` | （多行合并为一条） |
| `gt.blockmachines.hatch.dynamotunnel.desc.0` | `gt.blockmachines.hatch.dynamotunnel.desc` | （多行合并） |
| `gt.blockmachines.hatch.energytunnel.desc.0` | `gt.blockmachines.hatch.energytunnel.desc` | （多行合并） |
| `gt.blockmachines.debug.tt.writer.name` | （已移至 gregtech 主模组） | Debug结构打印机 |

#### 废弃的激光仓系列（已重构）
原来 `dynamotunnel2~7` / `energytunnel2~7` 的各 tier 名称（`tier.05~10.name`）共 **46 条**已被删除。  
新版激光仓命名方式改变，不再需要这些 key。

#### 新增 key（需翻译）
```
# 物质凝聚炉（Eye of Harmony）配方界面
EOH.Recipe.BaseRecipeChance = Base Recipe Chance: %s%%
EOH.Recipe.EU.In/Out = EU Input/Output: %s EU
EOH.Recipe.Helium.In = Helium: %s L
EOH.Recipe.RecipeEnergyEfficiency = Recipe Energy Efficiency: %s%%
EOH.Recipe.SpacetimeTier = Spacetime Tier: %s
EOH_Controller_AstralArrayAmount = Stored Astral Arrays: %s
EOH_Controller_PlanetBlock = Current Planet Block: %s
# 安培追踪器界面
GT5U.gui.text.at_eu_transferred = §8EU Transferred:
GT5U.gui.text.at_history.values = %s EU/t  (%sA %s)
GT5U.gui.text.at_past_*.header (3条)
GT5U.gui.text.time_line = Time: %s secs
GT5U.gui.text.time_line_with_ticks = Time: %s secs (%d ticks)
GT5U.gui.text.total_line = Total: %s EU
GT5U.gui.text.usage_line = Usage: %s EU/t
# 星级颜色 Cosmetics 界面（FOG 机器）
fog.cosmetics.* (10条 - 颜色选择器)
# 新增机械方块
gt.blockcasingsBA0.10.name = Reinforced Temporal Structure Casing
gt.blockcasingsBA0.11.name = Reinforced Spatial Structure Casing
gt.blockcasingsBA0.12.name = Infinite Spacetime Energy Boundary Casing
gt.blockcasingsTT.2.name = Computer Heat Vent （需从旧 key 迁移）
gt.godforgecasing.0~8.name = 天神熔炉系列外壳 (9条)
gt.blockmachines.pipe.datastream.block.name = Optical Fiber Cable Casing
gt.blockmachines.pipe.energystream.block.name = Laser Vacuum Pipe Casing
# 世界加速器
tt.block.world_accelerator.set_mode = Switched mode to: %s
tt.block.world_accelerator.set_range = Machine range changed to %s blocks
tt.block.world_accelerator.set_speed = Machine acceleration changed to x%s
# Ender 流体连接
tt.cover.ender_fluid_link.fill = Ender Filling Engaged!
tt.cover.ender_fluid_link.suck = Ender Suction Engaged!
# 量子计算机连接状态
tt.infodata.multi.connection_health.* (5条)
tt.keyword.Structure.AnyComputerCasingsHint1or3
```

---

## 五、修复方案

### 方案说明

本分析附带了一个 Python 修复脚本 `fix_translation_keys.py`，可在 `Translation-of-GTNH` 仓库根目录下运行。

脚本功能：
1. **自动重命名**：将所有已识别的旧 key 替换为新 key（保留现有中文翻译）
2. **自动补全**：用英文原文填充所有缺失的新 key（标记 `# TODO: 待翻译` 以便后续人工翻译）
3. **自动删除**：将纯废弃 key（无对应新 key）注释掉
4. **生成报告**：输出详细的修改报告

### 修复后预期效果

| 修复项 | 效果 |
|--------|------|
| `gt.component.*` → `gt.oreprefix.*` | BlackMetal 螺栓等所有材料物品名称恢复中文 |
| `gtnop.world.*` 大小写 | NEI 矿石插件中行星名称恢复中文 |
| `ig.elevator.structure.*Dot` → `*HintNumber*` | 太空电梯结构提示恢复中文 |
| `gtnhlanth.tt.hintdot` → `gtnhlanth.tt.hintNumber` | 粒子束工艺提示恢复中文 |
| `ggfab.gui.advassline.shutdown.input_busses` → `input_buses` | 先进装配线关机提示恢复中文 |
| `interaction.separateBusses.*` → `separateBuses.*` | miscutils 总线独立提示恢复中文 |
| `gt.3blockcasingsTT.2.name` → `gt.blockcasingsTT.2.name` | TecTech 计算机散热风扇名称恢复中文 |

---

## 六、修改文件清单

需要在 [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) 仓库修改的文件：

| 文件路径 | 操作 |
|---------|------|
| `resources/GregTech(+16)[gregtech]/lang/zh_CN.lang` | ⚠️ 重点修改：gt.component.* → gt.oreprefix.* |
| `resources/GregTech(+16)[gtneioreplugin]/lang/zh_CN.lang` | 世界名称大小写重命名 |
| `resources/GregTech(+16)[gtnhintergalactic]/lang/zh_CN.lang` | Dot → HintNumber 重命名 + 新增 |
| `resources/GregTech(+16)[gtnhlanth]/lang/zh_CN.lang` | hintdot → hintNumber + 新增粒子名 |
| `resources/GregTech(+16)[ggfab]/lang/zh_CN.lang` | busses → buses typo 修复 |
| `resources/GregTech(+16)[miscutils]/lang/zh_CN.lang` | separateBusses → separateBuses + 新增方块 |
| `resources/GregTech(+16)[tectech]/lang/zh_CN.lang` | 多处重命名 + 新增 EOH/FOG 界面 |
| `resources/GregTech(+16)[bartworks]/lang/zh_CN.lang` | 新增 chat/item key |
| `resources/GregTech(+16)[goodgenerator]/lang/zh_CN.lang` | 新增 AE 模式 + 反物质发电机 |
| `resources/GregTech(+16)[kubatech]/lang/zh_CN.lang` | 新增 HTGR + 融合外壳 |
