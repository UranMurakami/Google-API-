#!/usr/bin/env python3
"""
共有ドライブ設定ファイル
"""

# 共有ドライブの設定
SHARED_DRIVE_CONFIG = {
    'drive_id': '0AJsrfbnalvHzUk9PVA',
    'drive_name': '売り上げデータ管理用共有ドライブ',
    'service_account_email': 'googledrive-api@sodium-replica-467313-u1.iam.gserviceaccount.com',
    'credentials_file': 'sodium-replica-467313-u1-a5e3b290705b.json'
}

# フォルダー構造の設定
FOLDER_STRUCTURE = {
    'root_folder_name': '売り上げデータ管理用共有ドライブ',
    'year_folder_prefix': '年',
    'month_folder_prefix': '月'
}

# ファイル設定
FILE_CONFIG = {
    'csv_source_file': 'sales_data.csv',
    'file_encoding': 'utf-8',
    'date_column': '日付',
    'sales_column': '売上金額'
} 