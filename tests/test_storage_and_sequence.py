"""
Unit Tests for Storage Service & Sequence Service
=================================================
Verifies:
1. Company 1 generates 'INV-YYYYMMDD-XXXX'
2. Company 2 generates 'PG/S/1944/26-27' format (max 16 chars, GST rules)
3. Storage hierarchy directory creation
4. SHA-256 computation and integrity verification
"""
import os
import sys
import pytest
from datetime import datetime

TESTS_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(TESTS_DIR, '..', 'backend')
sys.path.insert(0, BACKEND_DIR)

from app.db.database import SessionLocal
from app.services.sequence_service import SequenceService
from app.services.storage_service import StorageService


class TestSequenceService:

    def setup_method(self):
        self.db = SessionLocal()

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_company_1_legacy_format(self):
        """Company 1 must produce INV-YYYYMMDD-XXXX format."""
        inv_no = SequenceService.generate_document_number(self.db, company_id=1, doc_type="INVOICE")
        assert inv_no.startswith("INV-")
        parts = inv_no.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 4  # XXXX

    def test_company_2_gst_format(self):
        """Company 2 (Pride Gold) must produce PG/S/<SEQ>/<FY> (max 16 chars)."""
        inv_no = SequenceService.generate_document_number(self.db, company_id=2, doc_type="INVOICE")
        assert inv_no.startswith(("PG/S/", "SJ/S/"))
        assert len(inv_no) <= 16
        # Matches reference pattern e.g. PG/S/1944/26-27
        parts = inv_no.split("/")
        assert len(parts) == 4
        assert parts[0] in ["PG", "SJ"]
        assert parts[1] == "S"
        assert parts[2].isdigit()
        assert len(parts[3]) == 5  # e.g. 26-27


class TestStorageService:

    def test_storage_financial_year(self):
        dt = datetime(2026, 11, 7)
        fy = StorageService.get_financial_year(dt, fy_start_month=4)
        assert fy == "26-27"

        dt_jan = datetime(2027, 2, 1)
        fy_jan = StorageService.get_financial_year(dt_jan, fy_start_month=4)
        assert fy_jan == "26-27"

    def test_storage_save_and_sha256_verification(self):
        dummy_pdf = b"%PDF-1.4 Mock invoice content for Company 2 Pride Gold"
        res = StorageService.save_pdf_document(
            company_id=2,
            doc_type="Invoices",
            filename="Sales_PG_S_1944_26-27.pdf",
            pdf_bytes=dummy_pdf,
            financial_year="26-27"
        )
        assert os.path.exists(res["file_path"])
        assert res["sha256_hash"] is not None
        assert len(res["sha256_hash"]) == 64

        # Integrity verification
        is_valid = StorageService.verify_file_integrity(res["file_path"], res["sha256_hash"])
        assert is_valid is True

        # Tamper detection
        is_tampered = StorageService.verify_file_integrity(res["file_path"], "0000000000000000000000000000000000000000000000000000000000000000")
        assert is_tampered is False

        # Cleanup
        try:
            os.remove(res["file_path"])
        except:
            pass


class TestCompanyProfitReports:

    def setup_method(self):
        self.db = SessionLocal()

    def teardown_method(self):
        self.db.rollback()
        self.db.close()

    def test_company_1_profit_analysis(self):
        from app.services.report_service import ReportService
        res = ReportService.get_company_profit_analysis(self.db, company_id=1)
        assert res["company_id"] == 1
        assert "selling_revenue" in res
        assert "purchase_cost" in res
        assert "gross_profit" in res
        assert res["invoice_count"] >= 0

    def test_company_1_wastage_analysis(self):
        from app.services.report_service import ReportService
        res = ReportService.get_company_wastage_analysis(self.db, company_id=1)
        assert res["company_id"] == 1
        assert "gold_wastage_earned_gms" in res
        assert "silver_wastage_earned_gms" in res

    def test_sequence_zero_pad_and_rollback(self):
        from app.services.sequence_service import SequenceService
        from app.models.company import CompanyNumberSequence
        from app.models.invoice import Invoice
        self.db.query(Invoice).filter(Invoice.invoice_number == 'SJ/S/01/26-27').delete()
        self.db.commit()
        seq = self.db.query(CompanyNumberSequence).filter(
            CompanyNumberSequence.company_id == 2,
            CompanyNumberSequence.doc_type == "INVOICE"
        ).first()
        if seq:
            seq.last_sequence = 0
            self.db.commit()

        num1 = SequenceService.generate_document_number(self.db, company_id=2, doc_type="INVOICE")
        assert "/01/" in num1, f"Expected 01 padding in {num1}"

        rolled_back = SequenceService.rollback_document_number(self.db, company_id=2, doc_number=num1, doc_type="INVOICE")
        assert rolled_back is True

        num2 = SequenceService.generate_document_number(self.db, company_id=2, doc_type="INVOICE")
        assert num2 == num1, f"Expected {num1} to be reused after rollback, got {num2}"
