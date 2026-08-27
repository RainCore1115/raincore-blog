#!/usr/bin/env python3
"""按行号替换 handler"""

FILE = "/root/awesome-bot/.venv/lib/python3.12/site-packages/nonebot_plugin_fakemsg/__init__.py"

with open(FILE) as f:
    lines = f.readlines()

# 找到 handler 开始和结束
start = None
end = None
for i, line in enumerate(lines):
    if "@send_fake_msg.handle()" in line:
        start = i
    if start is not None and i > start and "async def send_forward_msg" in line:
        end = i
        break

print(f"handler 在第 {start+1} 到 {end} 行")

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
                    await send_fake_msg.finish("消息格式错误，缺少\u201c说\u201d。")
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
        await send_fake_msg.finish(f"发送失败: {e}")

'''

# 替换
lines[start:end] = [new_handler]

with open(FILE, "w") as f:
    f.writelines(lines)

print("handler 替换成功")
