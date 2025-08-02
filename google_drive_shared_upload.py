#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GoogleドライブAPIを使用して共有ドライブにファイルをアップロードするスクリプト
サービスアカウント認証を使用
"""

import os
import mimetypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# スコープの定義（読み書き権限）
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_service_account(credentials_file):
    """
    サービスアカウントで認証を行う
    
    Args:
        credentials_file (str): サービスアカウントのJSONファイルパス
    
    Returns:
        googleapiclient.discovery.Resource: 認証されたDrive APIサービスオブジェクト
    """
    try:
        # サービスアカウントの認証情報を読み込み
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=SCOPES
        )
        
        # Drive APIサービスを構築
        service = build('drive', 'v3', credentials=credentials)
        print("✅ サービスアカウント認証が成功しました")
        return service
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return None

def list_shared_drives(service):
    """
    利用可能な共有ドライブ一覧を表示する
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
    """
    try:
        # 共有ドライブを取得
        drives = service.drives().list().execute()
        drive_list = drives.get('drives', [])
        
        if not drive_list:
            print("📁 共有ドライブが見つかりませんでした")
            print("💡 共有ドライブを作成するか、既存の共有ドライブにサービスアカウントを追加してください")
            return []
        
        print("\n📂 利用可能な共有ドライブ一覧:")
        print("="*60)
        for i, drive in enumerate(drive_list, 1):
            print(f"{i}. {drive['name']} (ID: {drive['id']})")
            print(f"   作成者: {drive.get('createdBy', {}).get('displayName', '不明')}")
            print(f"   作成日時: {drive.get('createdTime', '不明')}")
            print()
        print("="*60)
        
        return drive_list
        
    except HttpError as error:
        print(f"❌ 共有ドライブ一覧取得エラー: {error}")
        return []

def list_folders_in_shared_drive(service, drive_id):
    """
    共有ドライブ内のフォルダー一覧を表示する
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        drive_id (str): 共有ドライブID
    """
    try:
        # 共有ドライブ内のフォルダーを検索
        query = f"'{drive_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            fields="files(id, name, createdTime)"
        ).execute()
        
        folders = results.get('files', [])
        
        if not folders:
            print(f"📁 共有ドライブ内にフォルダーが見つかりませんでした")
            return []
        
        print(f"\n📂 共有ドライブ内のフォルダー一覧:")
        print("="*50)
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder['name']} (ID: {folder['id']})")
        print("="*50)
        
        return folders
        
    except HttpError as error:
        print(f"❌ フォルダー一覧取得エラー: {error}")
        return []

def upload_file_to_shared_drive(service, file_path, drive_id, folder_id=None, new_filename=None):
    """
    ファイルを共有ドライブにアップロードする
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        file_path (str): アップロードするファイルのパス
        drive_id (str): 共有ドライブID
        folder_id (str): アップロード先のフォルダーID（Noneの場合は共有ドライブのルート）
        new_filename (str): 新しいファイル名（Noneの場合は元のファイル名）
    
    Returns:
        dict: アップロードされたファイルの情報
    """
    try:
        # ファイルの存在確認
        if not os.path.exists(file_path):
            print(f"❌ ファイルが見つかりません: {file_path}")
            return None
        
        # ファイル名を取得
        if new_filename:
            filename = new_filename
        else:
            filename = os.path.basename(file_path)
        
        # MIMEタイプを取得
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        # ファイルサイズを取得
        file_size = os.path.getsize(file_path)
        print(f"📁 アップロード情報:")
        print(f"   ファイル名: {filename}")
        print(f"   ファイルサイズ: {file_size:,} bytes")
        print(f"   MIMEタイプ: {mime_type}")
        print(f"   共有ドライブID: {drive_id}")
        
        # メタデータを準備
        file_metadata = {
            'name': filename,
            'mimeType': mime_type
        }
        
        # フォルダーIDが指定されている場合は親フォルダーを設定
        if folder_id:
            file_metadata['parents'] = [folder_id]
            print(f"   アップロード先: フォルダーID {folder_id}")
        else:
            print(f"   アップロード先: 共有ドライブルート")
        
        # メディアアップロードオブジェクトを作成
        media = MediaFileUpload(
            file_path,
            mimetype=mime_type,
            resumable=True
        )
        
        print("🚀 アップロードを開始します...")
        
        # ファイルをアップロード
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,
            fields='id, name, size, webViewLink, createdTime'
        ).execute()
        
        print("✅ アップロードが完了しました！")
        print(f"   ファイルID: {file.get('id')}")
        print(f"   ファイル名: {file.get('name')}")
        print(f"   ファイルサイズ: {file.get('size', '不明')} bytes")
        print(f"   作成日時: {file.get('createdTime')}")
        print(f"   リンク: {file.get('webViewLink')}")
        
        return file
        
    except HttpError as error:
        print(f"❌ アップロードエラー: {error}")
        return None
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return None

def create_shared_drive(service, drive_name):
    """
    新しい共有ドライブを作成する
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        drive_name (str): 共有ドライブ名
    
    Returns:
        dict: 作成された共有ドライブの情報
    """
    try:
        drive_metadata = {
            'name': drive_name
        }
        
        drive = service.drives().create(
            body=drive_metadata,
            requestId='unique-request-id-' + str(hash(drive_name))
        ).execute()
        
        print(f"✅ 共有ドライブ '{drive_name}' が作成されました (ID: {drive['id']})")
        return drive
        
    except HttpError as error:
        print(f"❌ 共有ドライブ作成エラー: {error}")
        return None

def main():
    """
    メイン関数
    """
    # サービスアカウントのJSONファイルパス
    credentials_file = "disco-vista-466212-a2-611d98d41f0c.json"
    
    # ファイルの存在確認
    if not os.path.exists(credentials_file):
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        return
    
    print("🚀 GoogleドライブAPIに接続中...")
    
    # サービスアカウントで認証
    service = authenticate_service_account(credentials_file)
    if not service:
        return
    
    # 利用可能な共有ドライブ一覧を表示
    shared_drives = list_shared_drives(service)
    
    if not shared_drives:
        print("\n💡 共有ドライブがありません。新しい共有ドライブを作成しますか？")
        print("   例: create_shared_drive(service, 'テスト用共有ドライブ')")
        return
    
    # 最初の共有ドライブを使用
    drive_id = shared_drives[0]['id']
    drive_name = shared_drives[0]['name']
    
    print(f"\n📂 共有ドライブ '{drive_name}' を使用します")
    
    # 共有ドライブ内のフォルダー一覧を表示
    folders = list_folders_in_shared_drive(service, drive_id)
    
    print("\n" + "="*60)
    print("📤 共有ドライブへのファイルアップロード例")
    print("="*60)
    
    # テストファイルを作成
    test_content = "これは共有ドライブにアップロードされたテストファイルです。"
    with open("shared_drive_test.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # 共有ドライブのルートにアップロード
    print("\n1️⃣ 共有ドライブルートにアップロード:")
    result = upload_file_to_shared_drive(service, "shared_drive_test.txt", drive_id)
    
    if result:
        print("✅ 共有ドライブへのアップロードが成功しました！")
    else:
        print("❌ 共有ドライブへのアップロードが失敗しました")
    
    print("\n💡 使用方法:")
    print("   upload_file_to_shared_drive(service, 'ファイルパス', '共有ドライブID')")
    print("   create_shared_drive(service, '共有ドライブ名')")

if __name__ == "__main__":
    main() 