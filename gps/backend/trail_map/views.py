import json
import logging
from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from geopy.distance import geodesic

from accounts.models import CustomUser
from trail_map.models import Location

logger = logging.getLogger(__name__)


class SaveLocationDataView(APIView):
    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        """CSRF 無効化"""
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def post(request):
        """POST リクエストで位置情報を保存"""
        body_unicode = request.body.decode("utf-8")
        try:
            body_data = json.loads(body_unicode)
        except ():
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        latitude = body_data.get("latitude")
        longitude = body_data.get("longitude")

        if latitude is not None and longitude is not None:
            custom_user = get_object_or_404(CustomUser, token=request.user.token)
            Location.objects.create(latitude=latitude, longitude=longitude, token=custom_user)
            return JsonResponse({"message": "Location saved successfully"}, status=201)
        else:
            return JsonResponse({"error": "Invalid data: latitude and longitude are required"}, status=400)

class GetLocationDataView(APIView):
    def dispatch(self, request, *args, **kwargs):
        """CSRF 無効化"""
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """位置情報を取得（期間フィルタリング）"""
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        data = request.data
        print(f"data: {data}")
        token = request.user.token
        from_datetime = data.get('params', {}).get('from', None)
        to_datetime = data.get('params', {}).get('to', None)


        locations = Location.objects.filter(token=token)
        if from_datetime:
            locations = locations.filter(timestamp__gte=from_datetime)
        if to_datetime:
            locations = locations.filter(timestamp__lte=to_datetime)

        location_data = [
            {
                'latitude': str(location.latitude),
                'longitude': str(location.longitude),
                'timestamp': location.timestamp.isoformat(),
            }
            for location in locations.order_by('timestamp')
        ]
        print(f"location_data.count(): {len(location_data)}")
        print("移動距離計算を開始します。")
        try:
            if len(location_data) > 1:
                total_distance = int(self.calculate_total_distance(location_data))
                daily_distances = self.calculate_daily_distance(location_data)
                print("日付ごとの移動距離",daily_distances)
            else:
                total_distance = 0.0
                daily_distances = {}

            # ログ出力 + データ構築は統一
            print(f"総移動距離: {total_distance:.2f} m")
            data = {
                "location_data": location_data,
                "total_distance": total_distance,
                "daily_distances": daily_distances,
            }
        except Exception as e:
            logger.error(f"エラー詳細: {e}", exc_info=True)
            return JsonResponse({"error": "An error occurred while calculating distance"}, status=500)

        return JsonResponse(data, safe=False)

    @staticmethod
    def calculate_total_distance(location_data):
        total_distance = 0.0

        for i in range(1, len(location_data)):
            prev = location_data[i - 1]
            curr = location_data[i]

            try:
                prev_lat = float(prev["latitude"])
                prev_lon = float(prev["longitude"])
                curr_lat = float(curr["latitude"])
                curr_lon = float(curr["longitude"])

                # ✅ 緯度・経度のバリデーション
                if not (-90 <= prev_lat <= 90):
                    logger.warning(f"Skipping invalid prev_lat: {prev_lat}")
                    continue
                if not (-90 <= curr_lat <= 90):
                    logger.warning(f"Skipping invalid curr_lat: {curr_lat}")
                    continue
                if not (-180 <= prev_lon <= 180):
                    logger.warning(f"Skipping invalid prev_lon: {prev_lon}")
                    continue
                if not (-180 <= curr_lon <= 180):
                    logger.warning(f"Skipping invalid curr_lon: {curr_lon}")
                    continue

                # ✅ 距離計算
                prev_coords = (prev_lat, prev_lon)
                curr_coords = (curr_lat, curr_lon)
                distance = geodesic(prev_coords, curr_coords).meters
                total_distance += distance

            except ValueError as e:
                logger.error(f"Invalid GPS data: {e} (prev: {prev}, curr: {curr})")
                continue  # 異常データはスキップ

        return total_distance

    @staticmethod
    def calculate_daily_distance(location_data):
        """日付ごとの移動距離を計算するメソッド"""
        daily_distances = defaultdict(float)  # 日付ごとの移動距離を保存

        for i in range(1, len(location_data)):
            prev = location_data[i - 1]
            curr = location_data[i]

            try:
                prev_lat = float(prev["latitude"])
                prev_lon = float(prev["longitude"])
                curr_lat = float(curr["latitude"])
                curr_lon = float(curr["longitude"])

                # ✅ 緯度のバリデーションチェック（異常値はスキップ）
                if not (-90 <= prev_lat <= 90):
                    logger.warning(f"Skipping invalid prev_lat: {prev_lat}")
                    continue
                if not (-90 <= curr_lat <= 90):
                    logger.warning(f"Skipping invalid curr_lat: {curr_lat}")
                    continue

                prev_coords = (prev_lat, prev_lon)
                curr_coords = (curr_lat, curr_lon)
                distance = geodesic(prev_coords, curr_coords).meters
                daily_distances[curr["timestamp"][:10]] += distance

            except ValueError as e:
                logger.error(f"Error processing location data: {e}")
                continue  # 異常値はスキップして処理を継続

        return dict(daily_distances)  # 結果を辞書として返す