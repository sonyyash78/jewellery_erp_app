"""
Multi-Company Storage & PDF Archiving Service
=============================================
Manages hierarchical and secure storage per company:
- Company 1: Retains legacy structure `JewelleryERP_Data/Archived_PDFs/{Sales,Purchases}/{Party}/{date}.pdf` untouched.
- Company 2+: Uses `JewelleryERP_Data/Company_{id}/GST_Invoices/FY_{fy}/Sales_<PREFIX>_<SERIES>_<SEQ>_<FY>.pdf`.
- Strict path traversal prevention: Validates all paths stay within canonical roots.
- Automatic mirroring to mounted USB storage drives.
- Computes and verifies SHA-256 integrity hashes for all generated files.
"""
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from app.core.config import DATA_DIR


class StorageService:

    @staticmethod
    def get_financial_year(dt: Optional[datetime] = None, fy_start_month: int = 4) -> str:
        """Calculate Indian financial year string (e.g. '26-27')."""
        if dt is None:
            dt = datetime.now()
        year = dt.year
        month = dt.month
        if month >= fy_start_month:
            start_yr = year % 100
            end_yr = (year + 1) % 100
        else:
            start_yr = (year - 1) % 100
            end_yr = year % 100
        return f"{start_yr:02d}-{end_yr:02d}"

    @classmethod
    def get_all_storage_roots(cls) -> List[Path]:
        """Return primary data root and any active external USB drives."""
        roots = [DATA_DIR]
        seen = {str(DATA_DIR).lower()}
        # Check external drive letters D through Z
        for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
            drive = Path(f"{letter}:\\")
            if drive.exists():
                try:
                    usb_root = drive / "JewelleryERP_Data"
                    if str(usb_root).lower() not in seen:
                        seen.add(str(usb_root).lower())
                        roots.append(usb_root)
                except Exception:
                    pass
        return roots

    @classmethod
    def resolve_destination(
        cls,
        company_id: int,
        category: str,
        folder_name: str,
        doc_number: str,
        doc_date: Optional[str] = None
    ) -> Path:
        """
        Determine target relative path based on company:
        - Company 1: Archived_PDFs/{category}/{folder_name}/{doc_date or doc_number}.pdf
        - Company 2+: Company_{company_id}/GST_Invoices/FY_{fy}/Sales_{clean_number}.pdf
        """
        clean_cat = "Sales" if category.lower() in ("sales", "invoices", "invoice") else "Purchases"
        clean_num = re.sub(r'[\\/*?:"<>|]', '_', str(doc_number).strip())

        if company_id == 1:
            # Company 1 Legacy path structure
            filename = f"{doc_date}.pdf" if doc_date else f"{clean_num}.pdf"
            clean_folder = re.sub(r'[\\/*?:"<>|]', '_', str(folder_name).strip())
            return Path("Archived_PDFs") / clean_cat / clean_folder / filename
        else:
            # Company 2+ GST Partitioned structure
            fy = cls.get_financial_year()
            # E.g. Sales_PG_S_1944_26-27.pdf
            filename = f"{clean_cat}_{clean_num}.pdf"
            return Path(f"Company_{company_id}") / "GST_Invoices" / f"FY_{fy}" / filename

    @classmethod
    def save_pdf(
        cls,
        company_id: int,
        category: str,
        folder_name: str,
        doc_number: str,
        pdf_bytes: bytes,
        doc_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Saves PDF document with strict path traversal verification and USB mirroring.
        """
        rel_path = cls.resolve_destination(company_id, category, folder_name, doc_number, doc_date)
        sha256_hash = hashlib.sha256(pdf_bytes).hexdigest()

        saved_paths = []
        for root in cls.get_all_storage_roots():
            target_file = (root / rel_path).resolve()

            # Security: Strict path traversal prevention
            try:
                if not target_file.is_relative_to(root.resolve()):
                    raise ValueError(f"Path traversal detected! Target: {target_file}")
            except AttributeError:
                # Python < 3.9 fallback
                if os.path.commonpath([str(target_file), str(root.resolve())]) != str(root.resolve()):
                    raise ValueError(f"Path traversal detected! Target: {target_file}")

            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, "wb") as f:
                f.write(pdf_bytes)
            saved_paths.append(str(target_file))

        return {
            "primary_path": saved_paths[0] if saved_paths else "",
            "all_paths": saved_paths,
            "sha256_hash": sha256_hash,
            "file_size": len(pdf_bytes)
        }

    @classmethod
    def save_pdf_document(
        cls,
        company_id: int,
        doc_type: str,
        filename: str,
        pdf_bytes: bytes,
        financial_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compatibility wrapper for save_pdf."""
        res = cls.save_pdf(
            company_id=company_id,
            category=doc_type,
            folder_name=f"Company_{company_id}",
            doc_number=filename,
            pdf_bytes=pdf_bytes
        )
        return {
            "file_path": res.get("primary_path"),
            "filename": filename,
            "file_size": res.get("file_size"),
            "sha256_hash": res.get("sha256_hash")
        }

    @classmethod
    def verify_file_integrity(cls, file_path: Path, expected_hash: str) -> bool:
        """Verify that the stored file matches its stored SHA-256 hash."""
        p = Path(file_path)
        if not p.exists():
            return False
        with open(p, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        return actual.lower() == expected_hash.lower()
