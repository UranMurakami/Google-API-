#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細な共有ドライブアクセス確認スクリプト
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def authenticate_service_account():
    """サービスアカウント認証"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            'sodium-replica-467313-u1-a5e3b290705b.json',
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✅ サービスアカウント認証が成功しました")
        return service
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return None

def check_shared_drive_detailed(service, drive_id):
    """共有ドライブへの詳細なアクセス確認"""
    print(f"\n🔍 共有ドライブID: {drive_id}")
    print("-" * 50)
    
    try:
        # 1. 共有ドライブの基本情報を取得
        print("1️⃣ 共有ドライブの基本情報を確認中...")
        drive = service.drives().get(driveId=drive_id).execute()
        print(f"   ✅ 共有ドライブ名: {drive['name']}")
        print(f"   ✅ 共有ドライブID: {drive['id']}")
        
        # 2. 共有ドライブ内のファイル一覧を取得
        print("\n2️⃣ 共有ドライブ内のファイル一覧を確認中...")
        files = service.files().list(
            driveId=drive_id,
            supportsAllDrives=True,
            fields="files(id,name,mimeType,size,createdTime)",
            pageSize=10
        ).execute()
        
        file_list = files.get('files', [])
        print(f"   ✅ ファイル数: {len(file_list)}")
        
        if file_list:
            print("   📁 ファイル一覧:")
            for file in file_list:
                print(f"      - {file['name']} ({file['mimeType']})")
        else:
            print("   📁 ファイルなし（空の共有ドライブ）")
        
        # 3. フォルダー作成テスト
        print("\n3️⃣ フォルダー作成テスト中...")
        test_folder_metadata = {
            'name': 'テストフォルダー',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [drive_id]
        }
        
        test_folder = service.files().create(
            body=test_folder_metadata,
            supportsAllDrives=True,
            fields='id,name'
        ).execute()
        
        print(f"   ✅ テストフォルダー作成成功: {test_folder['name']} (ID: {test_folder['id']})")
        
        # 4. テストフォルダーを削除
        print("\n4️⃣ テストフォルダーを削除中...")
        service.files().delete(fileId=test_folder['id']).execute()
        print("   ✅ テストフォルダー削除成功")
        
        print("\n🎉 この共有ドライブに完全にアクセス可能です！")
        return True
        
    except HttpError as e:
        if e.resp.status == 404:
            print("   ❌ 共有ドライブが見つかりません")
        elif e.resp.status == 403:
            print("   ❌ アクセス権限がありません")
            print("   💡 サービスアカウントに権限を付与してください")
        else:
            print(f"   ❌ HTTPエラー: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 予期しないエラー: {e}")
        return False

def main():
    print("🔍 詳細な共有ドライブアクセス確認スクリプト")
    print("=" * 60)
    
    # サービスアカウント認証
    service = authenticate_service_account()
    if not service:
        return
    
    # 新しい共有ドライブID
    drive_id = '0AJsrfbnalvHzUk9PVA'
    
    # 詳細な確認
    success = check_shared_drive_detailed(service, drive_id)
    
    print("\n" + "=" * 60)
    print("📊 確認結果")
    print("=" * 60)
    
    if success:
        print("✅ 共有ドライブへのアクセスが確認できました！")
        print("💡 ファイルアップロードを実行できます")
    else:
        print("❌ 共有ドライブへのアクセスができません")
        print("\n🔧 解決方法:")
        print("1. Google Workspace管理者に連絡")
        print("2. サービスアカウントを共有ドライブのメンバーに追加")
        print("3. 適切な権限（編集者以上）を付与")
        print("4. 権限の反映を待つ（数分かかる場合があります）")

if __name__ == "__main__":
    main() 