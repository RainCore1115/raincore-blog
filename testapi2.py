import os, sys, asyncio
os.chdir('/root/awesome-bot')
sys.path.insert(0, '/root/awesome-bot/.venv/lib/python3.12/site-packages')

# 先初始化 nonebot
import nonebot
nonebot.init()

# 直接 import client 相关内容（不通过 __init__.py 避免加载 matcher 模块）
import importlib.util
spec = importlib.util.spec_from_file_location(
    "maimai_client",
    "/root/awesome-bot/.venv/lib/python3.12/site-packages/nonebot_plugin_maimaimonitor/client.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# 查看 MaimaiReporterClient 需要什么参数
import inspect
print('MaimaiReporterClient init signature:')
print(inspect.signature(mod.MaimaiReporterClient.__init__))
print()

# 用默认值创建
client = mod.MaimaiReporterClient()
data = asyncio.run(client.fetch_status())
print('返回类型:', type(data))
print('内容:', str(data)[:2000] if data else None)
