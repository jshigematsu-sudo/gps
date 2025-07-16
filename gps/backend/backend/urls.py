from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/', include([
        # JWT 認証の取得とリフレッシュ用のエンドポイント
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # ログインでアクセストークンとリフレッシュトークンを取得
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # トークンのリフレッシュ
        path("auth/", include("dj_rest_auth.urls")),  # ログイン・ログアウト
        path("auth/registration/", include("dj_rest_auth.registration.urls")),  # ユーザー登録
        path("trail_map/", include("trail_map.urls")),  # trail_map アプリへのルート
        path('current_meet_locations/', include('current_meet_locations.urls')),
        path("current_member_positions/", include("current_member_positions.urls")),
    ])),
    path("admin/", admin.site.urls),  # 管理サイトのルート（APIに含めない）
]
