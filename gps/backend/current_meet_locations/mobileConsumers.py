import json
import asyncio
from datetime import datetime, UTC

from channels.generic.websocket import AsyncWebsocketConsumer



site_locations = {}
active_tasks = {}

class MobileConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.site_uuid = None
        self.user_name = None

    async def connect(self):
        try:
            print("📡 WebSocket 接続要求あり")
            self.site_uuid = self.scope['url_route']['kwargs']['siteUuid']
            self.group_name = f"chat_{self.site_uuid}"
            print(f"group_name: {self.group_name}")

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ 接続成功: {self.group_name}")

            # site_uuid ごとに1回だけ定期送信を開始
            if self.site_uuid not in active_tasks:
                print(f"⏱ 定期送信開始: {self.site_uuid}")
                active_tasks[self.site_uuid] = asyncio.create_task(self.periodic_broadcast())

        except Exception as e:
            print("❌ connect() エラー:", e)
            await self.close()

    async def periodic_broadcast(self):
        while True:
            await asyncio.sleep(30)  # ⏱ 30秒ごと
            members = site_locations.get(self.site_uuid, {})
            if members:
                print(f"📤 定期送信: {members}")
                await self.channel_layer.group_send(
                    f"chat_{self.site_uuid}",
                    {
                        "type": "location.broadcast",
                        "members": members,
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                )

    async def location_broadcast(self, event):
        await self.send(text_data=json.dumps({
            "type": "location_update",
            "members": event["members"]
        }))

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            print("📦 data", data)

            site_uuid = data.get("siteUuid")
            user_name = data.get("userName")
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if not all([site_uuid, user_name, latitude, longitude]):
                await self.send(text_data=json.dumps({"error": "不完全なデータです"}, ensure_ascii=False))
                return

            # サイトごとの辞書を初期化
            if site_uuid not in site_locations:
                site_locations[site_uuid] = {}

            # 更新または新規登録
            site_locations[site_uuid][user_name] = {
                "latitude": latitude,
                "longitude": longitude
            }

            print(f"✅ 保存成功: {user_name}@{site_uuid} → 緯度: {latitude}, 経度: {longitude}")

        except json.JSONDecodeError:
            print("[🔥 JSON パースエラー]")
            await self.send(text_data=json.dumps({
                "error": "不正なJSONです"
            }, ensure_ascii=False))