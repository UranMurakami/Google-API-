#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共有ドライブを作成してファイルをアップロードする例
"""

from google_drive_shared_upload import (
    authenticate_service_account, 
    create_shared_drive, 
    upload_file_to_shared_drive,
    list_folders_in_shared_drive
)

def main():
    """
    共有ドライブ作成とアップロード例
    """
    # サービスアカウントのJSONファイルパス
    credentials_file = "disco-vista-466212-a2-611d98d41f0c.json"
    
    print("🚀 GoogleドライブAPIに接続中...")
    
    # サービスアカウントで認証
    service = authenticate_service_account(credentials_file)
    if not service:
        return
    
    print("\n" + "="*60)
    print("📂 共有ドライブ作成とアップロード例")
    print("="*60)
    
    # 1. 新しい共有ドライブを作成
    print("\n1️⃣ 新しい共有ドライブを作成:")
    drive_name = "APIテスト用共有ドライブ"
    shared_drive = create_shared_drive(service, drive_name)
    
    if not shared_drive:
        print("❌ 共有ドライブの作成に失敗しました")
        return
    
    drive_id = shared_drive['id']
    print(f"✅ 共有ドライブが作成されました: {drive_name} (ID: {drive_id})")
    
    # 2. 共有ドライブ内のフォルダー一覧を表示
    print("\n2️⃣ 共有ドライブ内のフォルダーを確認:")
    folders = list_folders_in_shared_drive(service, drive_id)
    
    # 3. テストファイルを作成してアップロード
    print("\n3️⃣ ファイルをアップロード:")
    
    # テストファイルを作成
    test_content = """これは共有ドライブにアップロードされたテストファイルです。

作成日時: 2025年
用途: GoogleドライブAPIテスト
内容: 共有ドライブへのファイルアップロード機能のテスト

このファイルは正常にアップロードされました！
"""
    
    with open("shared_drive_upload_test.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # 共有ドライブにアップロード
    result = upload_file_to_shared_drive(
        service, 
        "shared_drive_upload_test.txt", 
        drive_id,
        new_filename="APIテスト_アップロード成功.txt"
    )
    
    if result:
        print("✅ 共有ドライブへのアップロードが成功しました！")
        print(f"   ファイルID: {result.get('id')}")
        print(f"   リンク: {result.get('webViewLink')}")
    else:
        print("❌ 共有ドライブへのアップロードが失敗しました")
    
    # 4. 複数のファイルをアップロード
    print("\n4️⃣ 複数のファイルをアップロード:")
    
    # 複数のテストファイルを作成
    files_to_create = [
        ("sample1.txt", "サンプルファイル1の内容です。"),
        ("sample2.txt", "サンプルファイル2の内容です。"),
        ("data.csv", "名前,年齢,部署\n田中,25,営業部\n佐藤,30,開発部\n鈴木,28,人事部"),
        ("config.json", '{"app_name": "テストアプリ", "version": "1.0.0", "debug": true}')
    ]
    
    for filename, content in files_to_create:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"\n📁 {filename} をアップロード中...")
        result = upload_file_to_shared_drive(service, filename, drive_id)
        
        if result:
            print(f"✅ {filename} のアップロードが成功しました")
        else:
            print(f"❌ {filename} のアップロードが失敗しました")
    
    print("\n" + "="*60)
    print("🎉 共有ドライブ作成とアップロード例が完了しました！")
    print("="*60)
    print(f"📂 作成された共有ドライブ: {drive_name}")
    print(f"🔗 共有ドライブID: {drive_id}")
    print("💡 共有ドライブはGoogleドライブの管理画面で確認できます")

if __name__ == "__main__":
    main() 