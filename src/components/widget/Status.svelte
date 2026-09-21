<script lang="ts">
import { onMount } from "svelte";

// 数据源：时间雨 API (v2)
//   GET {API_BASE}?machine=<设备名>  返回单个对象
//   { machine, last_seen, activity: { window_title, app, access_time, privacy_mode }, media, device }
const API_BASE = "https://shijian.07210700.xyz/api/v2/status";

interface Activity {
	machine?: string;
	window_title?: string | null;
	app?: string | null;
	access_time?: string | null;
	privacy_mode?: boolean;
}

interface DeviceInfo {
	battery?: { level?: number | null; charging?: boolean };
	network?: { wifi?: boolean; type?: string };
	screen?: { on?: boolean };
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
	key: string;
	machine: string;
	name: string;
	emoji: string;
}

// 视奸模块展示的两台设备
const DEVICES: DeviceConfig[] = [
	{ key: "pc", machine: "yuhe-pc", name: "雨核的电脑", emoji: "🖥️" },
	{ key: "phone", machine: "yuhe-sanxing", name: "雨核的手机", emoji: "📱" },
];

// 超过该时长未上传数据视为离线（与 bot 插件一致，3 分钟）
const OFFLINE_THRESHOLD = 3 * 60 * 1000;

let statuses: Record<string, StatusData | null> = {};
let loading = true;

onMount(async () => {
	await fetchAll();
});

async function fetchAll() {
	loading = true;
	const timestamp = Date.now();
	try {
		const entries = await Promise.all(
			DEVICES.map(async (d) => {
				try {
					const res = await fetch(
						`${API_BASE}?machine=${encodeURIComponent(d.machine)}&_t=${timestamp}`,
					);
					if (!res.ok) return [d.machine, null] as const;
					const json = await res.json();
					// v2 返回单个对象；兼容数组写法
					const data = Array.isArray(json) ? json[0] : json;
					return [d.machine, (data as StatusData) ?? null] as const;
				} catch (error) {
					console.error("Error fetching status data:", d.machine, error);
					return [d.machine, null] as const;
				}
			}),
		);
		statuses = Object.fromEntries(entries);
	} finally {
		loading = false;
	}
}

function getStatus(machine: string): StatusData | null {
	return statuses[machine] ?? null;
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

function formatTime(time: string | undefined): string {
	if (!time) return "N/A";
	const date = new Date(time);
	if (Number.isNaN(date.getTime())) return "N/A";
	return date.toLocaleString("zh-CN", {
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
		hour12: false,
	});
}

function formatRelativeTime(time: string | undefined): string {
	if (!time) return "未知时间";
	const t = new Date(time).getTime();
	if (Number.isNaN(t)) return "未知时间";
	const diff = Date.now() - t;
	if (diff < 0) return "刚刚";
	const seconds = Math.floor(diff / 1000);
	if (seconds < 10) return "刚刚";
	if (seconds < 60) return `${seconds} 秒前`;
	const minutes = Math.floor(seconds / 60);
	if (minutes < 60) return `${minutes} 分钟前`;
	const hours = Math.floor(minutes / 60);
	if (hours < 24) return `${hours} 小时前`;
	return `${Math.floor(hours / 24)} 天前`;
}

function getActivityText(data: StatusData | null): string {
	if (!data) return "暂无数据";
	const activity = data.activity;
	if (activity?.privacy_mode) return "开启了隐私模式 🔒";
	const title = (activity?.window_title || "").trim();
	if (title) return title;
	const app = (activity?.app || "").trim();
	if (app) return app;
	return "未知应用";
}

function getMediaText(data: StatusData | null): string | null {
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
	const status = media.data?.status ? statusMap[media.data.status] || media.data.status : "";
	return `${title}${artist ? ` — ${artist}` : ""}${status ? `（${status}）` : ""}`;
}

function getDeviceText(data: StatusData | null): string | null {
	const device = data?.device;
	if (!device) return null;
	const parts: string[] = [];
	if (device.battery) {
		const level = device.battery.level;
		const levelText = level === null || level === undefined || level < 0 ? "--" : `${level}%`;
		parts.push(`🔋${levelText}${device.battery.charging ? "（充电中）" : ""}`);
	}
	if (device.network) {
		parts.push(`📶${device.network.type || (device.network.wifi ? "WLAN" : "移动网络")}`);
	}
	if (device.screen) {
		parts.push(device.screen.on ? "💡亮屏" : "🌙息屏");
	}
	return parts.length ? parts.join(" | ") : null;
}
</script>

<div class="status-widget">
    {#if loading}
        <div class="loading-text">加载中...</div>
    {:else}
        {#each DEVICES as device (device.machine)}
            {@const data = getStatus(device.machine)}
            {#if data}
                {@const online = isOnline(data)}
                {@const lastSeen = getLastSeen(data)}
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-name">{device.emoji} {device.name}</span>
                        <span class="status-indicator" class:online={online}>
                            {online ? '在线' : '离线'}
                        </span>
                    </div>
                    <div class="status-program" title={getActivityText(data)}>
                        {getActivityText(data)}
                    </div>
                    {#if getMediaText(data)}
                        <div class="status-media" title={getMediaText(data) ?? ''}>
                            🎵 {getMediaText(data)}
                        </div>
                    {/if}
                    {#if getDeviceText(data)}
                        <div class="status-device">{getDeviceText(data)}</div>
                    {/if}
                    <div class="status-time">
                        {online ? formatRelativeTime(lastSeen) : `最后上传 ${formatRelativeTime(lastSeen)}`} · {formatTime(lastSeen)}
                    </div>
                </div>
            {:else}
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-name">{device.emoji} {device.name}</span>
                        <span class="status-indicator">离线</span>
                    </div>
                    <div class="no-data">暂无设备状态</div>
                </div>
            {/if}
        {/each}
    {/if}
</div>

<style>
    .status-widget {
        width: 100%;
    }

    .loading-text, .no-data {
        text-align: center;
        color: var(--text-secondary);
        padding: 0.5rem 0;
        font-size: 0.875rem;
    }

    .status-card {
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--line-divider);
    }

    .status-card:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }

    .status-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .status-name {
        font-weight: bold;
        color: var(--text-title);
    }

    .status-indicator {
        font-size: 0.75rem;
        padding: 0.1rem 0.5rem;
        border-radius: var(--radius-full);
        background-color: var(--btn-plain-bg-hover);
        color: var(--text-secondary);
        font-weight: 500;
    }

    .status-indicator.online {
        background-color: #28a745;
        color: white;
    }

    .status-program {
        font-size: 0.875rem;
        color: var(--text-content);
        margin-bottom: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .status-media,
    .status-device {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-bottom: 0.25rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .status-time {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-align: right;
    }
</style>
