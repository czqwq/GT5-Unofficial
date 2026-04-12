# GTNH 中文汉化显示不全问题分析与修改建议

## 问题现象

游戏中物品名称显示中英混杂，例如：
- `锡 Ingot`（应为 `锡锭`）
- `锡 Dust`（应为 `锡粉`）
- `锡 Plate`（应为 `锡板`）
- 以及所有基于材料生成的物品名称

## 根本原因

### GT5-Unofficial 的本地化机制

GT5-Unofficial（GTNH 中的 GregTech 模组）使用一套**动态模板系统**来生成材料物品的名称。核心逻辑在 `OrePrefixes.java` 中：

```java
// 生成本地化 key 的逻辑
public String getOreprefixKey(IOreMaterial materials) {
    return "gt.oreprefix." + this.getDefaultLocalNameFormatForItem(materials)
        .toLowerCase()
        .replace(" ", "_")
        .replace("%material", "material");
}

// 获取本地化名称
public String getLocalizedNameForItem(IOreMaterial materials) {
    return StatCollector.translateToLocalFormatted(getOreprefixKey(materials), materials.getLocalizedName());
}
```

**工作流程：**
1. 对于"锡锭"，模板格式为 `%material Ingot`
2. 生成 key：`gt.oreprefix.material_ingot`
3. 在语言文件中查找该 key：
   - 找到中文条目 → 正确显示（如 `%s锭` → `锡锭`）
   - 未找到 → 回退到英文 `%s Ingot`，但 `%s` 是已翻译的材料名 `锡` → 显示 **`锡 Ingot`**

### 汉化文件使用了已废弃的旧 key 格式

GT5-Unofficial **已经将** 材料物品名称的 key 从旧格式 `gt.component.*` **重命名为** 新格式 `gt.oreprefix.*`。

**关键数据：**
- GT5-Unofficial `en_US.lang` 中：**没有** `gt.component.*` 条目，只有 `gt.oreprefix.*`（共 169 条）
- GT5-Unofficial Java 代码中：**没有**任何地方查找 `gt.component.*` key
- Translation-of-GTNH 的 `zh_CN.lang` 中：只有旧的 `gt.component.*`（24 条），**完全没有** `gt.oreprefix.*`

由于 `gt.component.*` key 已经不被代码识别，翻译文件中这 24 条翻译**完全失效**，导致所有材料物品名称回退到英文模板。

---

## 受影响的文件

在 [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) 仓库中，以下文件需要修改：

1. **`resources/GregTech[gregtech]/lang/zh_CN.lang`**（203 KB，约 3923 行）
2. **`resources/GregTech(+16)[gregtech]/lang/zh_CN.lang`**（172 KB，约相同结构）

两个文件均有相同问题，需要同步修改。

---

## 修改方案

### 第一步：替换旧 key 为新 key

将两个文件中 `# Components` 部分的旧 `gt.component.*` 条目**替换**为对应的新 `gt.oreprefix.*` 条目：

**当前（旧格式，已失效）：**
```lang
# Components
gt.component.dust=%s粉
gt.component.dustsmall=小堆%s粉
gt.component.dusttiny=小撮%s粉
gt.component.ingot=%s锭
gt.component.hotingot=热%s锭
gt.component.plate=%s板
gt.component.platedouble=双重%s板
gt.component.rod=%s杆
gt.component.rodlong=长%s杆
gt.component.gear=%s齿轮
gt.component.smallgear=小型%s齿轮
gt.component.screw=%s螺丝
gt.component.bolt=%s螺栓
gt.component.rotor=%s转子
gt.component.ring=%s环
gt.component.foil=%s箔
gt.component.plasmacell=%s等离子体单元
gt.component.cell=%s单元
gt.component.nugget=%s粒
gt.component.spring=%s弹簧
gt.component.smallspring=小型%s弹簧
gt.component.finewire=细%s导线
gt.component.platedense=致密%s板
gt.component.platesuperdense=超致密%s板
```

**修改为（新格式，对应关系如下）：**

| 旧 key | 新 key | 中文翻译 |
|--------|--------|---------|
| `gt.component.dust` | `gt.oreprefix.material_dust` | `%s粉` |
| `gt.component.dustsmall` | `gt.oreprefix.small_pile_of_material_dust` | `小堆%s粉` |
| `gt.component.dusttiny` | `gt.oreprefix.tiny_pile_of_material_dust` | `小撮%s粉` |
| `gt.component.ingot` | `gt.oreprefix.material_ingot` | `%s锭` |
| `gt.component.hotingot` | `gt.oreprefix.hot_material_ingot` | `热%s锭` |
| `gt.component.plate` | `gt.oreprefix.material_plate` | `%s板` |
| `gt.component.platedouble` | `gt.oreprefix.double_material_plate` | `双重%s板` |
| `gt.component.rod` | `gt.oreprefix.material_rod` | `%s杆` |
| `gt.component.rodlong` | `gt.oreprefix.long_material_rod` | `长%s杆` |
| `gt.component.gear` | `gt.oreprefix.material_gear` | `%s齿轮` |
| `gt.component.smallgear` | `gt.oreprefix.small_material_gear` | `小型%s齿轮` |
| `gt.component.screw` | `gt.oreprefix.material_screw` | `%s螺丝` |
| `gt.component.bolt` | `gt.oreprefix.material_bolt` | `%s螺栓` |
| `gt.component.rotor` | `gt.oreprefix.material_rotor` | `%s转子` |
| `gt.component.ring` | `gt.oreprefix.material_ring` | `%s环` |
| `gt.component.foil` | `gt.oreprefix.material_foil` | `%s箔` |
| `gt.component.plasmacell` | `gt.oreprefix.material_plasma_cell` | `%s等离子体单元` |
| `gt.component.cell` | `gt.oreprefix.material_cell` | `%s单元` |
| `gt.component.nugget` | `gt.oreprefix.material_nugget` | `%s粒` |
| `gt.component.spring` | `gt.oreprefix.material_spring` | `%s弹簧` |
| `gt.component.smallspring` | `gt.oreprefix.small_material_spring` | `小型%s弹簧` |
| `gt.component.finewire` | `gt.oreprefix.fine_material_wire` | `细%s导线` |
| `gt.component.platedense` | `gt.oreprefix.dense_material_plate` | `致密%s板` |
| `gt.component.platesuperdense` | `gt.oreprefix.superdense_material_plate` | `超致密%s板` |

### 第二步：添加新增的 `gt.oreprefix.*` 条目

GT5-Unofficial 新增了许多旧系统中没有的 oreprefix key，需要翻译并添加。以下是**建议的中文翻译**（供参考，可根据 GTNH 翻译风格调整）：

```lang
# Components（替换旧的 gt.component.* 部分，使用以下内容）
gt.oreprefix.material=%s
gt.oreprefix.material_ingot=%s锭
gt.oreprefix.hot_material_ingot=热%s锭
gt.oreprefix.material_nugget=%s粒
gt.oreprefix.material_dust=%s粉
gt.oreprefix.small_pile_of_material_dust=小堆%s粉
gt.oreprefix.tiny_pile_of_material_dust=小撮%s粉
gt.oreprefix.material_plate=%s板
gt.oreprefix.double_material_plate=双重%s板
gt.oreprefix.triple_material_plate=三重%s板
gt.oreprefix.quadruple_material_plate=四重%s板
gt.oreprefix.quintuple_material_plate=五重%s板
gt.oreprefix.dense_material_plate=致密%s板
gt.oreprefix.superdense_material_plate=超致密%s板
gt.oreprefix.material_rod=%s杆
gt.oreprefix.long_material_rod=长%s杆
gt.oreprefix.material_stick=%s棍
gt.oreprefix.long_material_stick=长%s棍
gt.oreprefix.short_material_stick=短%s棍
gt.oreprefix.material_gear=%s齿轮
gt.oreprefix.small_material_gear=小型%s齿轮
gt.oreprefix.material_screw=%s螺丝
gt.oreprefix.material_bolt=%s螺栓
gt.oreprefix.material_rotor=%s转子
gt.oreprefix.material_ring=%s环
gt.oreprefix.material_foil=%s箔
gt.oreprefix.material_cell=%s单元
gt.oreprefix.material_plasma_cell=%s等离子体单元
gt.oreprefix.material_plasma=%s等离子体
gt.oreprefix.material_spring=%s弹簧
gt.oreprefix.small_material_spring=小型%s弹簧
gt.oreprefix.fine_material_wire=细%s导线
gt.oreprefix.material_frame_box=%s框架箱
gt.oreprefix.material_frame_box_tileentity=%s（方块实体）
gt.oreprefix.block_of_material=%s块
gt.oreprefix.material_ore=%s矿石
gt.oreprefix.small_material_ore=小型%s矿石
gt.oreprefix.raw_material_ore=原始%s矿石
gt.oreprefix.crushed_material_ore=破碎%s矿石
gt.oreprefix.centrifuged_material=离心分离%s
gt.oreprefix.centrifuged_material_ore=离心分离%s矿石
gt.oreprefix.centrifuged_material_crystals=离心分离%s晶体
gt.oreprefix.purified_material=纯化%s
gt.oreprefix.purified_material_ore=纯化%s矿石
gt.oreprefix.purified_material_crystals=纯化%s晶体
gt.oreprefix.purified_pile_of_material=纯化堆%s
gt.oreprefix.purified_pile_of_material_dust=纯化%s粉堆
gt.oreprefix.purified_pile_of_material_powder=纯化%s粉末堆
gt.oreprefix.purified_pile_of_material_crystal_powder=纯化%s晶粉堆
gt.oreprefix.impure_pile_of_material=不纯堆%s
gt.oreprefix.impure_pile_of_material_dust=不纯%s粉堆
gt.oreprefix.impure_pile_of_material_powder=不纯%s粉末堆
gt.oreprefix.impure_pile_of_material_crystal_powder=不纯%s晶粉堆
gt.oreprefix.small_pile_of_material=小堆%s
gt.oreprefix.small_pile_of_material_dust=小堆%s粉
gt.oreprefix.small_pile_of_material_powder=小堆%s粉末
gt.oreprefix.small_pile_of_material_pulp=小堆%s浆
gt.oreprefix.small_pile_of_material_crystal_powder=小堆%s晶粉
gt.oreprefix.tiny_pile_of_material=小撮%s
gt.oreprefix.tiny_pile_of_material_dust=小撮%s粉
gt.oreprefix.tiny_pile_of_material_powder=小撮%s粉末
gt.oreprefix.tiny_pile_of_material_pulp=小撮%s浆
gt.oreprefix.tiny_pile_of_material_crystal_powder=小撮%s晶粉
gt.oreprefix.ground_material=研磨%s
gt.oreprefix.material_crystal=%s晶体
gt.oreprefix.material_crystal_plate=%s晶体板
gt.oreprefix.material_crystal_powder=%s晶粉
gt.oreprefix.exquisite_material=精美%s
gt.oreprefix.exquisite_material_crystal=精美%s晶体
gt.oreprefix.flawless_material=无瑕%s
gt.oreprefix.flawless_material_crystal=无瑕%s晶体
gt.oreprefix.flawed_material=有瑕%s
gt.oreprefix.flawed_material_crystal=有瑕%s晶体
gt.oreprefix.chipped_material=碎裂%s
gt.oreprefix.chipped_material_crystal=碎裂%s晶体
gt.oreprefix.shard_of_material=%s碎片
gt.oreprefix.material_chip=%s芯片
gt.oreprefix.material_lens=%s透镜
gt.oreprefix.material_powder=%s粉末
gt.oreprefix.material_pulp=%s浆
gt.oreprefix.material_sheet=%s薄板
gt.oreprefix.material_sheetmetal=%s金属板
gt.oreprefix.double_material_sheet=双重%s薄板
gt.oreprefix.triple_material_sheet=三重%s薄板
gt.oreprefix.quadruple_material_sheet=四重%s薄板
gt.oreprefix.quintuple_material_sheet=五重%s薄板
gt.oreprefix.dense_material_sheet=致密%s薄板
gt.oreprefix.superdense_material_sheet=超致密%s薄板
gt.oreprefix.thin_material_sheet=薄%s板
gt.oreprefix.material_bar=%s棒
gt.oreprefix.material_casing=%s外壳
gt.oreprefix.material_round=%s圆片
gt.oreprefix.material_pane=%s玻璃板
gt.oreprefix.material_plank=%s木板
gt.oreprefix.material_ice=%s冰
gt.oreprefix.raw_material_ice=原始%s冰
gt.oreprefix.material_infused_stone=%s灌注石
gt.oreprefix.material_nanites=%s纳米机器人
gt.oreprefix.material_turbine_blade=%s涡轮叶片
gt.oreprefix.material_saw_blade=%s锯刃
gt.oreprefix.material_buzzsaw_blade=%s圆锯刃
gt.oreprefix.material_drill_tip=%s钻头
gt.oreprefix.material_chainsaw_tip=%s链锯刃
gt.oreprefix.material_wrench_tip=%s扳手头
gt.oreprefix.material_file_head=%s锉刀头
gt.oreprefix.material_hammer_head=%s锤头
gt.oreprefix.molten_material=熔融%s
gt.oreprefix.molten_material_cell=熔融%s单元
gt.oreprefix.lightly_hydro-cracked_material=轻度氢裂%s
gt.oreprefix.lightly_steam-cracked_material=轻度蒸汽裂%s
gt.oreprefix.lightly_hydro-cracked_material_cell=轻度氢裂%s单元
gt.oreprefix.lightly_steam-cracked_material_cell=轻度蒸汽裂%s单元
gt.oreprefix.moderately_hydro-cracked_material=中度氢裂%s
gt.oreprefix.moderately_steam-cracked_material=中度蒸汽裂%s
gt.oreprefix.moderately_hydro-cracked_material_cell=中度氢裂%s单元
gt.oreprefix.moderately_steam-cracked_material_cell=中度蒸汽裂%s单元
gt.oreprefix.severely_hydro-cracked_material=重度氢裂%s
gt.oreprefix.severely_steam-cracked_material=重度蒸汽裂%s
gt.oreprefix.severely_hydro-cracked_material_cell=重度氢裂%s单元
gt.oreprefix.severely_steam-cracked_material_cell=重度蒸汽裂%s单元

# 线缆（带绝缘层）
gt.oreprefix.1x_material_cable=1x %s线缆
gt.oreprefix.2x_material_cable=2x %s线缆
gt.oreprefix.4x_material_cable=4x %s线缆
gt.oreprefix.8x_material_cable=8x %s线缆
gt.oreprefix.12x_material_cable=12x %s线缆
gt.oreprefix.16x_material_cable=16x %s线缆

# 导线（无绝缘层）
gt.oreprefix.1x_material_wire=1x %s导线
gt.oreprefix.2x_material_wire=2x %s导线
gt.oreprefix.4x_material_wire=4x %s导线
gt.oreprefix.8x_material_wire=8x %s导线
gt.oreprefix.12x_material_wire=12x %s导线
gt.oreprefix.16x_material_wire=16x %s导线

# 流体管道
gt.oreprefix.tiny_material_fluid_pipe=微型%s流体管道
gt.oreprefix.small_material_fluid_pipe=小型%s流体管道
gt.oreprefix.material_fluid_pipe=%s流体管道
gt.oreprefix.large_material_fluid_pipe=大型%s流体管道
gt.oreprefix.huge_material_fluid_pipe=超大型%s流体管道
gt.oreprefix.quadruple_material_fluid_pipe=四联%s流体管道
gt.oreprefix.nonuple_material_fluid_pipe=九联%s流体管道

# 物品管道
gt.oreprefix.tiny_material_item_pipe=微型%s物品管道
gt.oreprefix.small_material_item_pipe=小型%s物品管道
gt.oreprefix.material_item_pipe=%s物品管道
gt.oreprefix.large_material_item_pipe=大型%s物品管道
gt.oreprefix.huge_material_item_pipe=超大型%s物品管道
gt.oreprefix.tiny_restrictive_material_item_pipe=微型限制性%s物品管道
gt.oreprefix.small_restrictive_material_item_pipe=小型限制性%s物品管道
gt.oreprefix.restrictive_material_item_pipe=限制性%s物品管道
gt.oreprefix.large_restrictive_material_item_pipe=大型限制性%s物品管道
gt.oreprefix.huge_restrictive_material_item_pipe=超大型限制性%s物品管道

# 特殊物品（无材料参数）
gt.oreprefix.cardboard=硬纸板
gt.oreprefix.carton=纸箱
gt.oreprefix.thick_cardboard=厚纸板
gt.oreprefix.paperboard=纸板
gt.oreprefix.flour=面粉
gt.oreprefix.crushed_ice=碎冰
gt.oreprefix.mince_meat=碎肉
gt.oreprefix.cooked_mince_meat=熟碎肉
gt.oreprefix.chad=纸屑
gt.oreprefix.small_pile_of_bone_meal=小堆骨粉
gt.oreprefix.small_pile_of_flour=小堆面粉
gt.oreprefix.small_pile_of_crushed_ice=小堆碎冰
gt.oreprefix.small_pile_of_mince_meat=小堆碎肉（不存在于en_US.lang，可忽略）
gt.oreprefix.small_pile_of_cooked_mince_meat=小堆熟碎肉
gt.oreprefix.small_pile_of_chad=小堆纸屑
gt.oreprefix.tiny_pile_of_bone_meal=小撮骨粉
gt.oreprefix.tiny_pile_of_flour=小撮面粉
gt.oreprefix.tiny_pile_of_crushed_ice=小撮碎冰
gt.oreprefix.tiny_pile_of_mince_meat=小撮碎肉
gt.oreprefix.tiny_pile_of_cooked_mince_meat=小撮熟碎肉
gt.oreprefix.tiny_pile_of_chad=小撮纸屑
gt.oreprefix.small_pile_of_mince_meat=小堆碎肉
```

> ⚠️ **注意**：以上翻译建议仅供参考，请根据 GTNH 汉化包现有的翻译风格和术语体系（如 ParaTranz 项目中的已有术语）进行确认和调整。

---

## 验证方法

修改完成后，将文件覆盖到对应目录，进入游戏后检查：
- 锡锭（Tin Ingot）是否显示为 `锡锭` 而非 `锡 Ingot`
- 铜粉（Copper Dust）是否显示为 `铜粉` 而非 `铜 Dust`
- 铁板（Iron Plate）是否显示为 `铁板` 而非 `铁 Plate`

---

## 附录：GT5-Unofficial 中的 key 生成代码（OrePrefixes.java）

```java
// 以 ingot（锭）为例，getDefaultLocalNameFormatForItem 返回 "%material Ingot"
// getOreprefixKey 处理后得到 "gt.oreprefix.material_ingot"
// StatCollector.translateToLocalFormatted("gt.oreprefix.material_ingot", "锡") 
// 若 zh_CN.lang 中有 gt.oreprefix.material_ingot=%s锭，则输出 "锡锭"
// 若没有，则回退到 en_US.lang 的 gt.oreprefix.material_ingot=%s Ingot，输出 "锡 Ingot"

public String getOreprefixKey(IOreMaterial materials) {
    return "gt.oreprefix." + this.getDefaultLocalNameFormatForItem(materials)
        .toLowerCase()
        .replace(" ", "_")
        .replace("%material", "material");
}
```

---

## 相关仓库和文件

| 仓库 | 文件 | 说明 |
|------|------|------|
| [czqwq/GT5-Unofficial](https://github.com/czqwq/GT5-Unofficial) | `src/main/resources/assets/gregtech/lang/en_US.lang` | 英文原文，包含 169 条 `gt.oreprefix.*` key |
| [czqwq/GT5-Unofficial](https://github.com/czqwq/GT5-Unofficial) | `src/main/java/gregtech/api/enums/OrePrefixes.java` | 生成 oreprefix key 的核心逻辑 |
| [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) | `resources/GregTech[gregtech]/lang/zh_CN.lang` | **需修改**：旧 `gt.component.*` 替换为新 `gt.oreprefix.*` |
| [Kiwi233/Translation-of-GTNH](https://github.com/Kiwi233/Translation-of-GTNH) | `resources/GregTech(+16)[gregtech]/lang/zh_CN.lang` | **需修改**：同上 |
