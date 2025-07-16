from django.contrib.auth.hashers import make_password
from django.db import models


class Group(models.Model):
    id = models.AutoField(primary_key=True)  # グループのID
    name = models.CharField(max_length=255, unique=True)  # グループ名（一意制約）
    password = models.CharField(max_length=128, default="123")  # パスワードフィールド

    def __str__(self):
        return self.name


class UserCurrentPosition(models.Model):
    id = models.AutoField(primary_key=True)  # 主キーとして id を自動採番
    token = models.ForeignKey(
        'accounts.CustomUser',  # accounts_customer テーブルの token を参照
        on_delete=models.CASCADE,
        related_name='current_member_positions',  # 一意な関連名
        to_field='token'
    )
    group = models.ForeignKey(
        'Group',  # Groupテーブルを参照
        on_delete=models.CASCADE,  # グループ削除時に関連するユーザー情報も削除
        related_name='members'  # 一意な関連名
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['token', 'group'], name='unique_token_group')
        ]

    def __str__(self):
        return f'ID: {self.id} - User: {self.token.username} - Group: {self.group.name}'
