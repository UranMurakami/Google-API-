#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
利用可能な共有ドライブを一覧表示するスクリプト
"""

from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 設定情報
CREDENTIALS_FILE = 'sodium-replica-467313-u1-a5e3b290705b.json'

def authenticate_service_account():
    """サービスアカウント認証"""
    try:
        script_dir = Path(__file__).parent
        credentials_path = script_dir / CREDENTIALS_FILE
        
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✅ サービスアカウント認証が成功しました")
        return service
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return None

def list_shared_drives(service):
    """利用可能な共有ドライブを一覧表示"""
    try:
        print("\n🔍 利用可能な共有ドライブを確認中...")
        
        # 共有ドライブの一覧を取得
        results = service.drives().list(
            pageSize=100,
            fields="drives(id,name,createdTime,createdBy)"
        ).execute()
        
        drives = results.get('drives', [])
        
        if not drives:
            print("❌ アクセス可能な共有ドライブが見つかりません")
            print("💡 サービスアカウントが共有ドライブのメンバーに追加されているか確認してください")
            return None
        
        print(f"📊 利用可能な共有ドライブ数: {len(drives)}")
        print("\n📋 共有ドライブ一覧:")
        
        for i, drive in enumerate(drives, 1):
            print(f"\n{i}. 📂 共有ドライブ名: {drive.get('name', 'N/A')}")
            print(f"   🆔 共有ドライブID: {drive.get('id', 'N/A')}")
            print(f"   📅 作成日時: {drive.get('createdTime', 'N/A')}")
            print(f"   👤 作成者: {drive.get('createdBy', {}).get('displayName', 'N/A')}")
        
        return drives
        
    except HttpError as error:
        print(f"❌ 共有ドライブ一覧取得エラー: {error}")
        return None

def check_my_drive_access(service):
    """マイドライブへのアクセス確認"""
    try:
        print("\n🔍 マイドライブへのアクセスを確認中...")
        
        # マイドライブのルートフォルダーを取得
        results = service.files().list(
            pageSize=1,
            fields="files(id,name,mimeType)"
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            print("✅ マイドライブにアクセス可能")
            print("💡 ただし、サービスアカウントは個人ドライブへの書き込みが制限されています")
        else:
            print("❌ マイドライブにアクセスできません")
        
        return True
        
    except HttpError as error:
        print(f"❌ マイドライブアクセスエラー: {error}")
        return False

def main():
    """メイン処理"""
    print("🔍 利用可能な共有ドライブ確認スクリプト")
    print("="*60)
    
    # 1. サービスアカウント認証
    service = authenticate_service_account()
    if not service:
        return
    
    # 2. 共有ドライブ一覧取得
    drives = list_shared_drives(service)
    
    # 3. マイドライブアクセス確認
    check_my_drive_access(service)
    
    # 4. 結果表示
    print("\n" + "="*60)
    print("📊 確認結果")
    print("="*60)
    
    if drives:
        print(f"✅ 共有ドライブアクセス: 成功 ({len(drives)}個の共有ドライブ)")
        print("\n💡 利用可能な共有ドライブIDを使用してアップロードしてください")
        
        # 最初の共有ドライブを推奨
        if drives:
            recommended_drive = drives[0]
            print(f"\n🎯 推奨共有ドライブ:")
            print(f"   名前: {recommended_drive.get('name')}")
            print(f"   ID: {recommended_drive.get('id')}")
    else:
        print("❌ 共有ドライブアクセス: 失敗")
        print("\n⚠️ 以下の手順を実行してください:")
        print("   1. Google Workspace管理者に連絡")
        print("   2. サービスアカウントを共有ドライブのメンバーに追加")
        print("   3. 適切な権限（編集者以上）を付与")

if __name__ == "__main__":
    main() 