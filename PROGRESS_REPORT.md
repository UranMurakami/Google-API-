# GoogleドライブAPI連携プロジェクト 進捗報告書

## プロジェクト概要
`sales_data.csv`ファイルの売り上げデータをGoogleドライブAPIを使用して年・月ごとに分割し、「GoogleドライブAPI連携用」フォルダー内に年・月フォルダーを作成してアップロードするプロジェクト。

## 完了した作業

### ✅ 1. データ分割処理
- **ファイル**: `sales_data_splitter.py`
- **結果**: 成功
- **詳細**:
  - `sales_data.csv`（75件の売り上げデータ）を読み込み
  - 2023年（38件）と2024年（37件）に分割
  - 各年を12ヶ月分に分割
  - 合計24個のCSVファイルを作成
  - 保存先: `sales_data_split/`ディレクトリ

### ✅ 2. GoogleドライブAPI認証設定
- **ファイル**: `google_drive_folders.py`
- **結果**: 成功
- **詳細**:
  - サービスアカウント認証を実装
  - スコープ: `https://www.googleapis.com/auth/drive`
  - 認証ファイル: `disco-vista-466212-a2-611d98d41f0c.json`

### ✅ 3. フォルダー構造作成
- **ファイル**: `upload_to_existing_folder.py`
- **結果**: 部分的成功
- **詳細**:
  - 「GoogleドライブAPI連携用」フォルダーを特定
  - 2023年・2024年の年フォルダーを作成
  - 各年フォルダー内に01月〜12月の月フォルダーを作成
  - フォルダー作成は成功（24個のフォルダー）

## 発生した問題と対応

### ❌ 問題1: サービスアカウントのストレージ制限
- **エラー**: `Service Accounts do not have storage quota`
- **原因**: サービスアカウントは個人のGoogleドライブに直接アップロードできない
- **対応**: 共有ドライブの使用を試行

### ❌ 問題2: 共有ドライブ作成権限不足
- **エラー**: `The authenticated user cannot create new shared drives`
- **原因**: サービスアカウントは共有ドライブを作成する権限がない
- **対応**: OAuth 2.0認証の実装を試行

### ❌ 問題3: OAuth 2.0認証ファイル不足
- **エラー**: `credentials.jsonファイルが見つかりません`
- **原因**: OAuth 2.0認証用の設定ファイルが未作成
- **対応**: 手動アップロードを提案

## 現在の状況

### 📊 データ処理状況
```
sales_data_split/
├── 2023/
│   ├── 2023年01月_売上データ.csv (3件, ¥350,000)
│   ├── 2023年02月_売上データ.csv (3件, ¥305,000)
│   ├── ...
│   └── 2023年12月_売上データ.csv (5件, ¥2,565,000)
└── 2024/
    ├── 2024年01月_売上データ.csv (3件, ¥1,160,000)
    ├── 2024年02月_売上データ.csv (3件, ¥1,500,000)
    ├── ...
    └── 2024年12月_売上データ.csv (4件, ¥2,405,000)
```

### 📁 Googleドライブフォルダー構造
```
GoogleドライブAPI連携用/
├── 2023年/
│   ├── 01月/
│   ├── 02月/
│   ├── ...
│   └── 12月/
└── 2024年/
    ├── 01月/
    ├── 02月/
    ├── ...
    └── 12月/
```

## 作成されたスクリプト一覧

### 1. 基本認証・フォルダー操作
- `google_drive_folders.py` - サービスアカウント認証とフォルダー一覧取得
- `google_drive_upload.py` - 基本的なファイルアップロード機能
- `google_drive_oauth_upload.py` - OAuth 2.0認証によるアップロード

### 2. 共有ドライブ対応
- `google_drive_shared_upload.py` - 共有ドライブへのアップロード
- `create_shared_drive_example.py` - 共有ドライブ作成例

### 3. 売り上げデータ処理
- `sales_data_splitter.py` - データ分割処理（完了）
- `sales_data_uploader.py` - 統合アップロード処理
- `simple_sales_uploader.py` - 簡易アップロード処理
- `sales_uploader_service_account.py` - サービスアカウント版

### 4. 最新の実装
- `upload_to_existing_folder.py` - 既存フォルダーへのアップロード
- `upload_existing_files.py` - 既存CSVファイルのアップロード
- `upload_to_shared_drive.py` - 共有ドライブへのアップロード
- `upload_with_oauth.py` - OAuth 2.0認証によるアップロード

## 次のステップの選択肢

### 1. OAuth 2.0認証の設定
**必要な作業**:
- Google Cloud ConsoleでOAuth 2.0クライアントIDを作成
- `credentials.json`ファイルをダウンロード
- `upload_with_oauth.py`を実行

**メリット**: 個人ドライブに直接アップロード可能
**デメリット**: 初期設定が複雑

### 2. 手動アップロード
**必要な作業**:
- `sales_data_split`フォルダー内のCSVファイルを手動でアップロード
- 各ファイルを対応する月フォルダーに配置

**メリット**: 設定不要、即座に実行可能
**デメリット**: 手作業が必要

### 3. 共有ドライブの設定
**必要な作業**:
- Google Workspace管理者が共有ドライブを作成
- サービスアカウントにアクセス権を付与
- `upload_to_shared_drive.py`を実行

**メリット**: 自動化可能、権限管理が明確
**デメリット**: 管理者権限が必要

## 推奨事項

**即座の解決**: 手動アップロード
- データ分割とフォルダー構造は既に完了
- 24個のCSVファイルを対応する月フォルダーにドラッグ&ドロップ

**長期的な解決**: OAuth 2.0認証の設定
- 今後の自動化のために設定を完了
- 個人ドライブへの直接アップロードが可能

## 技術的な学び

1. **サービスアカウントの制限**: 個人ドライブへの直接アクセス不可
2. **共有ドライブの権限**: 作成には管理者権限が必要
3. **OAuth 2.0の複雑さ**: 初期設定は複雑だが柔軟性が高い
4. **ファイルパスの問題**: 全角スペースを含むパスの扱い

## 最終更新日
2024年12月27日

## 最新の進展

### ✅ Google Workspaceアカウントの設定
- **日時**: 2024年12月27日
- **内容**: Google Workspaceアカウントが作成され、API連携の準備が整った
- **新しいファイル**:
  - `workspace_setup_guide.md` - Google Workspace設定手順書
  - `test_workspace_connection.py` - 接続テストスクリプト
  - `sales_data_workspace_uploader.py` - Google Workspace用アップローダー

### ✅ Google Cloud Console設定の進捗
- **日時**: 2024年12月27日
- **完了項目**:
  - ✅ 新しいプロジェクトの作成
  - ✅ Google Drive APIの有効化
  - ✅ サービスアカウントの作成
- **残り作業**: サービスアカウントキーのダウンロード

### 🎯 次のステップ
1. **Google Cloud Consoleでの設定**:
   - ✅ 新しいプロジェクトの作成
   - ✅ Google Drive APIの有効化
   - ✅ サービスアカウントの作成
   - 🔄 サービスアカウントキーのダウンロード

2. **共有ドライブの設定**:
   - 共有ドライブの作成
   - サービスアカウントのメンバー追加

3. **テスト実行**:
   ```bash
   python test_workspace_connection.py
   ```

4. **売り上げデータアップロード**:
   ```bash
   python sales_data_workspace_uploader.py
   ```

## ステータス
🟢 **準備完了** - Google Workspaceアカウントが作成され、自動アップロードが可能になりました 