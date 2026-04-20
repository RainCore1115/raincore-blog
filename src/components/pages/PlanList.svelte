<script lang="ts">
    import { onMount } from 'svelte';
    import type { PlanItem, PlanStatus } from '@/types/plan';
    import { planConfig } from '@/config/planConfig';

    let plans: PlanItem[] = [];
    let activeFilter: PlanStatus | 'all' = 'all';
    let likeData: Record<string, number> = {};

    onMount(() => {
        plans = [...planConfig.plans].sort((a, b) => 
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        );
        
        const stored = localStorage.getItem('plan-likes');
        if (stored) {
            likeData = JSON.parse(stored);
            plans = plans.map(p => ({
                ...p,
                likes: likeData[p.id] ?? p.likes
            }));
        }
    });

    function filterPlans(status: PlanStatus | 'all') {
        activeFilter = status;
    }

    function getFilteredPlans() {
        if (activeFilter === 'all') return plans;
        return plans.filter(p => p.status === activeFilter);
    }

    function getStatusLabel(status: PlanStatus): string {
        const labels: Record<PlanStatus, string> = {
            completed: '已完成',
            in_progress: '施工中',
            planned: '画饼中'
        };
        return labels[status];
    }

    function getStatusColor(status: PlanStatus): string {
        const colors: Record<PlanStatus, string> = {
            completed: '#22c55e',
            in_progress: '#f59e0b',
            planned: '#6b7280'
        };
        return colors[status];
    }

    function formatDate(dateStr: string): string {
        return new Date(dateStr).toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    function likePlan(id: string) {
        const liked = localStorage.getItem(`plan-liked-${id}`);
        if (liked) return;

        plans = plans.map(p => {
            if (p.id === id) {
                const newLikes = p.likes + 1;
                likeData[id] = newLikes;
                return { ...p, likes: newLikes };
            }
            return p;
        });

        localStorage.setItem(`plan-liked-${id}`, 'true');
        localStorage.setItem('plan-likes', JSON.stringify(likeData));
    }

    function isLiked(id: string): boolean {
        return localStorage.getItem(`plan-liked-${id}`) === 'true';
    }
</script>

<div class="plan-container">
    <div class="filter-tabs">
        <button 
            class="filter-btn" 
            class:active={activeFilter === 'all'}
            on:click={() => filterPlans('all')}
        >
            全部 ({plans.length})
        </button>
        <button 
            class="filter-btn" 
            class:active={activeFilter === 'completed'}
            on:click={() => filterPlans('completed')}
        >
            已完成 ({plans.filter(p => p.status === 'completed').length})
        </button>
        <button 
            class="filter-btn" 
            class:active={activeFilter === 'in_progress'}
            on:click={() => filterPlans('in_progress')}
        >
            施工中 ({plans.filter(p => p.status === 'in_progress').length})
        </button>
        <button 
            class="filter-btn" 
            class:active={activeFilter === 'planned'}
            on:click={() => filterPlans('planned')}
        >
            画饼中 ({plans.filter(p => p.status === 'planned').length})
        </button>
    </div>

    <div class="plan-list">
        {#each getFilteredPlans() as plan (plan.id)}
            <div class="plan-card">
                <div class="plan-header">
                    <h3 class="plan-title">{plan.title}</h3>
                    <span 
                        class="status-badge" 
                        style="background-color: {getStatusColor(plan.status)}"
                    >
                        {getStatusLabel(plan.status)}
                    </span>
                </div>
                
                <p class="plan-description">{plan.description}</p>
                
                {#if plan.tags && plan.tags.length > 0}
                    <div class="plan-tags">
                        {#each plan.tags as tag}
                            <span class="tag">{tag}</span>
                        {/each}
                    </div>
                {/if}
                
                <div class="plan-footer">
                    <span class="plan-date">
                        创建于 {formatDate(plan.createdAt)}
                        {#if plan.updatedAt}
                            · 更新于 {formatDate(plan.updatedAt)}
                        {/if}
                    </span>
                    
                    <button 
                        class="like-btn" 
                        class:liked={isLiked(plan.id)}
                        on:click={() => likePlan(plan.id)}
                        disabled={isLiked(plan.id)}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={isLiked(plan.id) ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                        </svg>
                        <span>{plan.likes}</span>
                    </button>
                </div>

                {#if plan.link}
                    <a href={plan.link} target="_blank" rel="noopener" class="plan-link">
                        查看详情 →
                    </a>
                {/if}
            </div>
        {/each}
    </div>

    {#if getFilteredPlans().length === 0}
        <div class="empty-state">
            <p>暂无计划</p>
        </div>
    {/if}
</div>

<style>
    .plan-container {
        width: 100%;
    }

    .filter-tabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .filter-btn {
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        border: 1px solid var(--line-divider);
        background: var(--card-bg);
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.875rem;
    }

    .filter-btn:hover {
        border-color: var(--primary);
        color: var(--primary);
    }

    .filter-btn.active {
        background: var(--primary);
        border-color: var(--primary);
        color: white;
    }

    .plan-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .plan-card {
        background: var(--card-bg);
        border: 1px solid var(--line-divider);
        border-radius: var(--radius-large);
        padding: 1.25rem;
        transition: all 0.3s;
    }

    .plan-card:hover {
        box-shadow: var(--shadow-card-hover);
        border-color: var(--primary);
    }

    .plan-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }

    .plan-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-title);
        margin: 0;
    }

    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        color: white;
        white-space: nowrap;
    }

    .plan-description {
        color: var(--text-content);
        font-size: 0.9375rem;
        line-height: 1.6;
        margin: 0 0 0.75rem 0;
    }

    .plan-tags {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }

    .tag {
        padding: 0.125rem 0.5rem;
        background: var(--bg-secondary);
        border-radius: var(--radius-small);
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .plan-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--line-divider);
    }

    .plan-date {
        font-size: 0.8125rem;
        color: var(--text-secondary);
    }

    .like-btn {
        display: flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border: 1px solid var(--line-divider);
        border-radius: var(--radius-medium);
        background: transparent;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.875rem;
    }

    .like-btn:hover:not(:disabled) {
        border-color: #ef4444;
        color: #ef4444;
    }

    .like-btn.liked {
        border-color: #ef4444;
        color: #ef4444;
        cursor: default;
    }

    .like-btn:disabled {
        cursor: default;
    }

    .plan-link {
        display: inline-block;
        margin-top: 0.75rem;
        color: var(--primary);
        font-size: 0.875rem;
        text-decoration: none;
    }

    .plan-link:hover {
        text-decoration: underline;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 0;
        color: var(--text-secondary);
    }
</style>
