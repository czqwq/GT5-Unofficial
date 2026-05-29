-- blackhole_controller.lua
-- BHC（黑洞压缩机）自动化控制脚本
--
-- 所需组件：
--   gpu / transposer / redstone / me_controller / gt_machine（OC 适配器接控制器）
-- 多功能仓（MTEBlackHoleUtility）：
--   静态模式——黑洞开启时持续输出红石 15，推荐使用。
--   将 CFG.utilityHatchSide 设为对应方向启用；nil 表示不使用。

local component = require("component")
local computer  = require("computer")
local sides     = require("sides")
local unicode   = require("unicode")

-- ==================== 配置区（按需修改） ====================
local CFG = {
    -- 方向：转运器来源/目标，时空信号输出，多功能仓信号输入
    sourceSide       = sides.north,
    targetSide       = sides.south,
    rsSideSpacetime  = sides.up,
    utilityHatchSide = nil,   -- 多功能仓方向，不用则填 nil

    -- 缓存箱槽位
    seedSlot         = 1,   -- 黑洞种子
    collapseSlot     = 2,   -- 黑洞坍缩器

    -- 时间（秒）
    -- stability 从 100 以 1/s 衰减：<50 并行×2，<20 并行×4
    -- 82s 后 stability ≈ 18，刚好达到最大并行；不要超过 100s
    stabilizeWait    = 82,
    maxRunTime       = 300,  -- 单轮超时后自动重启黑洞
    pollInterval     = 1.0,

    -- 显示
    screenWidth      = 46,
    screenHeight     = 12,
    clrNormal  = 0x00FF88,
    clrWarning = 0xFFAA00,
    clrError   = 0xFF4444,
    clrIdle    = 0x888888,
    clrTitle   = 0x00CCFF,
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

local _ui = {
    status = "", info1 = "", info2 = "",
    elapsed = 0, total = 0, color = CFG.clrNormal,
}

-- 用显示宽度（而非字节数）填充到 n 列，修复中文字符撑不满行的问题
local function _padRight(s, n)
    local pad = n - unicode.wlen(s)
    if pad <= 0 then return s end
    return s .. string.rep(" ", pad)
end

function UI.init()
    local ok = pcall(function()
        gpu.setResolution(CFG.screenWidth, CFG.screenHeight)
    end)
    if not ok then
        gpu.setViewport(CFG.screenWidth, CFG.screenHeight)
    end
    gpu.setBackground(0x000000)
    gpu.fill(1, 1, CFG.screenWidth, CFG.screenHeight, " ")
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
    gpu.set(1, 3, _padRight("  状态: " .. _ui.status, CFG.screenWidth))
    gpu.set(1, 4, _padRight("  " .. _ui.info1, CFG.screenWidth))
    gpu.set(1, 5, _padRight("  " .. _ui.info2, CFG.screenWidth))

    -- 进度条（行 7-8）
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

    -- 运行时间（行 11，灰色）
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

-- 返回所有机器中最大的剩余 tick 数（用于估算等待时间）
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
-- 读取多功能仓红石信号判断黑洞状态（需配置 utilityHatchSide）
local Utility = {}

-- 返回 true/false，未配置则返回 nil
function Utility.isBlackHoleActive()
    if CFG.utilityHatchSide == nil then return nil end
    return redstone.getInput(CFG.utilityHatchSide) > 0
end

-- 等待信号达到目标状态，超时返回 false
function Utility.waitForState(targetActive, timeout)
    if CFG.utilityHatchSide == nil then return true end
    local deadline = computer.uptime() + (timeout or 120)
    while computer.uptime() < deadline do
        if Utility.isBlackHoleActive() == targetActive then return true end
        os.sleep(0.5)
    end
    return false
end


-- ===================== 关闭流程 ==============================
-- spacetimeOn: 调用时时空是否已开启
--   true  → 保持时空供应直到配方结束，防止 stability 继续下降吞噬输出
--   false → 不开时空（稳定等待阶段 stability 充足，无需供应）
local function shutdown(reason, spacetimeOn)
    if spacetimeOn then
        redstone.setOutput(CFG.rsSideSpacetime, 15)
    end
    Machine.setWorkAllowed(false)

    local remainTicks = Machine.maxRemainingTicks()
    local waitSec     = math.ceil(remainTicks / 20)

    Items.transferClosers()   -- 投入坍缩器，配方跑完后机器自动关闭黑洞

    -- 等待所有配方结束
    local t0 = computer.uptime()
    while Machine.anyRunning() do
        local elapsed = math.floor(computer.uptime() - t0)
        UI.update("关闭中",
            reason or "关闭黑洞中...",
            string.format("等待配方结束  %d / %d 秒  [时空保护中]", elapsed, waitSec),
            elapsed, waitSec, CFG.clrWarning)
        os.sleep(1)
    end

    -- 若配置了多功能仓，确认黑洞已关闭
    if CFG.utilityHatchSide ~= nil then
        Utility.waitForState(false, 30)
    end

    -- 短暂重启，让机器消化坍缩器（防止物品卡在输入仓）
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

        -- ME 有内容，启动一轮处理
        ::restart::

        -- 1. 确保缓存箱内种子与坍缩器数量充足
        waitForMaterials()

        -- 2. 投放种子，开启黑洞
        Items.transferSeeds()
        Machine.setWorkAllowed(true)

        -- 3. 稳定等待阶段：不开时空，让 stability 自然衰减
        --    stability = 100 − elapsed，<50 并行×2，<20 并行×4
        --    等 stabilizeWait 秒后 stability ≈ 18，达到最大并行
        local t0 = computer.uptime()
        while computer.uptime() < t0 + CFG.stabilizeWait do
            local elapsed = math.floor(computer.uptime() - t0)

            local hatchInfo = ""
            local hatchActive = Utility.isBlackHoleActive()
            if hatchActive ~= nil then
                hatchInfo = "  多功能仓: " .. (hatchActive and "★ 活跃" or "◌ 关闭")
            end

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

            -- ME 意外清空 → 提前关闭（稳定等待阶段时空未开，不需要供应）
            if not ME.hasContent() then
                shutdown("ME 已清空（稳定等待阶段）", false)
                UI.update("空闲", "ME 已清空，等待下次任务...",
                    "", 0, 0, CFG.clrIdle)
                goto continue
            end
        end

        -- 4. 开启时空信号，冻结 stability，进入正式运行
        --    每 30s 消耗量翻倍；供应中断则 stability 继续衰减
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

            -- 运行超时 → 重启黑洞，重置 stability
            if computer.uptime() >= t0 + CFG.maxRunTime then
                UI.update("重启中",
                    "运行时间过长，主动重启黑洞以重置 stability...",
                    "", 0, 0, CFG.clrWarning)
                shutdown("运行超时，重启黑洞", true)
                goto restart
            end
        end

        -- 5. ME 已清空，正常关闭（时空已开，保持供应直到配方结束）
        shutdown("ME 已清空", true)
        UI.update("空闲", "等待 ME 网络出现内容...", "", 0, 0, CFG.clrIdle)

        ::continue::
    end
end


-- ===================== 入口与清理 ============================
local ok, err = pcall(main)

-- 脚本退出时确保机器停止、时空关闭
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
    error(err, 0)
end
