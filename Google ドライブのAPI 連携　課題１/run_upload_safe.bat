@echo off
chcp 65001 >nul
echo ========================================
echo 売り上げデータアップロード実行
echo ========================================
echo.
echo 現在のディレクトリ: %CD%
echo.
echo Pythonスクリプトを実行中...
python "upload_existing_split_data_fixed.py"
echo.
echo 実行完了
pause 