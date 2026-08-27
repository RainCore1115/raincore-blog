#!/usr/bin/env python3
"""修复 nonebot_plugin_fakemsg 插件的多个 bug"""
import re

FILE = "/root/awesome-bot/.venv/lib/python3.12/site-packages/nonebot_plugin_fakemsg/__init__.py"

with open(FILE) as f:
    code = f.read()

# 备份
with open(FILE + ".bak", "w") as f:
    f.write(code)
print("已备份 .bak")

# === 修复 1: check_if_fakemsg ===
old_check = '''async def check_if_fakemsg(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
) -> bool:
    if len(event.original_message) > 1 and event.original_message[0].type == "at":
        if event.original_message[1].data.get("text").strip().startswith("说"):
            return True
    elif event.original_message[0].type == "text" and re.match(
        r"^\\d{6,10}说", event.original_message[0].data.get("text")
    ):
        return True
    return False'''

new_check = '''async def check_if_fakemsg(
    event: Union[GroupMessageEvent, PrivateMessageEvent],
) -> bool:
    msg = event.original_message
    # 跳过 reply 段，找到第一个有效段
    start = 0
    while start < len(msg) and msg[start].type == "reply":
        start += 1
    if start >= len(msg):
        return False

    # @模式: at + text("说...")
    if start + 1 < len(msg) and msg[start].type == "at":
        next_seg = msg[start + 1]
        if next_seg.type == "text":
            text_data = next_seg.data.get("text")
            if text_data and text_data.strip().startswith("说"):
                return True
        return False

    # 文本模式: "123456说..."
    if msg[start].type == "text":
        text_data = msg[start].data.get("text", "")
        if text_data and re.match(r"^\\d{5,11}说", text_data):
            return True
    return False'''

code = code.replace(old_check, new_check)
print("已修复 check_if_fakemsg")

# === 修复 2: handler ===
old_handler = '''@send_fake_msg.handle()
async def _(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent]):
    await send_fake_msg.send("正在伪造消息……")
    fetched_message = event.original_message
    fake_msg_list = []  # 创建伪造消息列表
    at_qq_message = fetched_message["at"]  # 获取at的qq号
    text_message = fetched_message["text"]  # 获取文本消息
    user_index = 0

    for text in text_message:
        raw_text: str = text.data["text"]
        user_msgs = raw_text.split(user_split)
        for raw_user_msg in user_msgs:
            user_msg = raw_user_msg.strip()  # 去除空格
            if user_msg.startswith("说"):
                user_msg = user_msg.split("说", 1)[1]
                user_qq = at_qq_message[user_index].data["qq"]
                user_info = await bot.get_stranger_info(user_id=int(user_qq))
                user_name = user_info["nickname"]
                user_index += 1
            elif user_msg not in {"", " "}:
                try:
                    user_qq, user_msg = user_msg.split("说", 1)
                except ValueError:
                    await send_fake_msg.finish("消息格式错误，缺少"说"。")
            else:
                continue

            # 白名单检测
            if user_qq in whitelist and str(event.user_id) not in superusers:
                await send_fake_msg.finish(f"你没有权限伪造该用户（{user_qq}）的消息。")

            user_info = await bot.get_stranger_info(user_id=int(user_qq))
            user_name = user_info["nickname"]
            fake_msg_list.extend(
                (user_name, user_qq, msg) for msg in user_msg.split(message_split)
            )

    try:
        await send_forward_msg(bot, event, fake_msg_list)
    except Exception as e:
        await send_fake_msg.finish(f"发送失败,{e}")'''

new_handler = '''@send_fake_msg.handle()
async def _(bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent]):
    await send_fake_msg.send("正在伪造消息……")
    fetched_message = event.original_message
    fake_msg_list = []
    at_qq_message = fetched_message["at"]
    text_message = fetched_message["text"]
    user_index = 0

    async def get_user_name(qq: str) -> str:
        """安全获取用户昵称，失败时返回QQ号"""
        try:
            info = await bot.get_stranger_info(user_id=int(qq))
            return info["nickname"]
        except Exception:
            try:
                if hasattr(event, "group_id"):
                    info = await bot.get_group_member_info(
                        group_id=event.group_id, user_id=int(qq)
                    )
                    return info.get("card") or info.get("nickname") or qq
            except Exception:
                pass
            return qq

    for text in text_message:
        raw_text: str = text.data["text"]
        user_msgs = raw_text.split(user_split)
        for raw_user_msg in user_msgs:
            user_msg = raw_user_msg.strip()
            if user_msg.startswith("说"):
                user_msg = user_msg.split("说", 1)[1]
                if user_index >= len(at_qq_message):
                    await send_fake_msg.finish("@数量与文本不匹配")
                user_qq = at_qq_message[user_index].data["qq"]
                if user_qq == "all":
                    await send_fake_msg.finish("不支持伪造@全体成员")
                user_name = await get_user_name(user_qq)
                user_index += 1
            elif user_msg not in {"", " "}:
                try:
                    user_qq, user_msg = user_msg.split("说", 1)
                except ValueError:
                    await send_fake_msg.finish("消息格式错误，缺少"说"。")
            else:
                continue

            if user_qq in whitelist and str(event.user_id) not in superusers:
                await send_fake_msg.finish(f"你没有权限伪造该用户（{user_qq}）的消息。")

            user_name = await get_user_name(user_qq)
            fake_msg_list.extend(
                (user_name, user_qq, msg) for msg in user_msg.split(message_split)
            )

    if not fake_msg_list:
        await send_fake_msg.finish("没有可伪造的消息内容")

    try:
        await send_forward_msg(bot, event, fake_msg_list)
    except Exception as e:
        await send_fake_msg.finish(f"发送失败: {e}")'''

code = code.replace(old_handler, new_handler)
print("已修复 handler")

with open(FILE, "w") as f:
    f.write(code)

print("\n修复完成!")
