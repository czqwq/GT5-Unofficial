-- ============================================================
-- blackhole_controller.lua  v2.0
-- OpenComputers 黑洞压缩机（Pseudostable Black Hole
-- Containment Field，BHC）自动化控制脚本
--
-- 改进点（相较于原版 blackhole.lua）：
--   · 彩色 UI，带进度条与运行时间显示
--   · 支持"黑洞多功能仓"（MTEBlackHoleUtility）红石信号检测
--     ——可实时判断黑洞开闭状态，无需额外轮询
--   · 全局配置表，便于调整而无需深入读代码
--   · 分模块（UI / Machine / Items / ME / Utility）
--   · 更健壮的关闭流程与异常恢复
--   · 用 pcall 保护主循环，崩溃时自动关机并恢复终端
--
-- 多功能仓说明（MTEBlackHoleUtility）：
--   · "静态模式"：黑洞开启期间持续输出红石信号 15
--   · "脉冲模式"：黑洞开启时每秒发出一个 5 tick（0.25 s）脉冲
--   · 将 CFG.utilityHatchSide 设为对应方向即可启用检测；
--     设为 nil 则完全依赖机器轮询（不影响其他功能）
--
-- 组件需求：
--   · gpu（显示器）
--   · transposer（转运器，连接放种子/坍缩器的缓存箱）
--   · redstone（红石 I/O，输出时空流体控制信号）
--   · me_controller（AE2 ME 控制器，判断网络是否有内容）
--   · gt_machine（OC 适配器连接到黑洞压缩机控制器方块）
-- ============================================================

local component = require("component")
local computer  = require("computer")
local sides     = require("sides")

-- ==================== 配置区（按需修改） ====================
local CFG = {

    -- 【方向】 ------------------------------------------------
    -- 转运器读取种子 / 坍缩器的方向（连接缓存箱一侧）
    sourceSide       = sides.north,
    -- 转运器输出到机器输入仓的方向
    targetSide       = sides.south,
    -- 红石 I/O 向时空注入仓发出开关信号的方向
    --（信号 15 = 允许注入时空；信号 0 = 停止注入）
    rsSideSpacetime  = sides.up,
    -- 【可选】多功能仓红石输出进入 OC 红石 I/O 的方向
    --   · 若未安装多功能仓，请保持 nil
    --   · 多功能仓建议设为"静态模式"（黑洞开时持续输出15）
    utilityHatchSide = nil,   -- 示例: sides.east

    -- 【槽位】（缓存箱内） ------------------------------------
    seedSlot         = 1,   -- 黑洞种子（Black Hole Seed）
    collapseSlot     = 2,   -- 黑洞坍缩器（Black Hole Collapser）

    -- 【时间（秒）】 ------------------------------------------
    -- ★ 关键：stability 从 100 开始以 1/s 速率自然下降：
    --   · stability < 50 → 并行数 ×2
    --   · stability < 20 → 并行数 ×4（最大并行！）
    --   · stability <  0 → 黑洞不稳定，配方会被清空
    -- 因此在启用时空信号"冻结"稳定性之前，必须等待稳定性
    -- 自然衰减到 < 20，才能达到最大并行。
    --   stabilizeWait = 82 s → stability ≈ 18（< 20，安全达最大并行）
    --   stabilizeWait 不应超过 100 s，否则稳定性归零机器进入不稳定态。
    stabilizeWait    = 82,
    -- 单轮最长运行时间，超时后自动重启黑洞（防止异常卡死）
    -- 重启会将 stability 重置为 100，并重新等待衰减至 < 20
    maxRunTime       = 300,
    -- 主循环轮询间隔（秒）
    pollInterval     = 1.0,

    -- 【显示】 ------------------------------------------------
    screenWidth      = 46,
    screenHeight     = 12,
    -- 颜色（0xRRGGBB）
    clrNormal  = 0x00FF88,  -- 正常 / 运行中
    clrWarning = 0xFFAA00,  -- 警告 / 过渡
    clrError   = 0xFF4444,  -- 错误
    clrIdle    = 0x888888,  -- 空闲
    clrTitle   = 0x00CCFF,  -- 标题
}
-- =============================================================


-- ===================== 组件绑定 ==============================
local gpu       = component.gpu
local transpos  = component.transposer
local redstone  = component.redstone
local me        = component.me_controller

-- 自动发现所有连接的黑洞压缩机
local machines = {}
for addr, _ in component.list("gt_machine") do
    if component.invoke(addr, "getName") == "multimachine.blackholecompressor" then
        table.insert(machines, addr)
    end
end
assert(#machines > 0,
    "未找到黑洞压缩机！请检查 OC 适配器是否正确连接到机器控制器方块。")


-- ===================== UI 模块 ===============================
local UI = {}

-- 内部状态缓存（避免每帧全屏重绘）
local _ui = {
    status = "", info1 = "", info2 = "",
    elapsed = 0, total = 0, color = CFG.clrNormal,
}

local function _padRight(s, n)
    local pad = n - #s
    if pad <= 0 then return s end
    return s .. string.rep(" ", pad)
end

function UI.init()
    local ok = pcall(function()
        gpu.setResolution(CFG.screenWidth, CFG.screenHeight)
    end)
    if not ok then
        -- 分辨率不支持时退而求其次
        gpu.setViewport(CFG.screenWidth, CFG.screenHeight)
    end
    gpu.setBackground(0x000000)
    -- 清屏
    gpu.fill(1, 1, CFG.screenWidth, CFG.screenHeight, " ")
    -- 固定标题行
    gpu.setForeground(CFG.clrTitle)
    gpu.set(1, 1, _padRight(
        string.format("  ◆ BHC 自动控制器  [%d 台机器]  ", #machines),
        CFG.screenWidth))
    gpu.setForeground(0x336688)
    gpu.set(1, 2, string.rep("─", CFG.screenWidth))
    gpu.set(1, 6, string.rep("─", CFG.screenWidth))
    gpu.set(1, 10, string.rep("─", CFG.screenWidth))
end

function UI.update(status, info1, info2, elapsed, total, color)
    _ui.status  = status  or _ui.status
    _ui.info1   = info1   or ""
    _ui.info2   = info2   or ""
    _ui.elapsed = elapsed or 0
    _ui.total   = total   or 0
    _ui.color   = color   or CFG.clrNormal

    gpu.setForeground(_ui.color)

    -- 行 3：状态
    gpu.set(1, 3, _padRight("  状态: " .. _ui.status, CFG.screenWidth))
    -- 行 4：信息1
    gpu.set(1, 4, _padRight("  " .. _ui.info1, CFG.screenWidth))
    -- 行 5：信息2
    gpu.set(1, 5, _padRight("  " .. _ui.info2, CFG.screenWidth))

    -- 行 7-9：进度条区域
    if _ui.total > 0 then
        gpu.setForeground(_ui.color)
        local barW  = CFG.screenWidth - 4
        local pct   = math.min(1.0, _ui.elapsed / _ui.total)
        local fill  = math.floor(pct * barW)
        local bar   = "  [" .. string.rep("█", fill)
                             .. string.rep("░", barW - fill) .. "]"
        gpu.set(1, 7, _padRight(bar, CFG.screenWidth))
        gpu.set(1, 8, _padRight(
            string.format("  进度: %d / %d 秒  (%.0f%%)",
                math.floor(_ui.elapsed), _ui.total, pct * 100),
            CFG.screenWidth))
    else
        gpu.fill(1, 7, CFG.screenWidth, 2, " ")
    end

    -- 行 11：系统运行时间（灰色）
    gpu.setForeground(0x555555)
    gpu.set(1, 11, _padRight(
        string.format("  系统运行: %.0f 秒", computer.uptime()),
        CFG.screenWidth))
end


-- ===================== Machine 模块 ==========================
local Machine = {}

function Machine.setWorkAllowed(enabled)
    for _, addr in ipairs(machines) do
        component.invoke(addr, "setWorkAllowed", enabled)
    end
end

function Machine.anyRunning()
    for _, addr in ipairs(machines) do
        if component.invoke(addr, "getWorkProgress") ~= 0 then
            return true
        end
    end
    return false
end

-- 返回所有机器中最大的剩余 tick 数
function Machine.maxRemainingTicks()
    local maxTicks = 0
    for _, addr in ipairs(machines) do
        local prog   = component.invoke(addr, "getWorkProgress")
        local maxP   = component.invoke(addr, "getWorkMaxProgress")
        local remain = maxP - prog
        if remain > maxTicks then maxTicks = remain end
    end
    return maxTicks
end


-- ===================== Items 模块 ============================
local Items = {}

-- 返回 (seedOK, collapseOK, seedCount, collapseCount)
function Items.available()
    local seeds   = transpos.getSlotStackSize(CFG.sourceSide, CFG.seedSlot)
    local closers = transpos.getSlotStackSize(CFG.sourceSide, CFG.collapseSlot)
    return seeds >= #machines, closers >= #machines, seeds, closers
end

function Items.transferSeeds()
    transpos.transferItem(CFG.sourceSide, CFG.targetSide,
        #machines, CFG.seedSlot, 2)
end

function Items.transferClosers()
    transpos.transferItem(CFG.sourceSide, CFG.targetSide,
        #machines, CFG.collapseSlot, 2)
end


-- ===================== ME 模块 ===============================
local ME = {}

function ME.hasContent()
    return me.getItemsInNetwork()[1]  ~= nil
        or me.getFluidsInNetwork()[1] ~= nil
end


-- ===================== Utility Hatch 模块 ====================
-- 黑洞多功能仓（MTEBlackHoleUtility）检测
-- 当 CFG.utilityHatchSide ~= nil 时启用；
-- 建议将多功能仓设为"静态模式"，黑洞开启时持续输出红石 15。
local Utility = {}

-- 返回 true/false（已配置），或 nil（未配置，不可用）
function Utility.isBlackHoleActive()
    if CFG.utilityHatchSide == nil then return nil end
    return redstone.getInput(CFG.utilityHatchSide) > 0
end

-- 等待多功能仓信号变为目标值；超时返回 false
-- targetActive: true = 等黑洞打开，false = 等黑洞关闭
-- timeout: 最长等待秒数
function Utility.waitForState(targetActive, timeout)
    if CFG.utilityHatchSide == nil then return true end  -- 未配置，直接通过
    local deadline = computer.uptime() + (timeout or 120)
    while computer.uptime() < deadline do
        if Utility.isBlackHoleActive() == targetActive then return true end
        os.sleep(0.5)
    end
    return false  -- 超时
end


-- ===================== 关闭流程 ==============================
-- 停止机器 → 投放坍缩器 → 等待所有配方结束 → 关闭时空信号
local function shutdown(reason)
    Machine.setWorkAllowed(false)

    local remainTicks = Machine.maxRemainingTicks()
    local waitSec     = math.ceil(remainTicks / 20)

    Items.transferClosers()

    local t0 = computer.uptime()
    while Machine.anyRunning() do
        local elapsed = math.floor(computer.uptime() - t0)
        UI.update("关闭中",
            reason or "关闭黑洞中...",
            string.format("等待配方结束  %d / %d 秒", elapsed, waitSec),
            elapsed, waitSec, CFG.clrWarning)
        os.sleep(1)
    end

    -- 若配置了多功能仓，等待其红石信号归零（黑洞已关闭）
    if CFG.utilityHatchSide ~= nil then
        Utility.waitForState(false, 30)
    end

    -- 二次确认：让机器跑半秒再关，防止物品卡在输入仓
    Machine.setWorkAllowed(true)
    os.sleep(0.5)
    Machine.setWorkAllowed(false)
    redstone.setOutput(CFG.rsSideSpacetime, 0)
end


-- ===================== 等待材料 ==============================
local function waitForMaterials()
    while true do
        local ok1, ok2, sc, cc = Items.available()
        if ok1 and ok2 then return end
        UI.update("等待材料",
            string.format("种子: %d / %d    坍缩器: %d / %d",
                sc, #machines, cc, #machines),
            "请向缓存箱补充物品，每隔 5 s 重新检测...",
            0, 0, CFG.clrError)
        os.sleep(5)
    end
end


-- ===================== 主控制循环 ============================
local function main()
    UI.init()
    Machine.setWorkAllowed(false)
    redstone.setOutput(CFG.rsSideSpacetime, 0)
    UI.update("空闲", "等待 ME 网络出现内容...", "", 0, 0, CFG.clrIdle)

    while true do
        os.sleep(CFG.pollInterval)

        if not ME.hasContent() then
            UI.update("空闲", "等待 ME 网络出现内容...", "", 0, 0, CFG.clrIdle)
            goto continue
        end

        -- ── ME 有内容，启动一轮处理 ─────────────────────────
        ::restart::

        -- 1. 确保缓存箱内种子与坍缩器数量充足
        waitForMaterials()

        -- 2. 投放种子，开启黑洞
        Items.transferSeeds()
        Machine.setWorkAllowed(true)

        -- 3. 等待稳定阶段
        --    策略：不开时空信号，让 stability 自然衰减。
        --    stability = 100 − elapsed（秒）：
        --      · elapsed > 50 s → stability < 50 → 并行 ×2
        --      · elapsed > 80 s → stability < 20 → 并行 ×4（最大！）
        --    stabilizeWait 默认 82 s，确保时空信号开启时
        --    stability ≈ 18，机器已处于最大并行模式。
        local t0 = computer.uptime()
        while computer.uptime() < t0 + CFG.stabilizeWait do
            local elapsed = math.floor(computer.uptime() - t0)

            -- 检测多功能仓状态（如已配置）
            local hatchInfo = ""
            local hatchActive = Utility.isBlackHoleActive()
            if hatchActive ~= nil then
                hatchInfo = "  多功能仓: " .. (hatchActive and "★ 活跃" or "◌ 关闭")
            end

            -- stability ≈ 100 - elapsed（最小为 0）
            local estStability = math.max(0, 100 - elapsed)
            local parallelMul  = 1
            if estStability < 20 then parallelMul = 4
            elseif estStability < 50 then parallelMul = 2
            end
            UI.update("稳定等待",
                string.format("stability ≈ %d  并行: ×%d  (%d / %d 秒)",
                    estStability, parallelMul, elapsed, CFG.stabilizeWait),
                string.format("机器数: %d%s", #machines, hatchInfo),
                elapsed, CFG.stabilizeWait,
                parallelMul == 4 and CFG.clrNormal or CFG.clrWarning)

            os.sleep(1)

            -- ME 意外变空 → 提前收工
            if not ME.hasContent() then
                shutdown("ME 已清空（稳定等待阶段）")
                UI.update("空闲", "ME 已清空，等待下次任务...",
                    "", 0, 0, CFG.clrIdle)
                goto continue
            end
        end

        -- 4. 开启时空信号，进入正式运行阶段
        --    此时 stability ≈ 18（< 20），机器处于最大并行（×4）。
        --    时空流体注入可阻止 stability 继续下降（冻结在当前值）：
        --      · 每秒消耗 1 L 时空可将衰减归零
        --      · 每累计节省 30 s 后，每秒消耗量翻倍
        --    若时空供应中断，stability 继续下降直至 < 0 进入不稳定态。
        redstone.setOutput(CFG.rsSideSpacetime, 15)
        t0 = computer.uptime()

        while ME.hasContent() do
            local elapsed = math.floor(computer.uptime() - t0)

            local hatchInfo = ""
            local hatchActive = Utility.isBlackHoleActive()
            if hatchActive ~= nil then
                hatchInfo = "  多功能仓: " .. (hatchActive and "★ 活跃" or "◌ 关闭")
            end

            -- 开启时空后 stability 冻结在 stabilizeWait 时的值
            local frozenStability = math.max(0, 100 - CFG.stabilizeWait)
            local pMul = frozenStability < 20 and "×4(MAX)" or
                         (frozenStability < 50 and "×2" or "×1")
            UI.update("运行中",
                string.format("处理 ME 网络内容  并行: %s  (%d / %d 秒)",
                    pMul, elapsed, CFG.maxRunTime),
                string.format("机器数: %d%s", #machines, hatchInfo),
                elapsed, CFG.maxRunTime, CFG.clrNormal)

            os.sleep(1)

            -- 运行超时 → 重启黑洞（防止 stability 耗尽导致黑洞崩溃）
            if computer.uptime() >= t0 + CFG.maxRunTime then
                UI.update("重启中",
                    "运行时间过长，主动重启黑洞以重置 stability...",
                    "", 0, 0, CFG.clrWarning)
                shutdown("运行超时，重启黑洞")
                goto restart
            end
        end

        -- 5. ME 已清空，正常关闭
        shutdown("ME 已清空")
        UI.update("空闲", "等待 ME 网络出现内容...", "", 0, 0, CFG.clrIdle)

        ::continue::
    end  -- while true
end


-- ===================== 入口与清理 ============================
local ok, err = pcall(main)

-- 无论如何都执行清理，防止机器悬空运行
Machine.setWorkAllowed(false)
while Machine.anyRunning() do os.sleep(0.5) end
redstone.setOutput(CFG.rsSideSpacetime, 0)

-- 恢复终端
gpu.setForeground(0xFFFFFF)
gpu.setBackground(0x000000)
pcall(function()
    gpu.setResolution(gpu.maxResolution())
end)

if not ok then
    -- 重新抛出，让 OC shell 显示错误信息
    error(err, 0)
end
