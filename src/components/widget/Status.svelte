<script lang="ts">
    import { onMount } from 'svelte';

    interface StatusData {
        machine: string;
        window_title: string;
        app: string | null;
        access_time: string;
    }

    let pcStatus: StatusData | null = null;
    let phoneStatus: StatusData | null = null;
    let loading = true;

    onMount(async () => {
        await fetchStatus();
    });

    async function fetchStatus() {
        loading = true;
        try {
            const timestamp = Date.now();
            const [pcResponse, phoneResponse] = await Promise.all([
                fetch(`https://status.baka86.love/api/current-status?machine=raincore-pc&limit=1&_t=${timestamp}`),
                fetch(`https://status.baka86.love/api/current-status?machine=raincore-phone&limit=1&_t=${timestamp}`)
            ]);

            const pcData = await pcResponse.json();
            const phoneData = await phoneResponse.json();

            if (pcData && pcData.length > 0) {
                pcStatus = pcData[0];
            }
            if (phoneData && phoneData.length > 0) {
                phoneStatus = phoneData[0];
            }
        } catch (error) {
            console.error('Error fetching status data:', error);
        } finally {
            loading = false;
        }
    }

    function formatTime(time: string | undefined): string {
        if (!time) return 'N/A';
        const date = new Date(time);
        return date.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit', 
            hour12: false 
        });
    }

    function isOnline(accessTime: string): boolean {
        const lastSeen = new Date(accessTime).getTime();
        const now = Date.now();
        return (now - lastSeen) < 5 * 60 * 1000;
    }

    function getDisplayName(machine: string): string {
        return machine === 'raincore-pc' ? '雨核的电脑' : '雨核的手机';
    }
</script>

<div class="status-widget">
    {#if loading}
        <div class="loading-text">加载中...</div>
    {:else}
        {#if pcStatus}
            <div class="status-card">
                <div class="status-header">
                    <span class="status-name">{getDisplayName(pcStatus.machine)}</span>
                    <span class="status-indicator" class:online={isOnline(pcStatus.access_time)}>
                        {isOnline(pcStatus.access_time) ? '在线' : '离线'}
                    </span>
                </div>
                <div class="status-program" title={pcStatus.window_title}>
                    {pcStatus.window_title || 'Unknown'}
                </div>
                <div class="status-time">{formatTime(pcStatus.access_time)}</div>
            </div>
        {/if}

        {#if phoneStatus}
            <div class="status-card">
                <div class="status-header">
                    <span class="status-name">{getDisplayName(phoneStatus.machine)}</span>
                    <span class="status-indicator" class:online={isOnline(phoneStatus.access_time)}>
                        {isOnline(phoneStatus.access_time) ? '在线' : '离线'}
                    </span>
                </div>
                <div class="status-program" title={phoneStatus.window_title}>
                    {phoneStatus.window_title || 'Unknown'}
                </div>
                <div class="status-time">{formatTime(phoneStatus.access_time)}</div>
            </div>
        {/if}

        {#if !pcStatus && !phoneStatus}
            <div class="no-data">暂无设备状态</div>
        {/if}
    {/if}
</div>

<style>
    .status-widget {
        width: 100%;
    }

    .loading-text, .no-data {
        text-align: center;
        color: var(--text-secondary);
        padding: 1rem 0;
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

    .status-time {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-align: right;
    }
</style>
