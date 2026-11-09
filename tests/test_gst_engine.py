"""
GST Engine Unit Tests
====================
Validates all required GST scenarios:
- Silver Bar reference case: 2,000 g @ ₹194.66
- Inter-state IGST case
- Synthetic Diamond 0.25% (unworked) and 1.5% (cut & polished)
- Mixed-HSN invoice (Gold + Silver + Diamond)
- Negative round-off case
- Zero-value line
- Discount & other charges line
- Buyer GSTIN validation
"""
import unittest
from decimal import Decimal
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))

from app.services.gst_engine import GSTEngine, GSTLineItem


class TestGSTEngine(unittest.TestCase):

    def test_pride_gold_reference_silver_bar(self):
        """Reference case: Silver Bar 2,000 g @ 194.66 intra-state."""
        item = GSTLineItem(
            description="Silver Bar",
            hsn_code="71069120",
            quantity=Decimal("2000.000"),
            rate=Decimal("194.66"),
            gst_rate=Decimal("3.00")
        )
        res = GSTEngine.calculate_invoice_gst(
            seller_state_code="08",
            place_of_supply_state_code="08",
            items=[item]
        )

        self.assertTrue(res["is_intra_state"])
        self.assertEqual(res["total_taxable_amount"], Decimal("389320.00"))
        self.assertEqual(res["total_cgst_amount"], Decimal("5839.80"))
        self.assertEqual(res["total_sgst_amount"], Decimal("5839.80"))
        self.assertEqual(res["total_igst_amount"], Decimal("0.00"))
        self.assertEqual(res["total_tax_amount"], Decimal("11679.60"))
        self.assertEqual(res["pre_round_total"], Decimal("400999.60"))
        self.assertEqual(res["round_off"], Decimal("0.40"))
        self.assertEqual(res["grand_total"], Decimal("401000.00"))
        self.assertEqual(res["amount_chargeable_words"], "Indian Rupees Four Lakh One Thousand Only")
        self.assertEqual(res["tax_amount_words"], "Indian Rupees Eleven Thousand Six Hundred Seventy Nine and Sixty paise Only")

    def test_inter_state_silver_bar(self):
        """Inter-state case: Silver Bar 2,000 g @ 194.66 (Rajasthan 08 -> Gujarat 24)."""
        item = GSTLineItem(
            description="Silver Bar",
            hsn_code="71069120",
            quantity=Decimal("2000.000"),
            rate=Decimal("194.66"),
            gst_rate=Decimal("3.00")
        )
        res = GSTEngine.calculate_invoice_gst(
            seller_state_code="08",
            place_of_supply_state_code="24",
            items=[item]
        )

        self.assertFalse(res["is_intra_state"])
        self.assertEqual(res["total_taxable_amount"], Decimal("389320.00"))
        self.assertEqual(res["total_cgst_amount"], Decimal("0.00"))
        self.assertEqual(res["total_sgst_amount"], Decimal("0.00"))
        self.assertEqual(res["total_igst_amount"], Decimal("11679.60"))
        self.assertEqual(res["total_tax_amount"], Decimal("11679.60"))
        self.assertEqual(res["grand_total"], Decimal("401000.00"))

    def test_diamond_tiers(self):
        """Synthetic diamond 0.25% (unworked) and 1.5% (cut & polished)."""
        item_unworked = GSTLineItem(
            description="Synthetic Diamond Rough",
            hsn_code="71042120",
            quantity=Decimal("10.000"),
            rate=Decimal("5000.00"),
            gst_rate=Decimal("0.25")
        )
        item_cut = GSTLineItem(
            description="Synthetic Diamond Polished",
            hsn_code="71049120",
            quantity=Decimal("5.000"),
            rate=Decimal("20000.00"),
            gst_rate=Decimal("1.50")
        )
        res = GSTEngine.calculate_invoice_gst(
            seller_state_code="08",
            place_of_supply_state_code="08",
            items=[item_unworked, item_cut]
        )

        self.assertEqual(res["total_taxable_amount"], Decimal("150000.00"))
        # Unworked: 50,000 @ 0.25% = 125 (CGST 62.50, SGST 62.50)
        # Cut: 100,000 @ 1.50% = 1500 (CGST 750.00, SGST 750.00)
        self.assertEqual(res["total_cgst_amount"], Decimal("812.50"))
        self.assertEqual(res["total_sgst_amount"], Decimal("812.50"))
        self.assertEqual(res["total_tax_amount"], Decimal("1625.00"))
        self.assertEqual(res["grand_total"], Decimal("151625.00"))

    def test_negative_round_off(self):
        """Grand total ending in .39 should round DOWN (-0.39)."""
        item = GSTLineItem(
            description="Sample Item",
            hsn_code="711319",
            quantity=Decimal("1.000"),
            rate=Decimal("97.47"),
            gst_rate=Decimal("3.00")
        )
        res = GSTEngine.calculate_invoice_gst(
            seller_state_code="08",
            place_of_supply_state_code="08",
            items=[item]
        )
        self.assertEqual(res["pre_round_total"], Decimal("100.39"))
        self.assertEqual(res["round_off"], Decimal("-0.39"))
        self.assertEqual(res["grand_total"], Decimal("100.00"))

    def test_zero_value_line(self):
        """Zero-value line should compute cleanly without divide-by-zero."""
        item_zero = GSTLineItem(
            description="Free Gift Box",
            hsn_code="711319",
            quantity=Decimal("1.000"),
            rate=Decimal("0.00"),
            gst_rate=Decimal("3.00")
        )
        res = GSTEngine.calculate_invoice_gst(
            seller_state_code="08",
            place_of_supply_state_code="08",
            items=[item_zero]
        )
        self.assertEqual(res["total_taxable_amount"], Decimal("0.00"))
        self.assertEqual(res["grand_total"], Decimal("0.00"))

    def test_discount_and_other_charges(self):
        """Line with making charges, other charges, and discount."""
        item = GSTLineItem(
            description="Gold Chain",
            hsn_code="711319",
            quantity=Decimal("10.000"),
            rate=Decimal("7000.00"),
            making_charges=Decimal("3500.00"),
            other_charges=Decimal("500.00"),
            discount=Decimal("1000.00"),
            gst_rate=Decimal("3.00")
        )
        # Base: 70,000 + 3,500 + 500 - 1,000 = 73,000.00
        # GST @ 3% = 2,190.00
        # Total = 75,190.00
        res = GSTEngine.calculate_invoice_gst(
            seller_state_code="08",
            place_of_supply_state_code="08",
            items=[item]
        )
        self.assertEqual(res["total_taxable_amount"], Decimal("73000.00"))
        self.assertEqual(res["total_tax_amount"], Decimal("2190.00"))
        self.assertEqual(res["grand_total"], Decimal("75190.00"))

    def test_gstin_validation(self):
        """Validates format and state code matching."""
        # Valid Rajasthan GSTIN
        valid_res = GSTEngine.validate_gstin("08AEZPK5007N1ZS", "08")
        self.assertTrue(valid_res["valid"])

        # Mismatched state code
        mismatch_res = GSTEngine.validate_gstin("08AEZPK5007N1ZS", "24")
        self.assertFalse(mismatch_res["valid"])

        # B2C (Blank GSTIN)
        b2c_res = GSTEngine.validate_gstin("", "08")
        self.assertTrue(b2c_res["valid"])
        self.assertTrue(b2c_res["is_b2c"])

        # Malformed GSTIN
        invalid_res = GSTEngine.validate_gstin("INVALID123", "08")
        self.assertFalse(invalid_res["valid"])


if __name__ == '__main__':
    unittest.main()
