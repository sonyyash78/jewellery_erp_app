import unittest
import json
import sqlite3
from decimal import Decimal
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))

from app.services.calculation_service import CalculationService

class TestCompany1GoldenMaster(unittest.TestCase):
    def setUp(self):
        self.fixtures_path = BASE_DIR / 'tests' / 'baselines' / 'calculation_fixtures.json'
        self.counts_path = BASE_DIR / 'tests' / 'baselines' / 'table_counts_baseline.json'
        with open(self.fixtures_path, 'r', encoding='utf-8') as f:
            self.fixtures = json.load(f)
        with open(self.counts_path, 'r', encoding='utf-8') as f:
            self.counts = json.load(f)

    def test_gold_fixtures(self):
        for case in self.fixtures['gold_fixtures']:
            inp = case['input']
            expected = case['expected_output']
            out = CalculationService.calculate_selling(
                net_weight=Decimal(inp['net_weight']),
                metal_rate=Decimal(inp['metal_rate']),
                touch_purity=Decimal(inp['touch_purity']),
                wastage=Decimal(inp['wastage']),
                making_rate=Decimal(inp['making_rate']),
                making_type=inp['making_type'],
                hallmark=Decimal(inp['hallmark']),
                other=Decimal(inp['other']),
                discount=Decimal(inp['discount']),
                gst_rate=Decimal(inp['gst_rate'])
            )
            for k, exp_val in expected.items():
                self.assertEqual(str(out[k]), exp_val, f"Gold fixture failure on {inp['name']} key {k}")

    def test_silver_fixtures(self):
        for case in self.fixtures['silver_fixtures']:
            inp = case['input']
            expected = case['expected_output']
            out = CalculationService.calculate_selling(
                net_weight=Decimal(inp['net_weight']),
                metal_rate=Decimal(inp['metal_rate']),
                touch_purity=Decimal(inp['touch_purity']),
                wastage=Decimal(inp['wastage']),
                making_rate=Decimal(inp['making_rate']),
                making_type=inp['making_type'],
                hallmark=Decimal(inp['hallmark']),
                other=Decimal(inp['other']),
                discount=Decimal(inp['discount']),
                gst_rate=Decimal(inp['gst_rate'])
            )
            for k, exp_val in expected.items():
                self.assertEqual(str(out[k]), exp_val, f"Silver fixture failure on {inp['name']} key {k}")

    def test_table_row_counts_non_destructive(self):
        db_path = Path(r'C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for table, expected_cnt in self.counts.items():
            cur.execute(f'SELECT count(*) FROM {table}')
            cnt = cur.fetchone()[0]
            self.assertGreaterEqual(cnt, expected_cnt, f'Table {table} lost rows! Current: {cnt}, Expected >= {expected_cnt}')
        conn.close()

if __name__ == '__main__':
    unittest.main()
