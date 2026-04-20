<script lang="ts">
    import { onMount } from 'svelte';

    export let username: string;
    export let type: 'user' | 'org' = 'user';

    interface Repo {
        name: string;
        full_name: string;
        description: string;
        html_url: string;
        stargazers_count: number;
        forks_count: number;
        language: string;
        owner: {
            avatar_url: string;
            login: string;
        };
    }

    let repos: Repo[] = [];
    let loading = true;
    let error = false;

    onMount(async () => {
        try {
            const response = await fetch(`https://api.github.com/users/${username}/repos?sort=updated&per_page=10`);
            if (!response.ok) throw new Error('Failed to fetch');
            repos = await response.json();
        } catch (e) {
            console.error('Error fetching repos:', e);
            error = true;
        } finally {
            loading = false;
        }
    });

    function formatNumber(num: number): string {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
</script>

<div class="github-repos">
    {#if loading}
        <div class="loading">加载中...</div>
    {:else if error}
        <div class="error">加载失败</div>
    {:else}
        {#each repos as repo}
            <a href={repo.html_url} target="_blank" rel="noopener" class="repo-card">
                <div class="repo-header">
                    <div class="repo-owner">
                        <img src={repo.owner.avatar_url} alt={repo.owner.login} class="avatar" />
                        <span class="owner-name">{repo.owner.login}</span>
                    </div>
                    <span class="divider">/</span>
                    <span class="repo-name">{repo.name}</span>
                </div>
                <p class="repo-description">{repo.description || '暂无描述'}</p>
                <div class="repo-footer">
                    {#if repo.language}
                        <span class="language">
                            <span class="language-dot" style="background-color: var(--lang-{repo.language.toLowerCase()})"></span>
                            {repo.language}
                        </span>
                    {/if}
                    <span class="stars">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                        {formatNumber(repo.stargazers_count)}
                    </span>
                    <span class="forks">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="20" x2="12" y2="10"></line>
                            <line x1="18" y1="20" x2="18" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="4"></line>
                        </svg>
                        {formatNumber(repo.forks_count)}
                    </span>
                </div>
            </a>
        {/each}
    {/if}
</div>

<style>
    .github-repos {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .loading, .error {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
    }

    .repo-card {
        display: block;
        background: var(--card-bg);
        border: 1px solid var(--line-divider);
        border-radius: var(--radius-large);
        padding: 1rem 1.25rem;
        text-decoration: none;
        color: inherit;
        transition: all 0.3s;
    }

    .repo-card:hover {
        border-color: var(--primary);
        box-shadow: var(--shadow-card-hover);
    }

    .repo-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .repo-owner {
        display: flex;
        align-items: center;
        gap: 0.375rem;
    }

    .avatar {
        width: 20px;
        height: 20px;
        border-radius: 50%;
    }

    .owner-name {
        color: var(--text-secondary);
        font-size: 0.875rem;
    }

    .divider {
        color: var(--text-secondary);
    }

    .repo-name {
        font-weight: 600;
        color: var(--primary);
    }

    .repo-description {
        color: var(--text-content);
        font-size: 0.875rem;
        margin: 0 0 0.75rem 0;
        line-height: 1.5;
    }

    .repo-footer {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .language {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .language-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #858585;
    }

    .stars, .forks {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
</style>
