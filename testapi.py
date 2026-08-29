import sys, asyncio
sys.path.insert(0, '/root/awesome-bot/.venv/lib/python3.12/site-packages')
from nonebot_plugin_maimaimonitor.client import MaimaiReporterClient
client = MaimaiReporterClient()
data = asyncio.run(client.fetch_status())
print('类型:', type(data))
print('内容:', str(data)[:1500] if data else None)
