#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール設定.py - メール完了通知設定専用ツール
"""

import sys
import os

# utilsディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from email_notification import main
    main()
except ImportError as e:
    print("[NG] メール通知機能のインポートに失敗しました")
    print(f"エラー: {e}")
    print("📋 utils/email_notification.py が存在することを確認してください")
except Exception as e:
    print(f"[NG] 予期しないエラー: {e}")