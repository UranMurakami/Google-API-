#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
売り上げデータを年・月ごとに分割してGoogleドライブにアップロードするスクリプト（サービスアカウント版）
"""

import pandas as pd
import os
import csv
from datetime import datetime
from google_drive_shared_upload import authenticate_service_account, upload_file_to_shared_drive

def read_and_split_sales_data(csv_file):
    """
    売り上げデータを読み込んで年・月ごとに分割する
    
    Args:
        csv_file (str): CSVファイルのパス
    
    Returns:
        dict: 年・月ごとに分割されたデータ
    """
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # 日付列をdatetime型に変換
        df['日付'] = pd.to_datetime(df['日付'])
        
        print(f"✅ 売り上げデータを読み込みました: {len(df)}件")
        
        # 年・月でグループ化
        grouped = df.groupby([df['日付'].dt.year, df['日付'].dt.month])
        
        split_data = {}
        
        for (year, month), group in grouped:
            if year not in split_data:
                split_data[year] = {}
            
            split_data[year][month] = group
        
        print(f"✅ データを {len(split_data)}年分に分割しました")
        
        # 分割結果を表示
        for year in sorted(split_data.keys()):
            months = sorted(split_data[year].keys())
            print(f"   {year}年: {len(months)}ヶ月分 ({', '.join(map(str, months))}月)")
        
        return split_data
        
    except Exception as e:
        print(f"❌ データ読み込み・分割エラー: {e}")
        return None

def create_monthly_csv_files(split_data):
    """
    月ごとのCSVファイルを作成する
    
    Args:
        split_data (dict): 年・月ごとに分割されたデータ
    
    Returns:
        list: 作成されたCSVファイルのパスリスト
    """
    try:
        created_files = []
        
        for year in sorted(split_data.keys()):
            for month in sorted(split_data[year].keys()):
                # 月を2桁で表示
                month_str = f"{month:02d}"
                filename = f"sales_data_{year}_{month_str}.csv"
                
                # CSVファイルとして保存
                split_data[year][month].to_csv(filename, index=False, encoding='utf-8')
                created_files.append(filename)
                
                print(f"   📄 {filename} を作成しました ({len(split_data[year][month])}件)")
        
        print(f"✅ {len(created_files)}個のCSVファイルを作成しました")
        return created_files
        
    except Exception as e:
        print(f"❌ CSVファイル作成エラー: {e}")
        return []

def upload_to_shared_drive(service, csv_files, drive_id):
    """
    CSVファイルを共有ドライブにアップロードする
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        csv_files (list): アップロードするCSVファイルのリスト
        drive_id (str): 共有ドライブID
    
    Returns:
        int: アップロード成功件数
    """
    try:
        success_count = 0
        
        for csv_file in csv_files:
            # ファイル名から年・月を抽出
            filename = csv_file.replace('.csv', '')
            parts = filename.split('_')
            
            if len(parts) >= 4:
                year = parts[2]
                month = parts[3]
                
                # 新しいファイル名を作成
                new_filename = f"{year}年{month}月_売上データ.csv"
                
                # 共有ドライブにアップロード
                result = upload_file_to_shared_drive(service, csv_file, drive_id, new_filename=new_filename)
                
                if result:
                    success_count += 1
                    print(f"   ✅ {csv_file} を {new_filename} としてアップロードしました")
                else:
                    print(f"   ❌ {csv_file} のアップロードに失敗しました")
        
        return success_count
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return 0

def cleanup_temp_files(csv_files):
    """
    一時ファイルを削除する
    
    Args:
        csv_files (list): 削除するファイルのリスト
    """
    try:
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                os.remove(csv_file)
                print(f"   🧹 {csv_file} を削除しました")
        
        print("✅ 一時ファイルの削除が完了しました")
        
    except Exception as e:
        print(f"⚠️ 一時ファイル削除エラー: {e}")

def main():
    """
    メイン関数
    """
    # 設定
    csv_file = "sales_data.csv"
    credentials_file = "disco-vista-466212-a2-611d98d41f0c.json"
    
    print("🚀 売り上げデータ分割・アップロード処理を開始します...")
    print("="*60)
    
    # 1. GoogleドライブAPIに接続
    print("\n1️⃣ GoogleドライブAPIに接続中...")
    service = authenticate_service_account(credentials_file)
    if not service:
        print("❌ GoogleドライブAPIへの接続に失敗しました")
        return
    
    # 2. 共有ドライブを確認
    print("\n2️⃣ 共有ドライブを確認中...")
    from google_drive_shared_upload import list_shared_drives
    shared_drives = list_shared_drives(service)
    
    if not shared_drives:
        print("❌ 共有ドライブが見つかりません")
        print("💡 共有ドライブを作成するか、既存の共有ドライブにサービスアカウントを追加してください")
        return
    
    # 最初の共有ドライブを使用
    drive_id = shared_drives[0]['id']
    drive_name = shared_drives[0]['name']
    print(f"📂 共有ドライブ '{drive_name}' を使用します (ID: {drive_id})")
    
    # 3. 売り上げデータを読み込んで分割
    print("\n3️⃣ 売り上げデータを読み込んで分割中...")
    split_data = read_and_split_sales_data(csv_file)
    if split_data is None:
        print("❌ データの読み込み・分割に失敗しました")
        return
    
    # 4. 月ごとのCSVファイルを作成
    print("\n4️⃣ 月ごとのCSVファイルを作成中...")
    csv_files = create_monthly_csv_files(split_data)
    if not csv_files:
        print("❌ CSVファイルの作成に失敗しました")
        return
    
    # 5. 共有ドライブにアップロード
    print("\n5️⃣ 共有ドライブにアップロード中...")
    success_count = upload_to_shared_drive(service, csv_files, drive_id)
    
    # 6. 一時ファイルを削除
    print("\n6️⃣ 一時ファイルを削除中...")
    cleanup_temp_files(csv_files)
    
    # 結果表示
    print("\n" + "="*60)
    print("🎉 処理が完了しました！")
    print("="*60)
    print(f"📊 処理件数: {len(csv_files)}ファイル")
    print(f"✅ アップロード成功: {success_count}ファイル")
    print(f"❌ アップロード失敗: {len(csv_files) - success_count}ファイル")
    print(f"📁 アップロード先: 共有ドライブ '{drive_name}'")
    print("="*60)
    
    if success_count > 0:
        print("\n💡 アップロードされたファイルは以下の形式で保存されています:")
        print(f"   共有ドライブ '{drive_name}'/")
        for year in sorted(split_data.keys()):
            for month in sorted(split_data[year].keys()):
                month_str = f"{month:02d}"
                print(f"   ├── {year}年{month_str}月_売上データ.csv")

if __name__ == "__main__":
    main() 