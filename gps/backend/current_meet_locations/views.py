import json

from datetime import datetime, timedelta
from django.utils.timezone import is_naive, make_aware, get_current_timezone
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, Location, Sites, SiteMembers, MembersLocations


class CreateMeetingMap(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            body_unicode = request.body.decode("utf-8")
            try:
                body_data = json.loads(body_unicode)
            except ():
                return JsonResponse({"error": "Invalid JSON"}, status=400)
    
            user_name = body_data.get('params', {}).get('loginUserName', None)
            members_name = body_data.get('params', {}).get('memberName', None)
    
            user_latitude = body_data.get('params', {}).get('latitude', None)
            user_longitude = body_data.get('params', {}).get('longitude', None)

    
            # ユーザーが認証されているか確認
            if request.user.is_authenticated:
                name = user_name
                user = User.objects.create(name=user_name)
            else:
                name = members_name
                user = User.objects.create(name=members_name)

            user_location = Location.objects.create(latitude=user_latitude, longitude=user_longitude, user=user)

            print(name)
            return JsonResponse({
                "name": name,
                "latitude": user_location.latitude,
                "longitude": user_location.longitude,
                "timestamp": user_location.timestamp,
            })
        except():
            return JsonResponse({"error": "Internal Server Error"}, status=500)

    @staticmethod
    def get(request, *args, **kwargs):
        member_name = request.GET.get('memberName')
        user_name = request.GET.get('loginUserName')

        # ユーザーが認証されているか確認
        if request.user.is_authenticated:
            name = member_name
            location = Location.objects.filter(user__name=member_name).order_by('-timestamp').first()
        else:
            name = user_name
            location = Location.objects.filter(user__name=user_name).order_by('-timestamp').first()

        if not location:
            return JsonResponse({"message": "No location found"})
        print(name)

        return JsonResponse({
            "otherLocation": {
                "name": name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "timestamp": location.timestamp,
            }
        })


class GetSiteMembers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            site_uuid = request.GET.get('siteUuid')
            site = Sites.objects.get(id=site_uuid)

            # クエリセットの各オブジェクトから名前だけを抽出
            member_names = SiteMembers.objects.filter(site=site_uuid)
            filtered_names = [
                member.name for member in member_names if member.name != site.name
            ]

            member = {
                "creator_name": site.name,
                "members_list": filtered_names
            }

            return JsonResponse(member)
        except Exception as error:
            print(f"Error occurred: {error}")
            return JsonResponse({"error": "Something went wrong"}, status=500)


class SaveSiteData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def post(request, *args, **kwargs):
        print(request)
        try:
            body_unicode = request.body.decode("utf-8")
            body_data = json.loads(body_unicode)

            url = body_data.get('URL')
            creator_name = body_data.get('CreatorName')
            date_range = body_data.get('DateRange')

        except Exception as error:
            print(f"Error occurred: {error}")

        create_site_data = Sites.objects.create(url=url, name=creator_name, date_range=date_range)

        if int(date_range) == 1:
            create_site_data.date_range = date_range

        create_site_data.members.add(SiteMembers.objects.create(name=creator_name, site=create_site_data))

        return JsonResponse({"site_id": create_site_data.id})


class SaveMemberData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            body_unicode = request.body.decode("utf-8")
            body_data = json.loads(body_unicode)
            print(body_data)

            latitude = body_data.get('latitude')
            longitude = body_data.get('longitude')
            name = body_data.get('selectedName')
            site_uuid = body_data.get('siteUuid')

            site = Sites.objects.get(id=site_uuid)

            is_valid = Validator.is_valid(site.created_at, site.date_range)

            if not is_valid:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "このデータは有効期限が切れています。",
                        "code": "expired"
                    },
                    status=400,  # Bad Request または適切なステータスコード
                )

            user = SiteMembers.objects.get(site=site_uuid,name=name)
            created_user = MembersLocations.objects.create(latitude=latitude, longitude=longitude, site_member=user)

            if site.name == name:
                is_edited = True
            else:
                is_edited = False

            return JsonResponse({
                "member_id":user.id,
                "name":name,
                "latitude":created_user.latitude,
                "longitude":created_user.longitude,
                "timestamp":created_user.timestamp,
                "is_edited":is_edited,
            })

        except Exception as error:
            print(f"Error occurred: {error}")
            return JsonResponse(
                {
                    "success": False,
                    "message": "サーバー内部でエラーが発生しました。",
                    "error": str(error)
                },
                status=500,
            )


class GetSiteData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            site_uuid = request.GET.get('siteUuid')

            site = Sites.objects.get(id=site_uuid)

            return JsonResponse({"site_url": site.url},status=200)

        except Exception as error:
            print(f"Error occurred: {error}")



class GetMemberData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            site_uuid = request.GET.get('siteUuid')
            selected_member = request.GET.get('selectedMember')

            site = Sites.objects.get(id=site_uuid)

            if site.name == selected_member:
                is_edited = True
            else:
                is_edited = False

            is_valid = Validator.is_valid(site.created_at, site.date_range)

            if not is_valid:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "このデータは有効期限が切れています。",
                        "code": "expired"
                    },
                    status=400,  # Bad Request または適切なステータスコード
                )

            members = SiteMembers.objects.filter(site=site_uuid)
            print(members)

            # サブクエリで対応する SiteMember の最新の位置情報を取得
            latest_locations = MembersLocations.objects.filter(
                site_member=OuterRef('pk')  # SiteMembers の各メンバーに対応
            ).order_by('-timestamp')  # timestamp の降順に並び替え

            # サイトメンバーごとに最新の `latitude` と `longitude` を取得
            members_with_latest_locations = members.annotate(
                latest_latitude=Subquery(latest_locations.values('latitude')[:1]),  # 最新時刻の latitude
                latest_longitude=Subquery(latest_locations.values('longitude')[:1]),  # 最新時刻の longitude
                latest_timestamp=Subquery(latest_locations.values('timestamp')[:1])  # 最新時刻
            )

            # JSON レスポンス用データを作成
            data = [
                {
                    "member_id": member.id,
                    "name": member.name,
                    "latitude": member.latest_latitude,
                    "longitude": member.latest_longitude,
                    "timestamp": member.latest_timestamp,
                }
                for member in members_with_latest_locations
            ]

            response_data = {"members": data,"is_edited": is_edited}
            print("response_data",response_data)

            # JSON レスポンスを返却
            return JsonResponse(response_data)

        except Exception as error:
                print(f"Error occurred: {error}")


class ManageSiteMember(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            site_uuid = request.GET.get('siteUuid')
            delete_member = request.GET.get('deleteMember')
            new_member = request.GET.get("newMember")

            site = Sites.objects.get(id=site_uuid)

            if delete_member:
                deleted_count, _ = SiteMembers.objects.filter(site=site, name=delete_member).delete()
                if deleted_count == 0:
                    return JsonResponse({"message": "No members deleted"}, status=404)

            if new_member:
                SiteMembers.objects.create(site=site, name=new_member)

            if not site_uuid:
                return JsonResponse({"error": "Invalid parameters"}, status=400)


            return JsonResponse({"message": "success"},status=200)
        except Exception as error:
            print(f"Error occurred: {error}")

    @staticmethod
    def post(request, *args, **kwargs):
        try:
            body_unicode = request.body.decode("utf-8")
            body_data = json.loads(body_unicode)

            site_uuid = body_data.get('siteUuid')
            delete_member = body_data.get('deletedMember')
            new_member = body_data.get("newMember")

            site = Sites.objects.get(id=site_uuid)

            if delete_member:
                deleted_count, _ = SiteMembers.objects.filter(site=site, name=delete_member).delete()
                if deleted_count == 0:
                    return JsonResponse({"message": "No members deleted"}, status=404)

            if new_member:
                SiteMembers.objects.create(site=site, name=new_member)

            if not site_uuid:
                return JsonResponse({"error": "Invalid parameters"}, status=400)

            return JsonResponse({"message": "success"}, status=200)
        except Exception as error:
            print(f"Error occurred: {error}")

class GetDateInfo(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            # 現在の有効時間を取得
            site_uuid = request.GET.get('siteUuid')
            site = Sites.objects.get(id=site_uuid)
            is_valid = Validator.is_valid(site.created_at, site.date_range)

            if not is_valid:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "このデータは有効期限が切れています。",
                        "code": "expired"
                    },
                    status=400,  # Bad Request または適切なステータスコード
                )

            if is_naive(site.created_at):
                create_at = make_aware(site.created_at, get_current_timezone())
            else:
                create_at = site.created_at

            end_date = create_at + timedelta(hours=site.date_range)  # ← 時間で比較！

            return JsonResponse({"EndDate": end_date}, status=200)

        except Exception as error:
            print(f"Error occurred: {error}")


class Validator:
    @staticmethod
    def is_valid(create_at, date_range):
        # 現在日時を取得（タイムゾーン考慮）
        current_date = datetime.now()
        if is_naive(current_date):
            current_date = make_aware(current_date, get_current_timezone())

        # 有効期限 = create_at + date_range 時間
        if is_naive(create_at):
            create_at = make_aware(create_at, get_current_timezone())
        else:
            create_at = create_at

        end_date = create_at + timedelta(hours=date_range)  # ← 時間で比較！

        # 現在時刻が有効期限内かどうかを判定
        return current_date <= end_date

class DeleteSite(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        try:
            site_uuid = request.GET.get('siteUuid')
            site = Sites.objects.get(id=site_uuid)
            site.delete()
            return JsonResponse({"message": "success"},status=200)
        except Exception as error:
            print(f"Error occurred: {error}")








