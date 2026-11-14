"""
Persistence and database management for ArchDebt-Lens.
Supports JSON file storage and SQLite relational storage.
"""

import json
import sqlite3
from typing import Dict, List, Optional
from archdebt_lens.models.schemas import (
    ATDItem,
    LifecycleTrace,
)


class DataStore:
    """Manages storage and retrieval of ATD items and metrics."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or ":memory:"
        self._items: Dict[str, ATDItem] = {}
        self._traces: Dict[str, LifecycleTrace] = {}
        self._init_db()

    def _init_db(self):
        """Initializes SQLite schema if using a persistent database."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS atd_items (
                id TEXT PRIMARY KEY,
                project TEXT,
                debt_type TEXT,
                source TEXT,
                summary TEXT,
                description TEXT,
                payment_commit TEXT,
                intro_commit TEXT,
                is_validated INTEGER
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS file_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                atd_id TEXT,
                file_path TEXT,
                commit_hash TEXT,
                stage TEXT,
                fan_in INTEGER,
                fan_out INTEGER,
                sloc INTEGER,
                cyclomatic_complexity REAL,
                modification_count INTEGER,
                fan_in_per_sloc REAL,
                fan_out_per_sloc REAL
            )
        """)
        conn.commit()
        conn.close()

    def add_item(self, item: ATDItem):
        self._items[item.id] = item
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO atd_items
            (id, project, debt_type, source, summary, description, payment_commit, intro_commit, is_validated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.id,
            item.project,
            item.debt_type.value,
            item.source.value,
            item.summary,
            item.description,
            item.payment_commit,
            item.intro_commit,
            1 if item.is_validated else 0
        ))
        conn.commit()
        conn.close()

    def get_item(self, atd_id: str) -> Optional[ATDItem]:
        return self._items.get(atd_id)

    def list_items(self) -> List[ATDItem]:
        return list(self._items.values())

    def save_trace(self, trace: LifecycleTrace):
        self._traces[trace.atd_id] = trace
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        insert_sql = """
            INSERT INTO file_metrics
            (atd_id, file_path, commit_hash, stage, fan_in, fan_out, sloc,
             cyclomatic_complexity, modification_count, fan_in_per_sloc, fan_out_per_sloc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Insert intro metrics
        for path, metric in trace.metrics_intro.items():
            cur.execute(insert_sql, (
                trace.atd_id, path, metric.commit_hash, metric.stage.value,
                metric.fan_in, metric.fan_out, metric.sloc, metric.cyclomatic_complexity,
                metric.modification_count, metric.fan_in_per_sloc, metric.fan_out_per_sloc
            ))

        # Insert payment metrics
        for path, metric in trace.metrics_payment.items():
            cur.execute(insert_sql, (
                trace.atd_id, path, metric.commit_hash, metric.stage.value,
                metric.fan_in, metric.fan_out, metric.sloc, metric.cyclomatic_complexity,
                metric.modification_count, metric.fan_in_per_sloc, metric.fan_out_per_sloc
            ))

        conn.commit()
        conn.close()

    def get_trace(self, atd_id: str) -> Optional[LifecycleTrace]:
        return self._traces.get(atd_id)

    def export_json(self, path: str):
        data = {
            "items": [item.model_dump() for item in self._items.values()],
            "traces": [trace.model_dump() for trace in self._traces.values()]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def import_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item_dict in data.get("items", []):
                item = ATDItem(**item_dict)
                self.add_item(item)
            for trace_dict in data.get("traces", []):
                trace = LifecycleTrace(**trace_dict)
                self.save_trace(trace)
