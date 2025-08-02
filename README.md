# GoogleドライブAPI ツール

このプロジェクトは、GoogleドライブAPIを使用してサービスアカウントで認証し、ドライブ内のフォルダーを取得・ファイルをアップロードするPythonツールです。

## 機能

- ✅ サービスアカウントによる認証
- 🔐 OAuth 2.0認証によるファイルアップロード
- 📁 全フォルダーの一覧取得
- 📂 フォルダーの階層構造表示
- 📊 フォルダーの詳細情報表示（作成日時、更新日時、リンクなど）
- 📤 **ファイルのアップロード機能**
  - ルートへのアップロード
  - 指定フォルダーへのアップロード
  - 新しいファイル名でのアップロード

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 認証設定

#### サービスアカウント認証（フォルダー取得用）

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Drive APIを有効化
3. サービスアカウントを作成
4. サービスアカウントキー（JSON）をダウンロード
5. JSONファイルをプロジェクトのルートディレクトリに配置

#### OAuth 2.0認証（ファイルアップロード用）

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Drive APIを有効化
3. OAuth 2.0クライアントIDを作成
4. `credentials.json`をダウンロード
5. ファイルをプロジェクトのルートディレクトリに配置

### 3. 権限の設定

サービスアカウントにアクセスさせたいGoogleドライブのフォルダーに、サービスアカウントのメールアドレスを共有設定で追加してください。

## 使用方法

### フォルダー取得（サービスアカウント）

```bash
python google_drive_folders.py
```

### ファイルアップロード（OAuth 2.0）

```bash
# OAuth 2.0認証でアップロード
python google_drive_oauth_upload.py
```

### 共有ドライブ（サービスアカウント）

```bash
# 共有ドライブへのアップロード
python google_drive_shared_upload.py
```

## 認証方法の違い

| 機能 | 認証方法 | 用途 | 制限 |
|------|----------|------|------|
| フォルダー取得 | サービスアカウント | 読み取り専用 | 個人ドライブへの書き込み不可 |
| ファイルアップロード | OAuth 2.0 | 読み書き | 個人ドライブに書き込み可能 |
| 共有ドライブ | サービスアカウント | 読み書き | 共有ドライブのみ |

## アップロード機能の詳細

### OAuth 2.0認証での使用方法

```python
from google_drive_oauth_upload import authenticate_oauth, upload_file, upload_file_to_folder

# 認証
service = authenticate_oauth()

# ルートにアップロード
upload_file(service, "local_file.txt")

# 指定したフォルダーにアップロード
upload_file_to_folder(service, "local_file.txt", "フォルダー名")

# 新しいファイル名でアップロード
upload_file_to_folder(service, "local_file.txt", "フォルダー名", "new_name.txt")
```

### サービスアカウントでの使用方法（共有ドライブ）

```python
from google_drive_shared_upload import authenticate_service_account, upload_file_to_shared_drive

# 認証
service = authenticate_service_account("credentials.json")

# 共有ドライブにアップロード
upload_file_to_shared_drive(service, "local_file.txt", "shared_drive_id")
```

### アップロード可能なファイル形式

- テキストファイル (.txt, .md, .py, etc.)
- 画像ファイル (.jpg, .png, .gif, etc.)
- ドキュメント (.pdf, .doc, .docx, etc.)
- その他すべてのファイル形式

## 出力例

### フォルダー取得
```
🚀 GoogleドライブAPIに接続中...
✅ サービスアカウント認証が成功しました

==================================================
1. 全フォルダー一覧を取得
2. フォルダー階層構造を表示
==================================================
📁 1個のフォルダーが見つかりました

================================================================================
📂 Googleドライブのフォルダー一覧
================================================================================

1. フォルダー名: GoogleドライブAPI連携用
   ID: 13ieB-4-1D1sT66mdwd-VWkx-7KfhjD3z
   作成日時: 2025-07-27T12:00:05.357Z
   更新日時: 2025-07-27T12:01:53.234Z
   リンク: https://drive.google.com/drive/folders/13ieB-4-1D1sT66mdwd-VWkx-7KfhjD3z
   親フォルダー: ルート
```

### ファイルアップロード（OAuth 2.0）
```
🚀 GoogleドライブAPIに接続中...
🔐 OAuth 2.0認証を開始します...
💡 ブラウザが開きます。Googleアカウントでログインして権限を許可してください。
✅ OAuth 2.0認証が成功しました

📂 利用可能なフォルダー一覧:
==================================================
1. GoogleドライブAPI連携用 (ID: 13ieB-4-1D1sT66mdwd-VWkx-7KfhjD3z)
==================================================

📁 アップロード情報:
   ファイル名: oauth_test.txt
   ファイルサイズ: 45 bytes
   MIMEタイプ: text/plain
   アップロード先: ルート
🚀 アップロードを開始します...
✅ アップロードが完了しました！
   ファイルID: 1ABC123DEF456GHI789JKL
   ファイル名: oauth_test.txt
   ファイルサイズ: 45 bytes
   作成日時: 2025-07-27T12:30:00.000Z
   リンク: https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view
```

## ファイル構成

- `google_drive_folders.py` - フォルダー取得スクリプト（サービスアカウント）
- `google_drive_oauth_upload.py` - ファイルアップロードスクリプト（OAuth 2.0）
- `google_drive_shared_upload.py` - 共有ドライブアップロードスクリプト（サービスアカウント）
- `upload_example.py` - アップロード使用例
- `create_shared_drive_example.py` - 共有ドライブ作成例
- `requirements.txt` - 依存関係
- `disco-vista-466212-a2-611d98d41f0c.json` - サービスアカウントキー（既存）
- `credentials.json` - OAuth 2.0クライアントID（要作成）

## 注意事項

- サービスアカウントキーファイルは機密情報です。Gitにコミットしないでください
- OAuth 2.0認証では初回実行時にブラウザが開き、権限の許可が必要です
- サービスアカウントは個人ドライブへの書き込みができません（共有ドライブのみ）
- APIの利用制限にご注意ください
- 大きなファイルのアップロードには時間がかかる場合があります

## トラブルシューティング

### 認証エラー
- 認証ファイルのパスが正しいか確認
- JSONファイルが破損していないか確認
- OAuth 2.0認証ではブラウザでの権限許可が必要

### フォルダーが見つからない
- サービスアカウントに適切な権限が付与されているか確認
- フォルダーの共有設定を確認

### アップロードエラー

#### サービスアカウントの場合
- **ストレージクォータエラー**: 個人ドライブへの書き込みはできません。共有ドライブを使用してください
- **共有ドライブ作成エラー**: サービスアカウントには共有ドライブ作成権限がありません

#### OAuth 2.0の場合
- ファイルパスが正しいか確認
- ファイルが存在するか確認
- フォルダー名が正確か確認

### API制限エラー
- Google Cloud ConsoleでAPIの利用制限を確認
- 必要に応じてクォータの増加を申請

### ファイルパスエラー
- 全角スペースを含むパスでは、カレントディレクトリから実行してください
- 例: `python script.py` ではなく、`cd "path" && python script.py` 