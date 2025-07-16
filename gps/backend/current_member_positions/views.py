import json
from os import error

from allauth.headless.base.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from trail_map.models import Location
from .models import UserCurrentPosition, Group

User = get_user_model()

class GetMembersPosition(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            jwt_auth = JWTAuthentication()
            user_auth_tuple = jwt_auth.authenticate(request)

            data = json.loads(request.body)  # JSONデータを取得
            group_name = data.get("requestData", {}).get("group_name")

            if user_auth_tuple is None:
                return JsonResponse({"error": "Authentication failed"}, status=401)

            user, token = user_auth_tuple
            request.user = user  # 🔹 ここで request.user にセットする

            print(f"Authenticated User: {request.user}")  # ここで取得できるか確認
            print(f"User Token: {request.user.token}")  # 🔹 request.user.token を取得する


            user_token = request.user.token

            # ユーザーが所属するグループのグループIDを取得
            print(user_token)
            print(group_name)

            if group_name:
                group_data = Group.objects.filter(name=group_name).values('id').first()
                group_id = group_data['id'] if group_data else None
            else:
                group_data = self.get_group_id_by_token(user_token)
                group_id = group_data['group_id'] if group_data else None

            if not group_id:
                return JsonResponse({"error": "Group not found."}, status=404)

            # グループメンバーを取得
            group_members = self.get_group_members(group_id)
            if not group_members:
                return JsonResponse({"error": "No group members found."}, status=404)

            # 最新の位置情報を取得
            latest_locations = self.get_latest_locations(group_members)

            # 結果をログ出力（オプション）
            self.log_latest_locations(latest_locations)

            my_group_names = self.get_context_data()

            print(f"my_group_names: {my_group_names}")

            return JsonResponse({"latest_locations": list(latest_locations), "my_group_names": my_group_names}, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print("Unexpected Error:", str(e))  # Django のログで確認
            return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500)

    @staticmethod
    def get_group_id_by_token(token):
        return UserCurrentPosition.objects.filter(token_id=token).values('group_id').first()

    def get_context_data(self, **kwargs):
        # 自分の所属グループの情報を取得して処理
        self_group_ids = self.get_user_group_ids()
        self_group_names = list(self.get_group_names(self_group_ids).values_list("name", flat=True))

        return self_group_names

    def get_user_group_ids(self):
        """ログインユーザーのグループID一覧を取得"""
        user_token = self.request.user.token
        return UserCurrentPosition.objects.filter(token_id=user_token).values_list('group_id', flat=True)

    @staticmethod
    def get_group_names(group_ids):
        """グループIDからグループ名一覧を取得"""
        if group_ids:
            return Group.objects.filter(id__in=group_ids).values_list('name', flat=True)
        return []

    @staticmethod
    def get_group_members(group_id):
        return UserCurrentPosition.objects.filter(group_id=group_id)

    @staticmethod
    def get_latest_locations(group_members):
        # `group_members`からトークンリストを取得
        member_tokens = group_members.values_list('token', flat=True)

        latest_locations = Location.objects.filter(
            token__in=member_tokens
        ).filter(
            timestamp=Subquery(
                Location.objects.filter(token=OuterRef('token'))
                .order_by('-timestamp')
                .values('timestamp')[:1]
            )
        ).values('token', 'latitude', 'longitude', 'timestamp', 'token__username')

        return latest_locations

    @staticmethod
    def log_latest_locations(locations):
        for location in locations:
            print(
                f"Token: {location['token']}, Latitude: {location['latitude']}, "
                f"Longitude: {location['longitude']}, Time: {location['timestamp']},Username: {location['token__username']}"
            )


class JoinNewGroup(APIView):
    permission_classes = [IsAuthenticated]
    ERROR_INVALID_JSON = {"error": "Invalid JSON"}
    ERROR_MISSING_CREDENTIALS = {"error": "Missing id or password"}
    ERROR_AUTH_FAILED = {
        "status": "error",
        "message": "認証失敗"
    }
    SUCCESS_AUTH_SUCCESS = {
        "status": "success",
        "message": "認証成功し、グループに参加しました。"
    }

    @staticmethod
    def parse_request_body(request_body):
        """リクエストのJSONボディを辞書に変換"""
        try:
            return json.loads(request_body.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    @staticmethod
    def validate_credentials(body_data):
        """認証情報が存在するか確認"""
        group_id = body_data.get("group_id")
        password = body_data.get("password")
        if not group_id or not password:
            return None, None
        return group_id, password

    def post(self, request, *args, **kwargs):
        jwt_auth = JWTAuthentication()
        user_auth_tuple = jwt_auth.authenticate(request)
        user, token = user_auth_tuple
        request.user = user

        body_unicode = request.body.decode("utf-8")
        try:
            body_data = json.loads(body_unicode)
        except ():
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        group_id = body_data.get("groupId")  # "1"
        password = body_data.get("password")
        try:
            if Group.objects.filter(id=group_id, password=password).exists():
                user_position = UserCurrentPosition(group_id=group_id, token=request.user)
                user_position.save()
                return JsonResponse(self.SUCCESS_AUTH_SUCCESS)
        except error:
            return JsonResponse({"error": error}, status=400)

        return JsonResponse(self.ERROR_AUTH_FAILED, status=403)