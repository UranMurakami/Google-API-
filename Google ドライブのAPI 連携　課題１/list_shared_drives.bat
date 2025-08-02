@echo off
chcp 65001 >nul
echo ========================================
echo 利用可能な共有ドライブ確認
echo ========================================
echo.
echo 現在のディレクトリ: %CD%
echo.
echo Pythonスクリプトを実行中...
python "list_available_shared_drives.py"
echo.
echo 実行完了
pause 