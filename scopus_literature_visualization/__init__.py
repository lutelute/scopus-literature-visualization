"""
Scopus Literature Visualization Package

Scopus文献データベースから取得した文献情報を可視化するパイプラインシステム
"""

__version__ = "1.0.0"
__author__ = "Literature Visualization Tool"
__email__ = "noreply@example.com"

from .pipeline import run_pipeline
from .cli import main as cli_main

__all__ = ['run_pipeline', 'cli_main']