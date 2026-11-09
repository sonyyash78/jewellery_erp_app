"""
Diamond Module & Multi-Company Isolation Tests
==============================================
Validates:
1. Diamond calculations in grams (gm) and rate per gram (Rs/gm)
2. Backward compatibility with carat calculations (1 gm = 5 ct)
3. Company 1 (Non-GST / Saideep) and Company 2 (GST / Pride Gold) isolation
"""
import unittest
from decimal import Decimal
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))

from app.db.database import SessionLocal
from app.services.calculation_service import CalculationService
from app.services.sequence_service import SequenceService


class TestDiamondModule(unittest.TestCase):

    def test_diamond_weight_in_grams(self):
        """Test diamond calculation using weight in grams (gm)."""
        res = CalculationService.calculate_diamond(
            weight_gm=Decimal("2.500"),
            rate_per_gm=Decimal("30000.00"),
            making_charges=Decimal("1500.00"),
            other_charges=Decimal("500.00"),
            discount=Decimal("2000.00"),
            gst_rate=Decimal("1.5"),
            is_same_state=True
        )
        # Subtotal = 2.500 * 30000 = 75000.00
        self.assertEqual(res["subtotal"], Decimal("75000.00"))
        # Taxable = 75000 + 1500 + 500 - 2000 = 75000.00
        self.assertEqual(res["taxable_amount"], Decimal("75000.00"))
        # 1.5% GST Intra-State -> CGST 0.75% = 562.50, SGST 0.75% = 562.50, Total Tax = 1125.00
        self.assertEqual(res["total_tax"], Decimal("1125.00"))
        self.assertEqual(res["grand_total"], Decimal("76125.00"))
        # Carat equivalent: 2.5 gm * 5 = 12.5000 ct
        self.assertEqual(res["carat_weight"], Decimal("12.5000"))

    def test_diamond_carat_backward_compatibility(self):
        """Test legacy carat-based calculation continues to work unchanged."""
        res = CalculationService.calculate_diamond(
            carat_weight=Decimal("1.250"),
            rate_per_carat=Decimal("40000.00"),
            making_charges=Decimal("0.00"),
            discount=Decimal("0.00"),
            gst_rate=Decimal("0.25"),
            is_same_state=True
        )
        # Subtotal = 1.25 * 40000 = 50000.00
        self.assertEqual(res["subtotal"], Decimal("50000.00"))
        self.assertEqual(res["taxable_amount"], Decimal("50000.00"))
        # 0.25% GST -> 125.00 total tax
        self.assertEqual(res["total_tax"], Decimal("125.00"))
        self.assertEqual(res["grand_total"], Decimal("50125.00"))


class TestCompanyDataIsolation(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_invoice_format_isolation(self):
        """Company 1 uses legacy format, Company 2 uses PG/S/SEQ/FY format."""
        seq_c1 = SequenceService.generate_document_number(
            self.db, company_id=1, doc_type="INVOICE"
        )
        self.assertTrue(seq_c1.startswith("INV-"))

        seq_c2 = SequenceService.generate_document_number(
            self.db, company_id=2, doc_type="INVOICE"
        )
        self.assertTrue(seq_c2.startswith(("PG/S/", "SJ/S/")))
        self.assertLessEqual(len(seq_c2), 16)
        parts = seq_c2.split("/")
        self.assertEqual(len(parts), 4)


if __name__ == '__main__':
    unittest.main()
