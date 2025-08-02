@echo off
chcp 65001 >nul
echo ========================================
echo 共有ドライブ状況確認
echo ========================================
echo.
echo 現在のディレクトリ: %CD%
echo.
echo Pythonスクリプトを実行中...
python "check_shared_drive_status.py"
echo.
echo 実行完了
pause 