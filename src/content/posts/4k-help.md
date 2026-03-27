---
title: 4k准度计算器使用帮助
published: 2026-03-12
description: "ACC 计算器插件使用帮助"
tags: [bot, 4k, ACC计算器]
category: bot使用帮助
draft: false
---

# **ACC 计算器插件使用帮助**

## **功能介绍**

本插件提供一个交互式的ACC（准确度）计算器，主要用于音游段位认定中，帮助玩家计算单曲ACC或推算段位总体ACC的变化。

## **使用方法**

通过发送指令`#acc计算器`来启动计算器。

启动后，机器人会通过一系列交互式问题引导您完成计算。您只需要根据提示回复相应的数字或内容即可。

### **交互流程**

1.  **启动计算器**: 发送 `#acc计算器`
2.  **选择计算方式**:
    *   `1`: 由段位ACC变化计算单曲ACC（知道每次打完一首歌后的段位总ACC，计算出每首歌的ACC是多少）。
    *   `2`: 由单曲ACC推算段位ACC变化（知道每首歌的单曲ACC，推算出段位总ACC的变化过程）。
3.  **选择段位类别**: 根据机器人列出的段位类别列表，输入序号进行选择。
4.  **选择具体段位**: 根据机器人列出的具体段位列表，输入序号进行选择。
5.  **输入ACC**: 根据机器人的提示，依次输入ACC数值（0-100）。
6.  **查看结果**: 输入所有必需的ACC后，机器人将返回计算结果。

### **取消操作**

在计算过程中的任何时候，您都可以发送 `取消` 来退出当前的计算任务。

## **支持的段位类别**

计算器支持以下多种音游的段位认定：

- Malody 4K Dan v2
- Malody 4K Extra Dan v2 (Sample)
- Malody 4K Dan v3
- osu!mania 4K Dan ~ REFORM
- osu!mania 4K Dan ~ REFORM ~ Sample
- osu!mania 4K Dan ~ REFORM ~ FINAL
- osu!mania 4K LN Dan Course v2
- Haku Dan (白段)
- Senpai Dan v1
- wds0 Dan
- osu!mania 7K Regular Dan Course
- osu!mania 7K LN Dan Course

## **示例**

```
你: #acc计算器

机器人: 欢迎使用baka86ACC计算器！
请选择计算方式：
1. 由段位ACC变化计算单曲ACC
2. 由单曲ACC推算段位ACC变化

您可以随时发送"取消"来退出计算。

你: 1

机器人: 请选择段位类别：
1. Malody 4K Dan v2
...

你: 3

机器人: 您选择了【Malody 4K Dan v3】，请选择具体段位：
1. 0
2. 1
...

你: 2

机器人: 请输入第 1 首歌【尘世闲游】结束时的段位 ACC：

你: 98.5

机器人: 请输入第 2 首歌【恋せよ乙女！】结束时的段位 ACC：

你: 98.2

... (继续输入直到完成)

机器人: (返回最终计算结果)
```
