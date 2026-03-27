import type { ProfileConfig } from "../types/config";

export const profileConfig: ProfileConfig = {
	// 头像
	// 图片路径支持三种格式：
	// 1. public 目录（以 "/" 开头，不优化）："/assets/images/avatar.webp"
	// 2. src 目录（不以 "/" 开头，自动优化但会增加构建时间，推荐）："assets/images/avatar.webp"
	// 3. 远程 URL："https://example.com/avatar.jpg"
	avatar: "https://q1.qlogo.cn/g?b=qq&nk=105823395&s=640",

	// 名字
	name: "RainCore",

	// 个人签名
	bio: "and in that light, I find deliverance.",

	// GitHub 用户名
	githubUsername: "raincore1115",

	// 链接配置
	// 已经预装的图标集：fa7-brands，fa7-regular，fa7-solid，material-symbols，simple-icons
	// 访问https://icones.js.org/ 获取图标代码，
	// 如果想使用尚未包含相应的图标集，则需要安装它
	// `pnpm add @iconify-json/<icon-set-name>`
	// showName: true 时显示图标和名称，false 时只显示图标
	links: [
		{
			name: "qq",
			icon: "fa7-brands:qq",
			url: "https://qm.qq.com/q/HUODrQ5Xi2",
			showName: false,
		},
		{
			name: "QQ群",
			icon: "fa7-brands:qq",
			url: "https://qun.qq.com/universal-share/share?ac=1&authKey=drNMAtD7%2Ba4aEBEAyzRprgEx3Acy1u58d7zFWvGXjEulx%2BRyTT3aKL2GM%2F0%2BQWho&busi_data=eyJncm91cENvZGUiOiI5NzU5OTU3MDUiLCJ0b2tlbiI6IjFaRHVKTzFRTWZtVzhuejdYMWdIM0MrUnpabE90anRpVmZrUWo1b3FvSzVMWTdOazRiTnZYNnZYb1VuSUt1R2EiLCJ1aW4iOiIxMDU4MjMzOTUifQ%3D%3D&data=51kQJLmxtwhT3qobZOEDhBSavnoCOlQhKEfBhD0wTahM5Jz4yDJeqbzlGqR833SC1N5PgdZMgnzrShgT94ISDg&svctype=4&tempid=h5_group_info",
			showName: false,
		},
		{
			name: "GitHub",
			icon: "fa7-brands:github",
			url: "https://github.com/raincore1115",
			showName: false,
		},
		{
			name: "Email",
			icon: "fa7-solid:envelope",
			url: "mailto:raincore@baka86.love",
			showName: false,
		},
	],
};
