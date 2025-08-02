#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共有ドライブアクセス権限確認スクリプト
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

def check_shared_drive_access(service):
    """共有ドライブへのアクセス権限を確認"""
    print("\n🔍 共有ドライブアクセス権限を確認中...")
    
    # 複数の共有ドライブIDを試す
    drive_ids = [
        '0AJsrfbnalvHzUk9PVA',  # 新しい共有ドライブID
        '1zv3ex_Jx1z6TJznXlaLkbeYgX6PR7B0s',  # 以前の設定（バックアップ）
        '1IkyFnANAdcEeagKpbc8_UhKUcMTjqgkc',  # 古い設定（バックアップ）
    ]
    
    for drive_id in drive_ids:
        print(f"\n📂 共有ドライブID: {drive_id}")
        try:
            # 共有ドライブの情報を取得
            drive = service.drives().get(driveId=drive_id).execute()
            print(f"✅ 共有ドライブ名: {drive['name']}")
            if 'createdTime' in drive:
                print(f"✅ 作成日時: {drive['createdTime']}")
            else:
                print("✅ 作成日時: 情報なし")
            
            # 共有ドライブ内のファイル一覧を取得
            files = service.files().list(
                driveId=drive_id,
                supportsAllDrives=True,
                fields="files(id,name,mimeType,size)"
            ).execute()
            
            print(f"✅ ファイル数: {len(files.get('files', []))}")
            print("✅ この共有ドライブにアクセス可能です！")
            return drive_id
            
        except HttpError as e:
            if e.resp.status == 404:
                print("❌ 共有ドライブが見つかりません")
            elif e.resp.status == 403:
                print("❌ アクセス権限がありません")
            else:
                print(f"❌ エラー: {e}")
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
    
    return None

def check_my_drive_access(service):
    """マイドライブへのアクセスを確認"""
    print("\n🔍 マイドライブへのアクセスを確認中...")
    try:
        files = service.files().list(
            pageSize=5,
            fields="files(id,name,mimeType)"
        ).execute()
        
        print("✅ マイドライブにアクセス可能")
        print(f"📁 ファイル数: {len(files.get('files', []))}")
        return True
        
    except Exception as e:
        print(f"❌ マイドライブアクセスエラー: {e}")
        return False

def main():
    print("🔍 共有ドライブアクセス権限確認スクリプト")
    print("=" * 50)
    
    # サービスアカウント認証
    service = authenticate_service_account()
    if not service:
        return
    
    # マイドライブアクセス確認
    check_my_drive_access(service)
    
    # 共有ドライブアクセス確認
    accessible_drive_id = check_shared_drive_access(service)
    
    print("\n" + "=" * 50)
    print("📊 確認結果")
    print("=" * 50)
    
    if accessible_drive_id:
        print(f"✅ 利用可能な共有ドライブID: {accessible_drive_id}")
        print("💡 このIDを使用してアップロードスクリプトを更新してください")
    else:
        print("❌ 利用可能な共有ドライブが見つかりません")
        print("\n🔧 解決方法:")
        print("1. Google Workspace管理者に連絡")
        print("2. サービスアカウントを共有ドライブのメンバーに追加")
        print("3. 適切な権限（編集者以上）を付与")

if __name__ == "__main__":
    main() 