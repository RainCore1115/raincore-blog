import type { FriendLink, FriendsPageConfig } from "../types/config";

// 可以在src/content/spec/friends.md中编写友链页面下方的自定义内容

// 友链页面配置
export const friendsPageConfig: FriendsPageConfig = {
	// 页面标题，如果留空则使用 i18n 中的翻译
	title: "",

	// 页面描述文本，如果留空则使用 i18n 中的翻译
	description: "",

	// 是否显示底部自定义内容（friends.mdx 中的内容）
	showCustomContent: true,

	// 是否开启随机排序配置，如果开启，就会忽略权重，构建时进行一次随机排序
	randomizeSort: false,
};

// 友链配置
export const friendsConfig: FriendLink[] = [
	{
		title: "HINS's Blog",
		imgurl: "https://avatars.githubusercontent.com/u/105108428?v=4",
		desc: "HINS的温馨小猫窝",
		siteurl: "https://blog.hinswu.top",
		tags: ["Blog"],
		weight: 10,
		enabled: true,
	},
	{
		title: "chuzouX Blog",
		imgurl: "https://q2.qlogo.cn/headimg_dl?dst_uin=3451860760&spec=0",
		desc: "技术分享与实践",
		siteurl: "https://chuzoux.top/",
		tags: ["Blog"],
		weight: 10,
		enabled: true,
	},
	{
		title: "皮梦 の 茶馆",
		imgurl:
			"http://thirdqq.qlogo.cn/ek_qqapp/AQBYdE3HOBBJWzCia3BjOePcJ5icmcwpTW0cEWXlZsib48hLvjwq5KYMmdBlpKtRB3cqt3Kmgfb5v69WGKRvB3Q6av6EV7Jfmc9n5SK9ZRxnAchmKJBILw/100",
		desc: "杂鱼皮梦的博客",
		siteurl: "https://blog.07210700.xyz",
		tags: ["Blog"],
		weight: 10,
		enabled: true,
	},
	{
		title: "Milk's Blog",
		imgurl:
			"https://upload.awmc.cc/uploads/20260330/c095b9df52d0c466ee38bdf202262176.png",
		desc: "喵喵咕噜咕噜～",
		siteurl: "https://blog.awmc.cc",
		tags: ["Blog"],
		weight: 10,
		enabled: true,
	},
	{
		title: "AWMC BBS",
		imgurl:
			"https://upload.awmc.cc/uploads/20260330/c095b9df52d0c466ee38bdf202262176.png",
		desc: "awmc论坛",
		siteurl: "https://awmc.cc",
		tags: ["Discussion"],
		weight: 9,
		enabled: true,
	},
	{
		title: "Dmocken的Phira下载站",
		imgurl: "https://phira.dmocken.top/Phira.png",
		desc: "只是一个普普通通的下载站~",
		siteurl: "https://phira.dmocken.top/",
		tags: ["Software"],
		weight: 8,
		enabled: true,
	},
	{
		title: "Chongxiの咖啡屋",
		imgurl: "https://xice.cx/images/14.webp",
		desc: "Lose yourself to find yourself",
		siteurl: "https://xice.cx/",
		tags: ["Blog"],
		weight: 10,
		enabled: true,
	},
	{
		title: "落雪咖啡屋",
		imgurl: "https://awmc.cc/media/image_1776709261927_32-png.242/",
		desc: "Score Tracker",
		siteurl: "https://lxns.net/",
		tags: ["Software"],
		weight: 10,
		enabled: true,
	},
	{
		title: "梦雨的主页",
		imgurl: "https://www.dreamrain.net/images/icon/logo.png",
		desc: "梦雨的后花园",
		siteurl: "https://www.dreamrain.net",
		tags: ["Blog"],
		weight: 10,
		enabled: true,
	},
];

// 获取启用的友链并进行排序
export const getEnabledFriends = (): FriendLink[] => {
	const friends = friendsConfig.filter((friend) => friend.enabled);

	if (friendsPageConfig.randomizeSort) {
		return friends.sort(() => Math.random() - 0.5);
	}

	return friends.sort((a, b) => b.weight - a.weight);
};
