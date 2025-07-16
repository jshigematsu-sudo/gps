import datetime
from django.utils.timezone import now
from accounts.models import CustomUser
from django.db import models


class Location(models.Model):
    """位置情報を格納するモデル"""

    # トークンとの関連（ForeignKey）
    token = models.ForeignKey(CustomUser, to_field='token', on_delete=models.CASCADE, db_column='token')

    # 位置情報（緯度、経度）
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    # 位置情報の登録日時
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location at {self.timestamp}"

    class Meta:
        verbose_name_plural = 'Locations'
        constraints = [
            models.UniqueConstraint(fields=['token', 'timestamp'], name='unique_token_timestamp')
        ]


class RequestLog(models.Model):
    # ユーザーとの関連付け（ForeignKey の設定）
    USER_COLUMN = 'user'
    user = models.ForeignKey(
        CustomUser,
        to_field='token',  # Unique Token from CustomUser
        on_delete=models.CASCADE,
        db_column=USER_COLUMN
    )
    count = models.PositiveIntegerField(default=0)  # アクセス回数
    last_called_at = models.DateTimeField(auto_now_add=True)  # 初期生成時の記録開始日時

    def update_last_called(self):
        """ログを現在の日付に更新（時刻部分を切り捨てる）"""
        today = now().date()  # 現在の日付（例: 2023-10-25）
        self.last_called_at = datetime.combine(today, datetime.min.time())  # 0時にリセット
        self.save(update_fields=['last_called_at'])
