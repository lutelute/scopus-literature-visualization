#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
email_notification.py - メール完了通知機能
オプション機能として、処理完了時にメール通知を送信
"""

import os
import json
import smtplib
import time
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.utils import formatdate
from typing import Dict, Optional, Tuple
import getpass

def メール設定ファイルパス() -> str:
    """メール設定ファイルのパスを取得"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), ".email_config.json")

def メール設定読み込み() -> Optional[Dict]:
    """メール設定を読み込み"""
    config_path = メール設定ファイルパス()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[NG] メール設定読み込みエラー: {e}")
            return None
    return None

def メール設定保存(設定: Dict) -> bool:
    """メール設定を保存"""
    config_path = メール設定ファイルパス()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(設定, f, ensure_ascii=False, indent=2)
        print(f"[OK] メール設定を保存しました: {config_path}")
        return True
    except Exception as e:
        print(f"[NG] メール設定保存エラー: {e}")
        return False

def メール設定削除() -> bool:
    """メール設定を削除"""
    config_path = メール設定ファイルパス()
    try:
        if os.path.exists(config_path):
            os.remove(config_path)
            print("[OK] メール設定を削除しました")
        return True
    except Exception as e:
        print(f"[NG] メール設定削除エラー: {e}")
        return False

def メール設定セットアップ() -> bool:
    """メール設定の対話的セットアップ"""
    print("\n📧 メール完了通知の設定")
    print("=" * 40)
    print("[HINT] Gmail使用を推奨（アプリパスワード必要）")
    print("📋 設定内容は暗号化されずに保存されます（ローカルのみ）")
    
    try:
        # 送信者情報
        print("\n📤 送信者設定:")
        送信者メール = input("送信者メールアドレス: ").strip()
        if not 送信者メール or "@" not in 送信者メール:
            print("[NG] 有効なメールアドレスを入力してください")
            return False
        
        送信者パスワード = getpass.getpass("送信者パスワード（アプリパスワード推奨）: ")
        if not 送信者パスワード:
            print("[NG] パスワードを入力してください")
            return False
        
        # 受信者情報
        print("\n📥 受信者設定:")
        受信者メール = input(f"受信者メールアドレス（空白で送信者と同じ）: ").strip()
        if not 受信者メール:
            受信者メール = 送信者メール
        
        # SMTP設定
        print("\n🌐 SMTP設定:")
        print("1. Gmail (smtp.gmail.com:587)")
        print("2. Outlook (smtp-mail.outlook.com:587)")
        print("3. その他（手動設定）")
        
        smtp選択 = input("選択 (1-3): ").strip()
        
        if smtp選択 == "1":
            smtpサーバー = "smtp.gmail.com"
            smtpポート = 587
        elif smtp選択 == "2":
            smtpサーバー = "smtp-mail.outlook.com"
            smtpポート = 587
        elif smtp選択 == "3":
            smtpサーバー = input("SMTPサーバー: ").strip()
            try:
                smtpポート = int(input("SMTPポート（通常587）: ").strip() or "587")
            except ValueError:
                smtpポート = 587
        else:
            print("[NG] 無効な選択です")
            return False
        
        # 設定保存
        設定 = {
            "送信者": {
                "メール": 送信者メール,
                "パスワード": 送信者パスワード
            },
            "受信者": 受信者メール,
            "smtp": {
                "サーバー": smtpサーバー,
                "ポート": smtpポート
            },
            "設定日時": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 接続テスト
        print("\n[INFO] 接続テスト中...")
        if メール送信テスト(設定):
            if メール設定保存(設定):
                print("\n[DONE] メール設定完了！")
                print("📧 今後の処理完了時にメール通知が送信されます")
                return True
        
        print("[NG] メール設定に失敗しました")
        return False
        
    except KeyboardInterrupt:
        print("\n⏹️  設定がキャンセルされました")
        return False
    except Exception as e:
        print(f"[NG] 設定エラー: {e}")
        return False

def メール送信テスト(設定: Dict) -> bool:
    """メール送信テスト"""
    try:
        件名 = "📧 Scopus文献可視化システム - メール設定テスト"
        本文 = """
こんにちは！

このメールは、Scopus文献可視化システムのメール通知機能のテストメールです。

[OK] メール設定が正常に完了しました
📧 今後の処理完了時に通知メールが送信されます

Scopus文献可視化システム
        """.strip()
        
        return メール送信(設定, 件名, 本文, テストモード=True)
        
    except Exception as e:
        print(f"[NG] テストメール送信エラー: {e}")
        return False

def メール送信(設定: Dict, 件名: str, 本文: str, テストモード: bool = False) -> bool:
    """メール送信実行"""
    try:
        # メール作成
        msg = MimeMultipart()
        msg['From'] = 設定['送信者']['メール']
        msg['To'] = 設定['受信者']
        msg['Subject'] = 件名
        msg['Date'] = formatdate(localtime=True)
        
        # 本文設定
        msg.attach(MimeText(本文, 'plain', 'utf-8'))
        
        # SMTP接続・送信
        smtp = smtplib.SMTP(設定['smtp']['サーバー'], 設定['smtp']['ポート'])
        smtp.starttls()
        smtp.login(設定['送信者']['メール'], 設定['送信者']['パスワード'])
        
        text = msg.as_string()
        smtp.sendmail(設定['送信者']['メール'], 設定['受信者'], text)
        smtp.quit()
        
        if テストモード:
            print("[OK] テストメール送信成功")
        else:
            print("📧 完了通知メールを送信しました")
        return True
        
    except Exception as e:
        if テストモード:
            print(f"[NG] テストメール送信失敗: {e}")
        else:
            print(f"[NG] メール送信失敗: {e}")
        return False

def 処理完了通知送信(成功ステップ: int, 総ステップ: int, 実行時間: float, 
                  生成ファイル数: Dict, pdf取得結果: Optional[Dict] = None) -> bool:
    """処理完了通知メールを送信"""
    設定 = メール設定読み込み()
    if not 設定:
        return False
    
    # メール内容作成
    件名 = f"[DONE] Scopus文献可視化システム - 処理完了通知 ({成功ステップ}/{総ステップ})"
    
    本文 = f"""
[DATA] Scopus文献可視化システム処理完了

実行結果:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CHART] 成功ステップ: {成功ステップ}/{総ステップ}
⏱️  実行時間: {実行時間/60:.1f}分
📅 完了日時: {time.strftime("%Y-%m-%d %H:%M:%S")}

[DIR] 生成ファイル数:
   [FILE] JSONファイル: {生成ファイル数.get('json', 0)}件
   📝 Markdownファイル: {生成ファイル数.get('md', 0)}件
   📋 PDFファイル: {生成ファイル数.get('pdf', 0)}件
"""

    if pdf取得結果:
        本文 += f"""
📥 PDF取得結果:
   [CHART] 新規PDF取得: {pdf取得結果.get('新規', 0)}件
   [DIR] 総PDF数: {pdf取得結果.get('総数', 0)}件
   ⚡ 処理速度: {pdf取得結果.get('速度', 0):.1f} files/sec
"""

    if 成功ステップ == 総ステップ:
        本文 += """
[TARGET] ステータス: 全処理完了
📂 結果確認: md_folder/ でMarkdownファイルを確認してください
"""
    else:
        本文 += """
[WARN]  ステータス: 一部ステップでエラーが発生
📋 詳細: ログを確認してください
"""

    本文 += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scopus文献可視化システム
🤖 自動通知メール
"""

    return メール送信(設定, 件名, 本文.strip())

def メール設定状況確認() -> Tuple[bool, str]:
    """メール設定の状況を確認"""
    設定 = メール設定読み込み()
    if 設定:
        受信者 = 設定.get('受信者', 'Unknown')
        設定日時 = 設定.get('設定日時', 'Unknown')
        return True, f"[OK] 設定済み（受信者: {受信者}、設定日: {設定日時}）"
    else:
        return False, "[NG] 未設定"

def main():
    """メール設定管理のメイン処理"""
    print("📧 メール通知設定管理")
    print("=" * 30)
    
    # 現在の設定状況表示
    設定済み, 状況 = メール設定状況確認()
    print(f"現在の状況: {状況}")
    
    print("\n📋 利用可能な操作:")
    print("1. メール設定セットアップ")
    print("2. 設定状況確認")
    print("3. テストメール送信")
    print("4. 設定削除")
    print("5. 終了")
    
    while True:
        try:
            選択 = input("\n選択 (1-5): ").strip()
            
            if 選択 == "1":
                メール設定セットアップ()
            elif 選択 == "2":
                設定済み, 状況 = メール設定状況確認()
                print(f"[DATA] {状況}")
            elif 選択 == "3":
                設定 = メール設定読み込み()
                if 設定:
                    メール送信テスト(設定)
                else:
                    print("[NG] メール設定がありません。先にセットアップしてください。")
            elif 選択 == "4":
                if 設定済み:
                    確認 = input("設定を削除しますか？ (y/n): ").lower().strip()
                    if 確認 in ['y', 'yes']:
                        メール設定削除()
                else:
                    print("[NG] 削除する設定がありません")
            elif 選択 == "5":
                print("👋 終了します")
                break
            else:
                print("[NG] 無効な選択です")
                
        except KeyboardInterrupt:
            print("\n👋 終了します")
            break

if __name__ == "__main__":
    main()