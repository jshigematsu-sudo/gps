import json
import traceback

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import MeetingChats, SiteMembers
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    online_users_map = {}
    # グループ名などの接続固有データ
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.site_uuid = None
        self.user_name = None

    async def connect(self):
        try:
            print("📡 WebSocket 接続要求あり")

            self.site_uuid = self.scope['url_route']['kwargs']['membersNameParameter']
            self.group_name = f"chat_{self.site_uuid}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ 接続成功: {self.group_name}")

            await self.send_chat_history()
        except Exception as e:
            print("❌ connect() エラー:", e)
            await self.close()

    async def disconnect(self, close_code):
        print(f"⚠️ WebSocket切断: {close_code}")
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

            if self.site_uuid and self.user_name:
                print("👋 切断したユーザー:", self.user_name)
                self.online_users_map[self.site_uuid].discard(self.user_name)

                print("🧑‍🤝‍🧑 更新後オンライン:", self.online_users_map[self.site_uuid])

                await self.channel_layer.group_send(self.group_name, {
                    "type": "status_message",
                    "online_users": list(self.online_users_map[self.site_uuid]),
                })
            else:
                print("🐛 切断データ:" ,self.site_uuid, self.user_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            print("📦 data", data)

            msg_type = data.get("type")

            if msg_type == "status":
                await self.handle_status(data)
                return

            if msg_type in (None, "chat"):
                await self.handle_chat_message(data)

        except Exception:
            print("[🔥 receive() エラー]")
            print(traceback.format_exc())
            await self.send(text_data=json.dumps({
                "error": "内部エラーが発生しました"
            }, ensure_ascii=False))

    async def handle_status(self, data):
        site_id = self.site_uuid
        sender = data.get("sender_name")
        status = data.get("status")

        self.user_name = sender

        # 初期化（サイトごとに記録）
        if site_id not in self.online_users_map:
            self.online_users_map[site_id] = set()

        if status == "online":
            self.online_users_map[site_id].add(sender)
        elif status == "offline":
            self.online_users_map[site_id].discard(sender)

        print(f"🌐 現在のオンライン: {self.online_users_map[site_id]}")

        # 全クライアントに現在のオンラインユーザー一覧を送信
        await self.channel_layer.group_send(self.group_name, {
            "type": "status_message",
            "online_users": list(self.online_users_map[site_id]),
        })

    async def status_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "online_users": event.get("online_users", []),
        }, ensure_ascii=False))

    async def handle_chat_message(self, data):
        message = data.get("message")
        sender = data.get("sender")
        if not sender:
            await self.send(text_data=json.dumps({
                "error": "sender が指定されていません"
            }, ensure_ascii=False))
            return

        print(f"[📩 受信] message: {message}")
        print(f"[🔍 sender={sender}, site_id={self.site_uuid}]")

        site_member = await sync_to_async(SiteMembers.objects.get)(
            name=sender,
            site_id=self.site_uuid
        )

        await sync_to_async(MeetingChats.objects.create)(
            site_id=self.site_uuid,
            site_member_id=site_member.id,
            message=message
        )

        await self.channel_layer.group_send(self.group_name, {
            "type": "chat_message",
            "message": message,
            "sender_name": sender,
            "sender_channel": self.channel_name,
            "sender_id": site_member.id,
        })

    async def send_chat_history(self):
        try:
            history = await sync_to_async(
                lambda: list(
                    MeetingChats.objects.filter(
                        site_id=self.site_uuid
                    ).order_by("timestamp").values("message", "timestamp", "site_member__name")
                )
            )()

            for chat in history:
                await self.send(text_data=json.dumps({
                    "message": chat["message"],
                    "sender_name": chat["site_member__name"],
                    "timestamp": chat["timestamp"].isoformat(),
                    "type": "history"
                }, ensure_ascii=False))
        except Exception as e:
            print("❌ チャット履歴の送信エラー:", e)

    async def chat_message(self, event):
        if event.get("sender_channel") == self.channel_name:
            return  # 自分には送らない

        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_name": event["sender_name"],
            "type": "chat"
        }, ensure_ascii=False))