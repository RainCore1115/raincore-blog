import {
	LinkPreset,
	type NavBarConfig,
	type NavBarLink,
	type NavBarSearchConfig,
	NavBarSearchMethod,
} from "../types/config";
import { siteConfig } from "./siteConfig";

// 根据页面开关动态生成导航栏配置
const getDynamicNavBarConfig = (): NavBarConfig => {
	// 基础导航栏链接
	const links: (NavBarLink | LinkPreset)[] = [
		// 主页
		LinkPreset.Home,

		// 归档
		LinkPreset.Archive,
	];

	// 友链
	links.push(LinkPreset.Friends);

	// 根据配置决定是否添加留言板，在siteConfig关闭pages.guestbook时导航栏不显示留言板
	if (siteConfig.pages.guestbook) {
		links.push(LinkPreset.Guestbook);
	}

	// 我的及其子菜单
	links.push({
		name: "我的",
		url: "/my/",
		icon: "material-symbols:person",
		children: [
			// 计划页面
			{
				name: "计划",
				url: "/plan/",
				icon: "material-symbols:calendar-month",
			},

			// 根据配置决定是否添加相册，在siteConfig关闭pages.gallery时导航栏不显示相册
			...(siteConfig.pages.gallery ? [LinkPreset.Gallery] : []),

			// 根据配置决定是否添加番组计划，在siteConfig关闭pages.bangumi时导航栏不显示番组计划
			...(siteConfig.pages.bangumi ? [LinkPreset.Bangumi] : []),
		],
	});

	// 关于及其子菜单
	links.push({
		name: "关于",
		url: "/content/",
		icon: "material-symbols:info",
		children: [
			// 根据配置决定是否添加赞助，在siteConfig关闭pages.sponsor时导航栏不显示赞助
			...(siteConfig.pages.sponsor ? [LinkPreset.Sponsor] : []),

			// 关于页面
			LinkPreset.About,
		],
	});

	// 自定义导航栏链接,并且支持多级菜单
	links.push({
		name: "链接",
		url: "/links/",
		icon: "material-symbols:link",

		// 子菜单
		children: [
			{
				name: "GitHub",
				url: "https://github.com/raincore1115",
				external: true,
				icon: "fa7-brands:github",
			},
			{
				name: "QQ群",
				url: "https://qun.qq.com/universal-share/share?ac=1&authKey=drNMAtD7%2Ba4aEBEAyzRprgEx3Acy1u58d7zFWvGXjEulx%2BRyTT3aKL2GM%2F0%2BQWho&busi_data=eyJncm91cENvZGUiOiI5NzU5OTU3MDUiLCJ0b2tlbiI6IjFaRHVKTzFRTWZtVzhuejdYMWdIM0MrUnpabE90anRpVmZrUWo1b3FvSzVMWTdOazRiTnZYNnZYb1VuSUt1R2EiLCJ1aW4iOiIxMDU4MjMzOTUifQ%3D%3D&data=51kQJLmxtwhT3qobZOEDhBSavnoCOlQhKEfBhD0wTahM5Jz4yDJeqbzlGqR833SC1N5PgdZMgnzrShgT94ISDg&svctype=4&tempid=h5_group_info",
				external: true,
				icon: "fa7-brands:qq",
			},
			{
				name: "视奸网站",
				url: "https://status.baka86.love",
				external: true,
				icon: "material-symbols:monitor-heart",
			},
		],
	});

	// 仅返回链接，其它导航搜索相关配置在模块顶层常量中独立导出
	return { links } as NavBarConfig;
};

// 导航搜索配置
export const navBarSearchConfig: NavBarSearchConfig = {
	method: NavBarSearchMethod.PageFind,
};

export const navBarConfig: NavBarConfig = getDynamicNavBarConfig();
