<script lang="ts">
import { onDestroy, onMount } from "svelte";
import { renderIcon } from "../../utils/widget-icons";

// 数据源：时间雨 API
//   GET {API_BASE}/group-map                -> { "雨核": ["yuhe-pc", "yuhe-sanxing"], ... }
//   GET {API_BASE}/v2/status?machine=<名>   -> 单个设备状态对象
// 组件设计参考 https://shijian.07210700.xyz/ ：
//   设备清单自动发现、在线汇总、倒计时自动刷新、手动刷新、隐私模式提示。
const API_BASE = "https://shijian.07210700.xyz/api";

/** 自动刷新间隔（与上游一致的 3 分钟） */
const REFRESH_INTERVAL = 3 * 60 * 1000;
/** 单次请求超时 */
const FETCH_TIMEOUT = 12 * 1000;
/** 超过该时长未上传数据视为离线（3 分钟） */
const OFFLINE_THRESHOLD = 3 * 60 * 1000;
/** 在 group-map 里取哪一组的设备 */
const GROUP_NAME = "雨核";

interface Activity {
	machine?: string;
	window_title?: string | null;
	app?: string | null;
	access_time?: string | null;
	privacy_mode?: boolean;
	extra?: DeviceInfo | null;
}

interface DeviceInfo {
	battery?: { level?: number | null; charging?: boolean } | null;
	network?: { wifi?: boolean; type?: string } | null;
	screen?: { on?: boolean } | null;
	os?: string | null;
	client_version?: string | null;
}

interface MediaData {
	title?: string;
	artist?: string;
	status?: string;
	source?: string;
}

interface Media {
	window_title?: string;
	app?: string;
	data?: MediaData;
}

interface StatusData {
	machine: string;
	last_seen?: string;
	activity?: Activity | null;
	media?: Media | null;
	device?: DeviceInfo | null;
}

interface DeviceConfig {
	machine: string;
	name: string;
	kind: "desktop" | "phone";
}

/** 已知设备的友好名称与类型；其余设备按名字猜类型 */
const KNOWN_DEVICES: Record<string, { name: string; kind: "desktop" | "phone" }> = {
	"yuhe-pc": { name: "雨核的电脑", kind: "desktop" },
	"yuhe-sanxing": { name: "雨核的手机", kind: "phone" },
};

const FALLBACK_DEVICES: DeviceConfig[] = [
	{ machine: "yuhe-pc", name: "雨核的电脑", kind: "desktop" },
	{ machine: "yuhe-sanxing", name: "雨核的手机", kind: "phone" },
];

function describeMachine(machine: string): DeviceConfig {
	const known = KNOWN_DEVICES[machine];
	if (known) return { machine, ...known };
	const lower = machine.toLowerCase();
	const isDesktop = /(pc|desktop|mac|macbook|legion|thinkpad|linux|imac|mini|windows|xps|surface)/.test(
		lower,
	);
	return { machine, name: machine, kind: isDesktop ? "desktop" : "phone" };
}

let devices: DeviceConfig[] = FALLBACK_DEVICES;
let statuses: Record<string, StatusData | null> = {};
let loading = true;
let refreshing = false;
let error: string | null = null;
let lastUpdated: number | null = null;
let nextRefreshAt = 0;
let now = Date.now();
let ticker: ReturnType<typeof setInterval> | undefined;

onMount(async () => {
	await ensureDevices();
	await fetchAll();
	ticker = setInterval(tick, 1000);
});

onDestroy(() => {
	if (ticker) clearInterval(ticker);
});

function tick() {
	now = Date.now();
	if (nextRefreshAt && now >= nextRefreshAt) {
		void fetchAll();
	}
}

/** 带超时的 JSON 请求（对应上游的 12s AbortController） */
async function fetchJson<T>(url: string): Promise<T> {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
	try {
		const res = await fetch(url, {
			signal: controller.signal,
			cache: "no-store",
		});
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		return (await res.json()) as T;
	} finally {
		clearTimeout(timer);
	}
}

/** 用 group-map 自动发现「雨核」名下的设备，失败时回退到写死的两台 */
async function ensureDevices() {
	try {
		const map = await fetchJson<Record<string, string[]>>(`${API_BASE}/group-map`);
		const list = map?.[GROUP_NAME];
		if (Array.isArray(list) && list.length > 0) {
			devices = list.map(describeMachine);
		}
	} catch (err) {
		console.warn("获取视奸名单失败，使用默认设备列表:", err);
	}
}

async function fetchAll() {
	refreshing = true;
	error = null;
	const timestamp = Date.now();
	const targets = devices;
	try {
		const results = await Promise.allSettled(
			targets.map((d) =>
				fetchJson<StatusData | StatusData[]>(
					`${API_BASE}/v2/status?machine=${encodeURIComponent(d.machine)}&_t=${timestamp}`,
				),
			),
		);

		const next: Record<string, StatusData | null> = {};
		let failed = 0;
		results.forEach((result, index) => {
			const machine = targets[index].machine;
			if (result.status === "fulfilled") {
				const json = result.value;
				next[machine] = (Array.isArray(json) ? json[0] : json) ?? null;
			} else {
				// 单台失败时保留上一次的数据，避免侧栏整块闪成「暂无数据」
				next[machine] = statuses[machine] ?? null;
				failed += 1;
			}
		});

		statuses = next;
		if (failed === targets.length) error = "状态获取失败";
		lastUpdated = Date.now();
	} finally {
		loading = false;
		refreshing = false;
		nextRefreshAt = Date.now() + REFRESH_INTERVAL;
	}
}

function getLastSeen(data: StatusData | null): string | undefined {
	if (!data) return undefined;
	return data.last_seen || data.activity?.access_time || undefined;
}

function isOnline(data: StatusData | null): boolean {
	const lastSeen = getLastSeen(data);
	if (!lastSeen) return false;
	const t = new Date(lastSeen).getTime();
	if (Number.isNaN(t)) return false;
	return Date.now() - t <= OFFLINE_THRESHOLD;
}

/**
 * 在线台数。
 * 参数显式传入（而不是闭包读取）是为了让下面的 $: 能静态收集到 statuses 依赖——
 * Svelte 的旧式响应式只根据 $: 语句里出现的变量推断依赖，
 * 写成 onlineCount() 这种闭包调用会导致 statuses 变化时数字不刷新。
 */
function countOnline(
	map: Record<string, StatusData | null>,
	list: DeviceConfig[],
): number {
	return list.filter((d) => isOnline(map[d.machine] ?? null)).length;
}

function formatClock(time: string | undefined | null): string {
	if (!time) return "未知时间";
	const date = new Date(time);
	if (Number.isNaN(date.getTime())) return "未知时间";
	return date.toLocaleString("zh-CN", {
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
		hour12: false,
	});
}

function formatRelativeTime(time: string | undefined | null): string {
	if (!time) return "未知时间";
	const t = new Date(time).getTime();
	if (Number.isNaN(t)) return "未知时间";
	const diff = Date.now() - t;
	if (diff < 0) return "刚刚";
	const seconds = Math.floor(diff / 1000);
	if (seconds < 60) return "刚刚";
	const minutes = Math.floor(seconds / 60);
	if (minutes < 60) return `${minutes} 分钟前`;
	const hours = Math.floor(minutes / 60);
	if (hours < 24) return `${hours} 小时前`;
	return `${Math.floor(hours / 24)} 天前`;
}

/** 当前活动：窗口标题优先，其次应用名 */
function getActivity(data: StatusData | null): { text: string; app: string } {
	if (!data) return { text: "暂无设备状态", app: "" };
	const activity = data.activity;
	if (activity?.privacy_mode) return { text: "开启了隐私模式", app: "" };
	const title = (activity?.window_title || "").trim();
	const app = (activity?.app || "").trim();
	if (title) return { text: title, app };
	if (app) return { text: app, app: "" };
	return { text: "无窗口活动", app: "" };
}

function getMedia(data: StatusData | null): string | null {
	const media = data?.media;
	if (!media) return null;
	const title = (media.data?.title || media.window_title || "").trim();
	if (!title) return null;
	const artist = (media.data?.artist || "").trim();
	const statusMap: Record<string, string> = {
		playing: "播放中",
		paused: "已暂停",
		stopped: "已停止",
		changing: "切换中",
		closed: "已结束",
	};
	const status = media.data?.status
		? statusMap[media.data.status] || media.data.status
		: "";
	return `${title}${artist ? ` — ${artist}` : ""}${status ? `（${status}）` : ""}`;
}

/** 设备元信息小标签：电量 / 网络 / 屏幕 / 系统 */
function getChips(data: StatusData | null): { icon: string; text: string }[] {
	const device = data?.device || data?.activity?.extra || null;
	if (!device || typeof device !== "object") return [];

	const chips: { icon: string; text: string }[] = [];

	if (device.battery && typeof device.battery === "object") {
		const level = device.battery.level;
		const levelText =
			level === null || level === undefined || level < 0 ? "--" : `${level}%`;
		chips.push({
			icon: "battery",
			text: device.battery.charging ? `${levelText} 充电中` : levelText,
		});
	}

	if (device.network && typeof device.network === "object") {
		const type = (device.network.type || "").trim();
		chips.push({
			icon: "wifi",
			text: type || (device.network.wifi ? "WLAN" : "移动网络"),
		});
	}

	if (device.screen && typeof device.screen === "object") {
		chips.push({
			icon: device.screen.on ? "light" : "moon",
			text: device.screen.on ? "亮屏" : "息屏",
		});
	}

	const os = (device.os || "").trim();
	if (os) {
		const isAndroid = /^\d+(\.\d+)*$/.test(os);
		chips.push({
			icon: device.os ? "phone" : "desktop",
			text: isAndroid ? `Android ${os}` : os,
		});
	}

	return chips;
}

/** 倒计时 mm:ss，和上游的格式保持一致 */
function formatCountdown(target: number, nowMs: number): string {
	if (!target) return "--:--";
	const seconds = Math.max(0, Math.ceil((target - nowMs) / 1000));
	const mm = Math.floor(seconds / 60);
	const ss = seconds % 60;
	return `${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
}

function formatUpdatedAt(timestamp: number | null): string {
	if (!timestamp) return "";
	return new Date(timestamp).toLocaleTimeString("zh-CN", { hour12: false });
}

// 派生值：显式把状态变量作为实参传入，保证依赖被正确收集
$: onlineTotal = countOnline(statuses, devices);
$: hasAnyData = devices.some((d) => !!statuses[d.machine]);
$: countdown = formatCountdown(nextRefreshAt, now);
$: updatedAt = formatUpdatedAt(lastUpdated);
$: allOffline = onlineTotal === 0;
</script>

<div class="status-widget">
    <div class="status-summary">
        <span class="summary-online">
            <span class="dot" class:live={!allOffline}></span>
            {onlineTotal} 台在线
        </span>
        <span class="summary-total">共 {devices.length} 台设备</span>
    </div>

    {#if loading}
        <div class="status-hint">正在获取设备状态…</div>
    {:else if error && allOffline && !hasAnyData}
        <div class="status-hint status-error">
            <span>{error}</span>
            <button class="retry-btn" type="button" onclick={() => fetchAll()}>再试一次</button>
        </div>
    {:else}
        {#each devices as device (device.machine)}
            {@const data = statuses[device.machine] ?? null}
            {@const online = isOnline(data)}
            {@const lastSeen = getLastSeen(data)}
            {@const activity = getActivity(data)}
            {@const chips = getChips(data)}
            {@const media = getMedia(data)}
            <div class="status-card" class:offline={!online}>
                <div class="status-header">
                    <span class="status-type" title={device.kind === 'desktop' ? '桌面设备' : '移动设备'}>
                        {@html renderIcon(device.kind === 'desktop' ? 'desktop' : 'phone', 15)}
                    </span>
                    <span class="status-name">{device.name}</span>
                    <span class="status-indicator" class:online={online}>
                        <span class="dot" class:live={online}></span>{online ? '在线' : '离线'}
                    </span>
                </div>

                <div class="status-program" title={activity.text}>
                    {#if data?.activity?.privacy_mode}
                        <span class="lock-icon">{@html renderIcon('lock', 13)}</span>
                    {/if}
                    {activity.text}
                </div>

                <div class="status-sub">
                    {#if activity.app}
                        <span class="status-app">{activity.app}</span>
                    {/if}
                    <span class="status-time">
                        {online ? formatRelativeTime(lastSeen) : `最后上传 ${formatRelativeTime(lastSeen)}`}
                    </span>
                </div>

                {#if media}
                    <div class="status-media" title={media}>
                        <span class="chip-icon">{@html renderIcon('music', 13)}</span>{media}
                    </div>
                {/if}

                {#if chips.length > 0}
                    <div class="status-chips">
                        {#each chips as chip (chip.icon + chip.text)}
                            <span class="chip">
                                <span class="chip-icon">{@html renderIcon(chip.icon, 12)}</span>{chip.text}
                            </span>
                        {/each}
                    </div>
                {/if}
            </div>
        {/each}
    {/if}

    <div class="status-footer">
        <span class="refresh-status">
            {#if refreshing}
                <span class="spin">{@html renderIcon('refresh', 13)}</span>刷新中…
            {:else}
                <span class="clock-icon">{@html renderIcon('update', 13)}</span>{countdown} 后自动刷新
            {/if}
        </span>
        <span class="footer-right">
            {#if lastUpdated}
                <span class="updated-at">上次更新 {updatedAt}</span>
            {/if}
            <button class="refresh-btn" type="button" onclick={() => fetchAll()} disabled={refreshing} title="立即刷新">
                <span class:spin={refreshing}>{@html renderIcon('refresh', 14)}</span>
            </button>
        </span>
    </div>
</div>

<style>
    .status-widget {
        width: 100%;
        font-size: 0.8125rem;
    }

    /* ---------- 顶部汇总 ---------- */
    .status-summary {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px dashed var(--line-divider);
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .summary-online {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-weight: 600;
        color: var(--text-content);
    }

    .dot {
        width: 0.4rem;
        height: 0.4rem;
        border-radius: 9999px;
        background-color: var(--text-secondary);
        opacity: 0.6;
        flex-shrink: 0;
    }

    .dot.live {
        background-color: #28a745;
        opacity: 1;
        box-shadow: 0 0 0 2px rgb(40 167 69 / 0.18);
    }

    /* ---------- 设备卡片 ---------- */
    .status-card {
        padding: 0.5rem 0.55rem;
        border-radius: 0.6rem;
        background-color: var(--btn-plain-bg-hover);
        margin-bottom: 0.5rem;
        transition: opacity 0.2s ease;
    }

    .status-card:last-of-type {
        margin-bottom: 0;
    }

    .status-card.offline {
        opacity: 0.78;
    }

    .status-header {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin-bottom: 0.35rem;
    }

    .status-type {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.25rem;
        height: 1.25rem;
        border-radius: 0.35rem;
        background-color: var(--btn-regular-bg);
        color: var(--primary);
        flex-shrink: 0;
    }

    .status-name {
        font-weight: 600;
        color: var(--text-title);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        margin-left: auto;
        flex-shrink: 0;
        font-size: 0.6875rem;
        font-weight: 600;
        padding: 0.1rem 0.4rem;
        border-radius: 9999px;
        background-color: var(--btn-regular-bg);
        color: var(--text-secondary);
    }

    .status-indicator.online {
        background-color: rgb(40 167 69 / 0.16);
        color: #28a745;
    }

    /* ---------- 活动 / 应用 ---------- */
    .status-program {
        color: var(--text-content);
        line-height: 1.35;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        word-break: break-word;
    }

    .status-sub {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 0.25rem;
        font-size: 0.6875rem;
        color: var(--text-secondary);
    }

    .status-app {
        padding: 0.05rem 0.35rem;
        border-radius: 0.3rem;
        background-color: var(--btn-regular-bg);
        color: var(--text-secondary);
        max-width: 55%;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .status-time {
        margin-left: auto;
        white-space: nowrap;
    }

    /* ---------- 媒体 ---------- */
    .status-media {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        margin-top: 0.35rem;
        padding: 0.2rem 0.4rem;
        border-radius: 0.35rem;
        background-color: var(--btn-regular-bg);
        font-size: 0.6875rem;
        color: var(--text-content);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ---------- 设备元信息 ---------- */
    .status-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.25rem;
        margin-top: 0.4rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        padding: 0.05rem 0.35rem;
        border-radius: 0.3rem;
        background-color: var(--card-bg);
        font-size: 0.6875rem;
        color: var(--text-secondary);
        white-space: nowrap;
    }

    .chip-icon,
    .lock-icon {
        display: inline-flex;
        align-items: center;
        vertical-align: -0.125em;
        opacity: 0.85;
    }

    .status-program .lock-icon {
        margin-right: 0.2rem;
    }

    /* ---------- 底部刷新控制 ---------- */
    .status-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-top: 0.6rem;
        padding-top: 0.5rem;
        border-top: 1px dashed var(--line-divider);
        font-size: 0.6875rem;
        color: var(--text-secondary);
    }

    .refresh-status,
    .footer-right {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }

    .clock-icon,
    .updated-at {
        opacity: 0.85;
    }

    .refresh-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.4rem;
        height: 1.4rem;
        border-radius: 0.4rem;
        background-color: var(--btn-regular-bg);
        color: var(--text-content);
        cursor: pointer;
        transition: background-color 0.2s ease, color 0.2s ease;
    }

    .refresh-btn:hover:not(:disabled) {
        background-color: var(--btn-regular-bg-hover);
        color: var(--primary);
    }

    .refresh-btn:disabled {
        cursor: default;
        opacity: 0.7;
    }

    .spin {
        display: inline-flex;
        animation: status-spin 0.9s linear infinite;
    }

    @keyframes status-spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* ---------- 空态 / 错误 ---------- */
    .status-hint {
        text-align: center;
        color: var(--text-secondary);
        padding: 0.6rem 0;
        font-size: 0.8125rem;
    }

    .status-error {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .retry-btn {
        padding: 0.2rem 0.7rem;
        border-radius: 0.4rem;
        background-color: var(--btn-regular-bg);
        color: var(--text-content);
        font-size: 0.75rem;
        cursor: pointer;
    }

    .retry-btn:hover {
        background-color: var(--btn-regular-bg-hover);
        color: var(--primary);
    }
</style>
