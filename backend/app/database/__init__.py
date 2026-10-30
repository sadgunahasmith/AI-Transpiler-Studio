"""
Database module entry point.
"""
from .db import init_db, save_history_record, get_history_records, clear_history

__all__ = ["init_db", "save_history_record", "get_history_records", "clear_history"]
