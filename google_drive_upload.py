#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GoogleドライブAPIを使用してファイルをアップロードするスクリプト
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

def get_folder_id_by_name(service, folder_name):
    """
    フォルダー名からフォルダーIDを取得する
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        folder_name (str): フォルダー名
    
    Returns:
        str: フォルダーID（見つからない場合はNone）
    """
    try:
        # フォルダーを検索
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
        results = service.files().list(
            q=query,
            fields="files(id, name)"
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
            print(f"📁 フォルダー '{folder_name}' が見つかりました (ID: {folder_id})")
            return folder_id
        else:
            print(f"❌ フォルダー '{folder_name}' が見つかりませんでした")
            return None
            
    except HttpError as error:
        print(f"❌ フォルダー検索エラー: {error}")
        return None

def list_folders(service):
    """
    利用可能なフォルダー一覧を表示する
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
    """
    try:
        # フォルダーのみを検索
        query = "mimeType='application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            fields="files(id, name, createdTime)"
        ).execute()
        
        folders = results.get('files', [])
        
        if not folders:
            print("📁 フォルダーが見つかりませんでした")
            return
        
        print("\n📂 利用可能なフォルダー一覧:")
        print("="*50)
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder['name']} (ID: {folder['id']})")
        print("="*50)
        
    except HttpError as error:
        print(f"❌ フォルダー一覧取得エラー: {error}")

def upload_file(service, file_path, folder_id=None, new_filename=None):
    """
    ファイルをGoogleドライブにアップロードする
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        file_path (str): アップロードするファイルのパス
        folder_id (str): アップロード先のフォルダーID（Noneの場合はルート）
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
            print(f"   アップロード先: ルート")
        
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

def upload_file_to_folder(service, file_path, folder_name, new_filename=None):
    """
    ファイルを指定したフォルダー名のフォルダーにアップロードする
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        file_path (str): アップロードするファイルのパス
        folder_name (str): アップロード先のフォルダー名
        new_filename (str): 新しいファイル名（Noneの場合は元のファイル名）
    
    Returns:
        dict: アップロードされたファイルの情報
    """
    # フォルダーIDを取得
    folder_id = get_folder_id_by_name(service, folder_name)
    if not folder_id:
        return None
    
    # ファイルをアップロード
    return upload_file(service, file_path, folder_id, new_filename)

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
    
    # 利用可能なフォルダー一覧を表示
    list_folders(service)
    
    # アップロード例
    print("\n" + "="*60)
    print("📤 ファイルアップロード例")
    print("="*60)
    
    # 例1: ルートにアップロード
    print("\n1️⃣ ルートにアップロード:")
    # upload_file(service, "example.txt")  # コメントアウト
    
    # 例2: 指定したフォルダーにアップロード
    print("\n2️⃣ 指定したフォルダーにアップロード:")
    # upload_file_to_folder(service, "example.txt", "GoogleドライブAPI連携用")  # コメントアウト
    
    print("\n💡 使用方法:")
    print("   upload_file(service, 'ファイルパス', 'フォルダーID')")
    print("   upload_file_to_folder(service, 'ファイルパス', 'フォルダー名')")

if __name__ == "__main__":
    main() 