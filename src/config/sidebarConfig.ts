import type { SidebarLayoutConfig } from "../types/config";

/**
 * 侧边栏布局配置
 */
export const sidebarLayoutConfig: SidebarLayoutConfig = {
	// 是否启用侧边栏功能
	enable: true,

	// 侧边栏位置：
	// left: 仅显示左侧边栏
	// right: 仅显示右侧边栏
	// both: 双侧边栏，1280px以上同时显示左右，769-1279px根据tabletSidebar配置显示其中一侧
	position: "right",

	// 平板端(769-1279px)显示哪侧侧边栏，仅position为both时生效
	// left: 平板端显示左侧边栏
	// right: 平板端显示右侧边栏
	tabletSidebar: "left",

	// 使用单侧栏(position为left或right)时，是否在文章详情页显示双侧边栏
	// 当position为left时开启此项，文章详情页将额外显示右侧边栏
	// 当position为right时开启此项，文章详情页将额外显示左侧边栏
	// 适用在只想用单侧栏，但在文章详情页想用对侧栏的目录等组件的场景
	showBothSidebarsOnPostPage: true,

	// 左侧边栏组件配置列表
	leftComponents: [],

	// 右侧边栏组件配置列表
	rightComponents: [
		{
			// 组件类型：用户资料组件
			type: "profile",
			enable: true,
			position: "top",
			showOnPostPage: true,
		},
		{
			// 组件类型：公告组件
			type: "announcement",
			enable: true,
			position: "top",
			showOnPostPage: true,
		},
		{
			// 组件类型：Status 组件
			type: "status",
			enable: true,
			position: "top",
			showOnPostPage: true,
		},
		{
			// 组件类型：GitHub 活动组件
			type: "github",
			enable: true,
			position: "top",
			showOnPostPage: true,
		},
		{
			// 组件类型：音乐播放器
			type: "music",
			enable: true,
			position: "sticky",
			showOnPostPage: true,
		},
		{
			// 组件类型：分类组件
			type: "categories",
			enable: true,
			position: "sticky",
			showOnPostPage: true,
			responsive: {
				collapseThreshold: 5,
			},
		},
		{
			// 组件类型：标签组件
			type: "tags",
			enable: true,
			position: "sticky",
			showOnPostPage: true,
			responsive: {
				collapseThreshold: 20,
			},
		},
		{
			// 组件类型：日历组件
			type: "calendar",
			enable: false,
			position: "sticky",
			showOnPostPage: false,
		},
		{
			// 组件类型：侧边栏目录组件（只在文章详情页显示）
			type: "sidebarToc",
			enable: true,
			position: "sticky",
			showOnPostPage: true,
			showOnNonPostPage: false,
		},
		{
			// 组件类型：广告栏组件
			type: "advertisement",
			enable: false,
			position: "sticky",
			showOnPostPage: true,
			configId: "ad1",
		},
	],

	// 移动端底部组件配置列表
	mobileBottomComponents: [
		{
			// 组件类型：用户资料组件
			type: "profile",
			enable: true,
			showOnPostPage: true,
		},
		{
			// 组件类型：公告组件
			type: "announcement",
			enable: true,
			showOnPostPage: true,
		},
		{
			// 组件类型：音乐播放器
			type: "music",
			enable: true,
			showOnPostPage: true,
		},
		{
			// 组件类型：分类组件
			type: "categories",
			enable: true,
			showOnPostPage: true,
			responsive: {
				collapseThreshold: 5,
			},
		},
		{
			// 组件类型：标签组件
			type: "tags",
			enable: true,
			showOnPostPage: true,
			responsive: {
				collapseThreshold: 20,
			},
		},
	],
};
