#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存の分割済み売り上げデータを共有ドライブにアップロード（修正版）
全角スペースを含むパスでも確実に動作
"""

import os
import sys
import glob
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# 設定情報（直接記述）
SHARED_DRIVE_CONFIG = {
    'drive_id': '0AJsrfbnalvHzUk9PVA',
    'drive_name': '売り上げデータ管理用共有ドライブ',
    'service_account_email': 'googledrive-api@sodium-replica-467313-u1.iam.gserviceaccount.com',
    'credentials_file': 'sodium-replica-467313-u1-a5e3b290705b.json'
}

def authenticate_service_account():
    """サービスアカウント認証"""
    try:
        # 現在のスクリプトのディレクトリを基準にパスを解決
        script_dir = Path(__file__).parent
        credentials_path = script_dir / SHARED_DRIVE_CONFIG['credentials_file']
        
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print("✅ サービスアカウント認証が成功しました")
        return service
        
    except FileNotFoundError:
        print(f"❌ 認証ファイルが見つかりません: {SHARED_DRIVE_CONFIG['credentials_file']}")
        return None
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return None

def get_existing_split_files():
    """既存の分割済みCSVファイルを取得"""
    try:
        csv_files = []
        
        # 現在のスクリプトのディレクトリを基準にパスを解決
        script_dir = Path(__file__).parent
        sales_data_split_dir = script_dir / "sales_data_split"
        
        if not sales_data_split_dir.exists():
            print(f"❌ sales_data_splitディレクトリが見つかりません: {sales_data_split_dir}")
            return None
        
        # sales_data_splitフォルダ内のCSVファイルを検索
        pattern = str(sales_data_split_dir / "**" / "*.csv")
        files = glob.glob(pattern, recursive=True)
        
        for file_path in sorted(files):
            file_path_obj = Path(file_path)
            filename = file_path_obj.name
            dir_path = file_path_obj.parent
            year = dir_path.name  # 2023, 2024
            
            # ファイル名から月を抽出 (例: 2023年01月_売上データ.csv)
            if "年" in filename and "月" in filename:
                month_part = filename.split("年")[1].split("月")[0]
                month = int(month_part)
                
                csv_files.append({
                    'file_path': str(file_path_obj),
                    'filename': filename,
                    'year': int(year),
                    'month': month,
                    'year_folder': f"{year}年",
                    'month_folder': f"{month:02d}月"
                })
        
        print(f"📁 分割済みCSVファイル数: {len(csv_files)}個")
        return csv_files
        
    except Exception as e:
        print(f"❌ ファイル取得エラー: {e}")
        return None

def check_existing_folders(service, folder_name, parent_id=None):
    """既存のフォルダーをチェック"""
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        else:
            query += f" and '{SHARED_DRIVE_CONFIG['drive_id']}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id,name)',
            supportsAllDrives=True,
            supportsTeamDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        files = results.get('files', [])
        return files[0]['id'] if files else None
        
    except Exception as e:
        print(f"❌ フォルダー確認エラー: {e}")
        return None

def create_folder_in_shared_drive(service, folder_name, parent_id=None):
    """共有ドライブ内にフォルダーを作成（既存チェック付き）"""
    try:
        # 既存のフォルダーをチェック
        existing_folder_id = check_existing_folders(service, folder_name, parent_id)
        if existing_folder_id:
            print(f"   📁 既存フォルダー使用: {folder_name} (ID: {existing_folder_id})")
            return existing_folder_id
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else [SHARED_DRIVE_CONFIG['drive_id']]
        }
        
        folder = service.files().create(
            body=folder_metadata,
            supportsAllDrives=True,
            supportsTeamDrives=True,
            fields='id,name'
        ).execute()
        
        print(f"   📁 フォルダー作成: {folder_name} (ID: {folder['id']})")
        return folder['id']
        
    except HttpError as error:
        print(f"❌ フォルダー作成エラー ({folder_name}): {error}")
        return None
    except Exception as e:
        print(f"❌ フォルダー作成エラー ({folder_name}): {e}")
        return None

def create_year_month_folders(service, csv_files):
    """年・月フォルダーを作成"""
    try:
        folder_ids = {}
        
        # 年フォルダーを作成
        years = sorted(set(file_info['year'] for file_info in csv_files))
        
        for year in years:
            year_folder_name = f"{year}年"
            year_folder_id = create_folder_in_shared_drive(service, year_folder_name)
            
            if year_folder_id:
                folder_ids[year] = {}
                
                # 月フォルダーを作成
                months = sorted(set(file_info['month'] for file_info in csv_files if file_info['year'] == year))
                
                for month in months:
                    month_folder_name = f"{month:02d}月"
                    month_folder_id = create_folder_in_shared_drive(service, month_folder_name, year_folder_id)
                    
                    if month_folder_id:
                        folder_ids[year][month] = month_folder_id
        
        return folder_ids
        
    except Exception as e:
        print(f"❌ フォルダー構造作成エラー: {e}")
        return None

def upload_file_to_shared_drive(service, file_path, folder_id, max_retries=3):
    """ファイルを共有ドライブにアップロード（リトライ機能付き）"""
    for attempt in range(max_retries):
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                supportsTeamDrives=True,
                fields='id,name,size'
            ).execute()
            
            print(f"   ✅ アップロード成功: {file['name']} (ID: {file['id']})")
            return True
            
        except HttpError as error:
            if attempt < max_retries - 1:
                print(f"   ⚠️ アップロードエラー ({os.path.basename(file_path)}): {error} - リトライ中... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(2)  # 2秒待機
            else:
                print(f"❌ アップロードエラー ({os.path.basename(file_path)}): {error} - 最大リトライ回数に達しました")
                return False
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   ⚠️ 予期しないエラー ({os.path.basename(file_path)}): {e} - リトライ中... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(2)  # 2秒待機
            else:
                print(f"❌ 予期しないエラー ({os.path.basename(file_path)}): {e} - 最大リトライ回数に達しました")
                return False
    
    return False

def upload_split_data(service, csv_files, folder_ids):
    """分割済みデータをアップロード"""
    try:
        success_count = 0
        
        for file_info in csv_files:
            year = file_info['year']
            month = file_info['month']
            file_path = file_info['file_path']
            filename = file_info['filename']
            
            # 対応するフォルダーIDを取得
            if year in folder_ids and month in folder_ids[year]:
                folder_id = folder_ids[year][month]
                
                # ファイルをアップロード
                if upload_file_to_shared_drive(service, file_path, folder_id):
                    success_count += 1
                    print(f"   📊 {filename} → {year}年/{month:02d}月/")
            else:
                print(f"❌ フォルダーが見つかりません: {year}年{month:02d}月")
        
        return success_count
        
    except Exception as e:
        print(f"❌ アップロード処理エラー: {e}")
        return 0

def main():
    """メイン処理"""
    print("🚀 既存の分割済み売り上げデータを共有ドライブにアップロード（修正版）")
    print("="*70)
    print(f"📂 共有ドライブ: {SHARED_DRIVE_CONFIG['drive_name']}")
    print(f"🆔 共有ドライブID: {SHARED_DRIVE_CONFIG['drive_id']}")
    print(f"👤 サービスアカウント: {SHARED_DRIVE_CONFIG['service_account_email']}")
    print(f"📁 スクリプトディレクトリ: {Path(__file__).parent}")
    print("="*70)

    # 1. サービスアカウント認証
    print("\n1️⃣ サービスアカウント認証中...")
    service = authenticate_service_account()
    if not service:
        return

    # 2. 既存の分割済みCSVファイルを取得
    print("\n2️⃣ 既存の分割済みCSVファイルを確認中...")
    csv_files = get_existing_split_files()
    if not csv_files:
        print("❌ 分割済みCSVファイルが見つかりません")
        return

    # 3. 年・月フォルダーを作成
    print("\n3️⃣ 共有ドライブに年・月フォルダーを作成中...")
    folder_ids = create_year_month_folders(service, csv_files)

    if not folder_ids:
        print("❌ フォルダー作成に失敗しました")
        return

    # 4. ファイルをアップロード
    print("\n4️⃣ 分割済み売り上げデータをアップロード中...")
    success_count = upload_split_data(service, csv_files, folder_ids)

    # 5. 結果表示
    print("\n" + "="*70)
    print("🎉 処理が完了しました！")
    print("="*70)
    print(f"📊 処理件数: {len(csv_files)}ファイル")
    print(f"✅ アップロード成功: {success_count}ファイル")
    print(f"❌ アップロード失敗: {len(csv_files) - success_count}ファイル")
    print(f"📁 アップロード先: 共有ドライブ '{SHARED_DRIVE_CONFIG['drive_name']}'")
    print(f"🔗 アクセスURL: https://drive.google.com/drive/folders/{SHARED_DRIVE_CONFIG['drive_id']}")
    print("="*70)

    if success_count > 0:
        print("\n💡 アップロードされたファイルは以下の構造で保存されています:")
        print(f"   共有ドライブ '{SHARED_DRIVE_CONFIG['drive_name']}'/")
        
        years = sorted(set(file_info['year'] for file_info in csv_files))
        for year in years:
            print(f"   ├── {year}年/")
            months = sorted(set(file_info['month'] for file_info in csv_files if file_info['year'] == year))
            for month in months:
                print(f"   │   └── {month:02d}月/")
                month_files = [f for f in csv_files if f['year'] == year and f['month'] == month]
                for file_info in month_files:
                    print(f"   │       └── {file_info['filename']}")

if __name__ == "__main__":
    main()