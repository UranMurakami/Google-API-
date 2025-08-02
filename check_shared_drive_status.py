#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共有ドライブの状況を確認するスクリプト
"""

import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 設定情報
SHARED_DRIVE_CONFIG = {
    'drive_id': '0AJsrfbnalvHzUk9PVA',
    'drive_name': '売り上げデータ管理用共有ドライブ',
    'service_account_email': 'googledrive-api@sodium-replica-467313-u1.iam.gserviceaccount.com',
    'credentials_file': 'sodium-replica-467313-u1-a5e3b290705b.json'
}

def authenticate_service_account():
    """サービスアカウント認証"""
    try:
        script_dir = Path(__file__).parent
        credentials_path = script_dir / SHARED_DRIVE_CONFIG['credentials_file']
        
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

def check_shared_drive_access(service):
    """共有ドライブへのアクセス権限を確認"""
    try:
        print(f"\n🔍 共有ドライブの状況を確認中...")
        print(f"📂 共有ドライブ名: {SHARED_DRIVE_CONFIG['drive_name']}")
        print(f"🆔 共有ドライブID: {SHARED_DRIVE_CONFIG['drive_id']}")
        
        # 共有ドライブの詳細情報を取得
        drive = service.drives().get(driveId=SHARED_DRIVE_CONFIG['drive_id']).execute()
        
        print(f"✅ 共有ドライブにアクセス可能")
        print(f"📊 共有ドライブ名: {drive.get('name', 'N/A')}")
        print(f"🆔 共有ドライブID: {drive.get('id', 'N/A')}")
        print(f"📅 作成日時: {drive.get('createdTime', 'N/A')}")
        print(f"👤 作成者: {drive.get('createdBy', {}).get('displayName', 'N/A')}")
        
        return True
        
    except HttpError as error:
        print(f"❌ 共有ドライブアクセスエラー: {error}")
        return False

def list_shared_drive_contents(service):
    """共有ドライブの内容を一覧表示"""
    try:
        print(f"\n📁 共有ドライブの内容を確認中...")
        
        # 共有ドライブ内のファイルとフォルダーを取得
        results = service.files().list(
            driveId=SHARED_DRIVE_CONFIG['drive_id'],
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="files(id,name,mimeType,createdTime,size)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("📂 共有ドライブは空です")
            return
        
        print(f"📊 ファイル・フォルダー数: {len(files)}")
        print("\n📋 内容一覧:")
        
        for file in files:
            file_type = "📁 フォルダー" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄 ファイル"
            size = f" ({file.get('size', 'N/A')} bytes)" if file.get('size') else ""
            print(f"   {file_type}: {file['name']} (ID: {file['id']}){size}")
        
        return files
        
    except HttpError as error:
        print(f"❌ 共有ドライブ内容取得エラー: {error}")
        return None

def test_file_upload(service):
    """テストファイルのアップロードを試行"""
    try:
        print(f"\n🧪 テストファイルアップロードを試行中...")
        
        # テストファイルを作成
        test_content = "これはテストファイルです。\n共有ドライブへのアップロードテスト用です。"
        test_file_path = "test_upload_shared_drive.txt"
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # ファイルメタデータ
        file_metadata = {
            'name': 'test_upload_shared_drive.txt',
            'parents': [SHARED_DRIVE_CONFIG['drive_id']]
        }
        
        # ファイルをアップロード
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(test_file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,
            supportsTeamDrives=True,
            fields='id,name,size'
        ).execute()
        
        print(f"✅ テストファイルアップロード成功: {file['name']} (ID: {file['id']})")
        
        # テストファイルを削除
        os.remove(test_file_path)
        
        return True
        
    except HttpError as error:
        print(f"❌ テストファイルアップロードエラー: {error}")
        return False
    except Exception as e:
        print(f"❌ テストファイル作成エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🔍 共有ドライブ状況確認スクリプト")
    print("="*50)
    
    # 1. サービスアカウント認証
    service = authenticate_service_account()
    if not service:
        return
    
    # 2. 共有ドライブアクセス確認
    if not check_shared_drive_access(service):
        return
    
    # 3. 共有ドライブ内容確認
    files = list_shared_drive_contents(service)
    
    # 4. テストファイルアップロード
    test_result = test_file_upload(service)
    
    # 5. 結果表示
    print("\n" + "="*50)
    print("📊 確認結果")
    print("="*50)
    print(f"✅ 共有ドライブアクセス: {'成功' if check_shared_drive_access(service) else '失敗'}")
    print(f"📁 内容確認: {'成功' if files is not None else '失敗'}")
    print(f"📤 テストアップロード: {'成功' if test_result else '失敗'}")
    
    if test_result:
        print("\n💡 共有ドライブへのアップロードが可能です")
    else:
        print("\n⚠️ 共有ドライブへのアップロードに問題があります")
        print("   サービスアカウントの権限を確認してください")

if __name__ == "__main__":
    main() 