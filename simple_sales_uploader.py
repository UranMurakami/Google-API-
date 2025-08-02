#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
売り上げデータを年・月ごとに分割してGoogleドライブにアップロードするスクリプト（簡易版）
"""

import pandas as pd
import os
import csv
from datetime import datetime
from google_drive_oauth_upload import authenticate_oauth, upload_file_to_folder, get_folder_id_by_name

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

def upload_to_google_drive(service, csv_files, parent_folder_name):
    """
    CSVファイルをGoogleドライブにアップロードする
    
    Args:
        service: 認証されたDrive APIサービスオブジェクト
        csv_files (list): アップロードするCSVファイルのリスト
        parent_folder_name (str): 親フォルダー名
    
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
                
                # フォルダー名を作成
                year_folder_name = f"{year}年"
                month_folder_name = f"{month}月"
                
                # 年フォルダーにアップロード
                result = upload_file_to_folder(service, csv_file, year_folder_name, f"{month_folder_name}_売上データ.csv")
                
                if result:
                    success_count += 1
                    print(f"   ✅ {csv_file} を {year_folder_name}/{month_folder_name} にアップロードしました")
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
    parent_folder_name = "GoogleドライブAPI連携用"
    
    print("🚀 売り上げデータ分割・アップロード処理を開始します...")
    print("="*60)
    
    # 1. GoogleドライブAPIに接続
    print("\n1️⃣ GoogleドライブAPIに接続中...")
    service = authenticate_oauth()
    if not service:
        print("❌ GoogleドライブAPIへの接続に失敗しました")
        return
    
    # 2. 売り上げデータを読み込んで分割
    print("\n2️⃣ 売り上げデータを読み込んで分割中...")
    split_data = read_and_split_sales_data(csv_file)
    if split_data is None:
        print("❌ データの読み込み・分割に失敗しました")
        return
    
    # 3. 月ごとのCSVファイルを作成
    print("\n3️⃣ 月ごとのCSVファイルを作成中...")
    csv_files = create_monthly_csv_files(split_data)
    if not csv_files:
        print("❌ CSVファイルの作成に失敗しました")
        return
    
    # 4. Googleドライブにアップロード
    print("\n4️⃣ Googleドライブにアップロード中...")
    success_count = upload_to_google_drive(service, csv_files, parent_folder_name)
    
    # 5. 一時ファイルを削除
    print("\n5️⃣ 一時ファイルを削除中...")
    cleanup_temp_files(csv_files)
    
    # 結果表示
    print("\n" + "="*60)
    print("🎉 処理が完了しました！")
    print("="*60)
    print(f"📊 処理件数: {len(csv_files)}ファイル")
    print(f"✅ アップロード成功: {success_count}ファイル")
    print(f"❌ アップロード失敗: {len(csv_files) - success_count}ファイル")
    print(f"📁 アップロード先: {parent_folder_name}")
    print("="*60)
    
    if success_count > 0:
        print("\n💡 アップロードされたファイルは以下の構造で保存されています:")
        print("   GoogleドライブAPI連携用/")
        for year in sorted(split_data.keys()):
            print(f"   ├── {year}年/")
            for month in sorted(split_data[year].keys()):
                month_str = f"{month:02d}"
                print(f"   │   └── {month_str}月_売上データ.csv")

if __name__ == "__main__":
    main() 