import type { PlanConfig } from "@/types/plan";

export const planConfig: PlanConfig = {
	plans: [
		{
			id: "1",
			title: "博客系统搭建",
			description: "基于 Astro + Firefly 主题搭建个人博客，完成基础配置和个性化定制",
			status: "completed",
			createdAt: "2026-03-01",
			updatedAt: "2026-03-28",
			tags: ["博客", "Astro"],
			likes: 0,
		},
		{
			id: "2",
			title: "视奸系统开发",
			description: "开发实时状态监控系统，展示电脑和手机的使用状态",
			status: "completed",
			createdAt: "2026-03-15",
			updatedAt: "2026-03-28",
			tags: ["监控", "API"],
			likes: 0,
		},
		{
			id: "3",
			title: "计划页面开发",
			description: "开发计划展示页面，支持状态分类和点赞功能",
			status: "in_progress",
			createdAt: "2026-03-28",
			tags: ["功能开发"],
			likes: 0,
		},
		{
			id: "4",
			title: "更多功能规划中...",
			description: "持续迭代和优化博客功能",
			status: "planned",
			createdAt: "2026-03-28",
			tags: ["规划"],
			likes: 0,
		},
	],
};
