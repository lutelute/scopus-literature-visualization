#!/usr/bin/env python3
"""
Windows環境でのUnicodeエラー修正スクリプト
全ての.pyファイルからUnicode絵文字を削除し、ASCII互換文字に置換する
"""

import os
import re
import glob

# Unicode文字の置換マップ
UNICODE_REPLACEMENTS = {
    # 絵文字 → ASCII
    '[OK]': '[OK]',
    '[NG]': '[NG]',
    '[WARN]': '[WARN]',
    '[WARN]': '[WARN]',
    '[SETUP]': '[SETUP]',
    '[PKG]': '[PKG]',
    '[HINT]': '[HINT]',
    '[GOOD]': '[GOOD]',
    '[SYS]': '[SYS]',
    '[DIR]': '[DIR]',
    '[FILE]': '[FILE]',
    '[INFO]': '[INFO]',
    '[DATA]': '[DATA]',
    '[CHART]': '[CHART]',
    '[DONE]': '[DONE]',
    '[TARGET]': '[TARGET]',
    '[TEST]': '[TEST]',
    '[START]': '[START]',
    '[LINK]': '[LINK]',
    '[WAIT]': '[WAIT]',
    '[PROC]': '[PROC]',
}

def fix_unicode_in_file(file_path):
    """単一ファイルのUnicode文字を修正"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Unicode文字を置換
        for unicode_char, replacement in UNICODE_REPLACEMENTS.items():
            content = content.replace(unicode_char, replacement)
        
        # 変更があった場合のみファイルを更新
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """メイン処理"""
    print("Windows Unicode エラー修正スクリプト")
    print("=" * 50)
    
    # すべての.pyファイルを検索
    py_files = []
    for root, dirs, files in os.walk('.'):
        # .venv, .git, __pycache__ などのディレクトリを除外
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    print(f"検索対象: {len(py_files)}個のPythonファイル")
    
    # 各ファイルを処理
    fixed_count = 0
    for file_path in py_files:
        if fix_unicode_in_file(file_path):
            fixed_count += 1
    
    print(f"\n修正完了: {fixed_count}/{len(py_files)}個のファイルを修正")
    
    if fixed_count > 0:
        print("\n修正されたファイル一覧:")
        print("- Windows CI環境でのUnicodeEncodeErrorが解決されました")
        print("- 絵文字がASCII互換文字に置換されました")
    else:
        print("\n修正対象のファイルはありませんでした")

if __name__ == "__main__":
    main()