#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Googleドライブへのファイルアップロード使用例
"""

from google_drive_upload import authenticate_service_account, upload_file, upload_file_to_folder

def main():
    """
    アップロード例
    """
    # サービスアカウントのJSONファイルパス
    credentials_file = "disco-vista-466212-a2-611d98d41f0c.json"
    
    print("🚀 GoogleドライブAPIに接続中...")
    
    # サービスアカウントで認証
    service = authenticate_service_account(credentials_file)
    if not service:
        return
    
    print("\n" + "="*60)
    print("📤 ファイルアップロード例")
    print("="*60)
    
    # 例1: ルートにアップロード
    print("\n1️⃣ ルートにアップロード:")
    # テストファイルを作成
    test_content = "これはテストファイルです。\nGoogleドライブAPIでアップロードされました。"
    with open("test_upload.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # ルートにアップロード
    result = upload_file(service, "test_upload.txt")
    
    if result:
        print("✅ ルートへのアップロードが成功しました！")
    else:
        print("❌ ルートへのアップロードが失敗しました")
    
    # 例2: 指定したフォルダーにアップロード
    print("\n2️⃣ 指定したフォルダーにアップロード:")
    # 別のテストファイルを作成
    test_content2 = "これはフォルダー内のテストファイルです。\n指定したフォルダーにアップロードされました。"
    with open("test_folder_upload.txt", "w", encoding="utf-8") as f:
        f.write(test_content2)
    
    # 指定したフォルダーにアップロード
    result2 = upload_file_to_folder(service, "test_folder_upload.txt", "GoogleドライブAPI連携用")
    
    if result2:
        print("✅ フォルダーへのアップロードが成功しました！")
    else:
        print("❌ フォルダーへのアップロードが失敗しました")
    
    # 例3: 新しいファイル名でアップロード
    print("\n3️⃣ 新しいファイル名でアップロード:")
    test_content3 = "これは新しい名前でアップロードされたファイルです。"
    with open("original_name.txt", "w", encoding="utf-8") as f:
        f.write(test_content3)
    
    # 新しいファイル名でアップロード
    result3 = upload_file_to_folder(
        service, 
        "original_name.txt", 
        "GoogleドライブAPI連携用", 
        "新しい名前_アップロード済み.txt"
    )
    
    if result3:
        print("✅ 新しい名前でのアップロードが成功しました！")
    else:
        print("❌ 新しい名前でのアップロードが失敗しました")
    
    print("\n" + "="*60)
    print("🎉 アップロード例が完了しました！")
    print("="*60)

if __name__ == "__main__":
    main() 