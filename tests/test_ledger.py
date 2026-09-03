import tempfile
import unittest
from pathlib import Path

from chronicle_app import LedgerStore


class TestLedgerStore(unittest.TestCase):
    def test_records_entry_and_returns_daily_summary(self) -> None:
        # Given: an empty personal time ledger
        with tempfile.TemporaryDirectory() as directory:
            store = LedgerStore(Path(directory) / "chronicle.sqlite3")

            # When: a focused work interval is entered
            entry = store.create_entry(
                title="论文阅读",
                started_at="2026-08-02T09:00:00+08:00",
                ended_at="2026-08-02T10:30:00+08:00",
                category="研究",
                bs_mode="B",
                energy=4,
                note="读完方法部分",
            )

            # Then: the stored entry and daily ledger expose its duration
            summary = store.daily_summary("2026-08-02")
            self.assertEqual(entry["minutes"], 90)
            self.assertEqual(summary["total_minutes"], 90)
            self.assertEqual(summary["focus_minutes"], 90)
            self.assertEqual(summary["entries"][0]["title"], "论文阅读")

    def test_rejects_end_before_start(self) -> None:
        # Given: an available ledger store
        with tempfile.TemporaryDirectory() as directory:
            store = LedgerStore(Path(directory) / "chronicle.sqlite3")

            # When: an interval ends before it begins
            with self.assertRaises(ValueError):
                store.create_entry(
                    title="无效记录",
                    started_at="2026-08-02T11:00:00+08:00",
                    ended_at="2026-08-02T10:00:00+08:00",
                    category="其他",
                    bs_mode="S",
                    energy=2,
                    note="",
                )

            # Then: the boundary rejects the invalid entry

