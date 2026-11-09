"""
Atomic Document Sequence Generator
==================================
Thread-safe and multi-worker safe sequence generation with row-level locks.
Company 1 retains legacy 'INV-YYYYMMDD-XXXX' format unchanged.
Company 2+ uses GST compliant '<PREFIX>/<SERIES>/<SEQ>/<FY>' (max 16 chars).
All GST sequences start at 01 (e.g. SJ/S/01/26-27, SJ/P/01/26-27, SJ/E/01/26-27)
and roll back cleanly on cancellation/deletion with zero gaps.
"""
import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.company import Company, CompanyNumberSequence
from app.models.number_sequence import NumberSequence
from app.services.storage_service import StorageService


class SequenceService:

    @classmethod
    def generate_document_number(
        cls,
        db: Session,
        company_id: int,
        doc_type: str = "INVOICE"
    ) -> str:
        """
        Generate next sequential document number.
        Enforces company-specific formatting and resets per financial year.
        Company 1: Legacy format (INV-YYYYMMDD-XXXX, PUR-YYYYMMDD-XXXX, EXC-YYYYMMDD-XXXX)
        Company 2+: GST format (SJ/S/01/26-27, SJ/P/01/26-27, SJ/E/01/26-27)
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        is_gst = bool(company and company.gst_enabled)

        # Company 1 Non-GST legacy numbering behavior
        if not is_gst and company_id == 1:
            return cls._generate_legacy_number(db, company_id, doc_type)

        # GST Multi-Company numbering: <PREFIX>/<SERIES>/<SEQ>/<FY>
        fy = StorageService.get_financial_year(fy_start_month=company.financial_year_start if company else 4)
        prefix = company.invoice_prefix if (company and company.invoice_prefix) else "SJ"
        series = company.invoice_series if (company and company.invoice_series) else "S"

        # Map doc_type for series if purchase/exchange
        dtype_upper = doc_type.upper()
        if dtype_upper == "PURCHASE":
            series = "P"
        elif dtype_upper == "EXCHANGE":
            series = "E"
        elif dtype_upper == "CREDIT_NOTE":
            series = "CN"
        elif dtype_upper == "DEBIT_NOTE":
            series = "DN"

        # Lock sequence row using with_for_update()
        seq_record = db.query(CompanyNumberSequence).filter(
            CompanyNumberSequence.company_id == company_id,
            CompanyNumberSequence.financial_year == fy,
            CompanyNumberSequence.doc_type == dtype_upper
        ).with_for_update().first()

        if not seq_record:
            # First number in this FY for this company starts at 1
            start_seq = 1
            seq_record = CompanyNumberSequence(
                company_id=company_id,
                financial_year=fy,
                doc_type=dtype_upper,
                last_sequence=start_seq,
                prefix=prefix,
                series=series
            )
            db.add(seq_record)
            db.flush()
            next_num = start_seq
        else:
            seq_record.last_sequence += 1
            db.flush()
            next_num = seq_record.last_sequence

        num_str = f"{next_num:02d}" if next_num < 100 else str(next_num)
        doc_number = f"{prefix}/{series}/{num_str}/{fy}"

        # Collision prevention: ensure number is not already actively in use
        if dtype_upper == "INVOICE":
            from app.models.invoice import Invoice
            while db.query(Invoice).filter(Invoice.invoice_number == doc_number).first() is not None:
                seq_record.last_sequence += 1
                next_num = seq_record.last_sequence
                num_str = f"{next_num:02d}" if next_num < 100 else str(next_num)
                doc_number = f"{prefix}/{series}/{num_str}/{fy}"
                db.flush()
        elif dtype_upper == "PURCHASE":
            from app.models.purchase import Purchase
            while db.query(Purchase).filter(Purchase.purchase_number == doc_number).first() is not None:
                seq_record.last_sequence += 1
                next_num = seq_record.last_sequence
                num_str = f"{next_num:02d}" if next_num < 100 else str(next_num)
                doc_number = f"{prefix}/{series}/{num_str}/{fy}"
                db.flush()
        elif dtype_upper == "EXCHANGE":
            from app.models.exchange import Exchange
            if hasattr(Exchange, 'exchange_number'):
                while db.query(Exchange).filter(Exchange.exchange_number == doc_number).first() is not None:
                    seq_record.last_sequence += 1
                    next_num = seq_record.last_sequence
                    num_str = f"{next_num:02d}" if next_num < 100 else str(next_num)
                    doc_number = f"{prefix}/{series}/{num_str}/{fy}"
                    db.flush()

        # GST Rule Validation: max 16 characters, only [A-Za-z0-9/-]
        if len(doc_number) > 16:
            doc_number = f"{prefix}/{num_str}/{fy}"[:16]

        assert re.match(r"^[A-Za-z0-9\/\-]+$", doc_number), f"Invalid GST invoice number: {doc_number}"
        return doc_number

    @classmethod
    def rollback_document_number(
        cls,
        db: Session,
        company_id: int,
        doc_number: str,
        doc_type: str = "INVOICE"
    ) -> bool:
        """
        Roll back sequence counter if the deleted or cancelled document was the latest sequence.
        Ensures no gaps are left in sequence numbering (e.g. SJ/S/01/26-27 -> rolled back so next starts at 01 again).
        """
        if not doc_number:
            return False

        # Format: <PREFIX>/<SERIES>/<SEQ>/<FY> (e.g. SJ/S/01/26-27 or SJ/P/01/26-27)
        parts = doc_number.strip().split('/')
        if len(parts) >= 4:
            try:
                seq_val = int(parts[2])
                fy_val = parts[3]
                dtype_upper = doc_type.upper()
                seq_record = db.query(CompanyNumberSequence).filter(
                    CompanyNumberSequence.company_id == company_id,
                    CompanyNumberSequence.financial_year == fy_val,
                    CompanyNumberSequence.doc_type == dtype_upper
                ).with_for_update().first()

                if seq_record and seq_record.last_sequence == seq_val:
                    seq_record.last_sequence = max(0, seq_record.last_sequence - 1)
                    db.flush()
                    return True
            except (ValueError, IndexError):
                pass

        return False

    @classmethod
    def _generate_legacy_number(
        cls,
        db: Session,
        store_id: int,
        doc_type: str
    ) -> str:
        """Legacy Company 1 generator: INV-YYYYMMDD-XXXX (untouched)."""
        from app.api.v1.invoices import generate_invoice_number
        if doc_type.upper() == "INVOICE":
            return generate_invoice_number(db, store_id=store_id)

        # For purchase/exchange legacy
        today = datetime.now().strftime('%Y%m%d')
        pfx = "PUR" if doc_type.upper() == "PURCHASE" else "EXC"
        entity_key = f"{pfx.lower()}_s{store_id}_{today}"
        prefix = f"{pfx}-{today}" if store_id == 1 else f"{pfx}-S{store_id}-{today}"

        seq = db.query(NumberSequence).filter(NumberSequence.entity == entity_key).with_for_update().first()
        if not seq:
            seq = NumberSequence(entity=entity_key, prefix=prefix, next_number=1)
            db.add(seq)
            db.flush()
            next_num = 1
        else:
            next_num = seq.next_number
            seq.next_number += 1
            db.flush()

        return f"{prefix}-{next_num:04d}"
