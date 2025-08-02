#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
売り上げデータを年・月ごとに分割するスクリプト
"""

import pandas as pd
import os
from datetime import datetime

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
            total_sales = sum(len(split_data[year][m]) for m in months)
            total_amount = sum(split_data[year][m]['売上金額'].sum() for m in months)
            print(f"   {year}年: {len(months)}ヶ月分 ({', '.join(map(str, months))}月) - {total_sales}件, ¥{total_amount:,}")
        
        return split_data
        
    except Exception as e:
        print(f"❌ データ読み込み・分割エラー: {e}")
        return None

def create_monthly_csv_files(split_data, output_dir="sales_data_split"):
    """
    月ごとのCSVファイルを作成する
    
    Args:
        split_data (dict): 年・月ごとに分割されたデータ
        output_dir (str): 出力ディレクトリ
    
    Returns:
        list: 作成されたCSVファイルのパスリスト
    """
    try:
        # 出力ディレクトリを作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        created_files = []
        
        for year in sorted(split_data.keys()):
            year_dir = os.path.join(output_dir, str(year))
            if not os.path.exists(year_dir):
                os.makedirs(year_dir)
            
            for month in sorted(split_data[year].keys()):
                # 月を2桁で表示
                month_str = f"{month:02d}"
                filename = f"{year}年{month_str}月_売上データ.csv"
                file_path = os.path.join(year_dir, filename)
                
                # CSVファイルとして保存
                split_data[year][month].to_csv(file_path, index=False, encoding='utf-8')
                created_files.append(file_path)
                
                # 統計情報を表示
                month_data = split_data[year][month]
                total_sales = len(month_data)
                total_amount = month_data['売上金額'].sum()
                avg_amount = month_data['売上金額'].mean()
                
                print(f"   📄 {filename} を作成しました")
                print(f"      📊 件数: {total_sales}件")
                print(f"      💰 売上合計: ¥{total_amount:,}")
                print(f"      📈 平均売上: ¥{avg_amount:,.0f}")
        
        print(f"✅ {len(created_files)}個のCSVファイルを作成しました")
        return created_files
        
    except Exception as e:
        print(f"❌ CSVファイル作成エラー: {e}")
        return []

def display_summary(split_data):
    """
    分割結果のサマリーを表示する
    
    Args:
        split_data (dict): 年・月ごとに分割されたデータ
    """
    print("\n" + "="*60)
    print("📊 売り上げデータ分割サマリー")
    print("="*60)
    
    total_records = 0
    total_sales_amount = 0
    
    for year in sorted(split_data.keys()):
        year_records = 0
        year_amount = 0
        
        print(f"\n📅 {year}年:")
        for month in sorted(split_data[year].keys()):
            month_data = split_data[year][month]
            records = len(month_data)
            amount = month_data['売上金額'].sum()
            
            year_records += records
            year_amount += amount
            total_records += records
            total_sales_amount += amount
            
            month_str = f"{month:02d}"
            print(f"   {month_str}月: {records}件, ¥{amount:,}")
        
        print(f"   📈 {year}年合計: {year_records}件, ¥{year_amount:,}")
    
    print(f"\n🎯 全体合計: {total_records}件, ¥{total_sales_amount:,}")

def main():
    """
    メイン関数
    """
    # 設定
    csv_file = "sales_data.csv"
    output_dir = "sales_data_split"
    
    print("🚀 売り上げデータ分割処理を開始します...")
    print("="*60)
    
    # 1. 売り上げデータを読み込んで分割
    print("\n1️⃣ 売り上げデータを読み込んで分割中...")
    split_data = read_and_split_sales_data(csv_file)
    if split_data is None:
        print("❌ データの読み込み・分割に失敗しました")
        return
    
    # 2. サマリーを表示
    display_summary(split_data)
    
    # 3. 月ごとのCSVファイルを作成
    print(f"\n2️⃣ 月ごとのCSVファイルを作成中... (出力先: {output_dir})")
    csv_files = create_monthly_csv_files(split_data, output_dir)
    if not csv_files:
        print("❌ CSVファイルの作成に失敗しました")
        return
    
    # 結果表示
    print("\n" + "="*60)
    print("🎉 売り上げデータ分割処理が完了しました！")
    print("="*60)
    print(f"📊 処理件数: {len(csv_files)}ファイル")
    print(f"📁 出力先: {output_dir}/")
    print("="*60)
    
    print("\n💡 作成されたファイル構造:")
    print(f"   {output_dir}/")
    for year in sorted(split_data.keys()):
        print(f"   ├── {year}/")
        for month in sorted(split_data[year].keys()):
            month_str = f"{month:02d}"
            print(f"   │   └── {year}年{month_str}月_売上データ.csv")

if __name__ == "__main__":
    main() 