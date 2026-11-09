"""
GST Engine
==========
Pure standalone GST calculation engine for Indian Jewellery ERP.
Supports:
- Intra-state (CGST + SGST) vs Inter-state (IGST) auto-detection
- Multi-rate, multi-HSN aggregation
- Round-off to nearest integer (positive or negative)
- Indian Numbering Currency In Words (Lakh, Crore, paise)
- Buyer GSTIN validation
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
import re


def round_cur(val: Decimal) -> Decimal:
    """Round to 2 decimal places using HALF_UP."""
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class GSTLineItem:
    def __init__(
        self,
        description: str,
        hsn_code: str,
        quantity: Decimal,
        rate: Decimal,
        unit: str = "Gms",
        discount: Decimal = Decimal("0.00"),
        making_charges: Decimal = Decimal("0.00"),
        other_charges: Decimal = Decimal("0.00"),
        gst_rate: Optional[Decimal] = None  # total percentage e.g. Decimal("3.00")
    ):
        self.description = description
        self.hsn_code = str(hsn_code).strip()
        self.quantity = Decimal(str(quantity))
        self.rate = Decimal(str(rate))
        self.unit = unit
        self.discount = Decimal(str(discount))
        self.making_charges = Decimal(str(making_charges))
        self.other_charges = Decimal(str(other_charges))
        self.gst_rate = Decimal(str(gst_rate)) if gst_rate is not None else None

        # Taxable amount = (quantity * rate) + making + other - discount
        base_value = self.quantity * self.rate
        self.taxable_amount = round_cur(base_value + self.making_charges + self.other_charges - self.discount)
        if self.taxable_amount < Decimal("0.00"):
            self.taxable_amount = Decimal("0.00")


class GSTEngine:
    # Standard Default Rates per HSN if not explicitly provided
    DEFAULT_RATES: Dict[str, Decimal] = {
        "71081200": Decimal("3.00"),  # Gold Bar / Bullion
        "711319": Decimal("3.00"),    # Gold Ornaments
        "71069120": Decimal("3.00"),  # Silver Bar / Bullion (Pride Reference)
        "71069100": Decimal("3.00"),  # Silver Bullion alternative
        "711311": Decimal("3.00"),    # Silver Ornaments
        "71042120": Decimal("0.25"),  # Synthetic Diamond Unworked
        "71049120": Decimal("1.50"),  # Synthetic Diamond Cut & Polished
        "71023910": Decimal("1.50"),  # Natural Diamond Cut & Polished
    }

    @staticmethod
    def validate_gstin(gstin: Optional[str], state_code: Optional[str] = None) -> Dict[str, Any]:
        """Validate GSTIN format and matching state code."""
        if not gstin or not gstin.strip():
            return {"valid": True, "is_b2c": True, "error": None}

        clean = gstin.strip().upper()
        # 15 char GSTIN regex: 2 digits (state), 10 char PAN, 1 entity, 1 'Z', 1 checksum
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, clean):
            return {"valid": False, "is_b2c": False, "error": f"Invalid GSTIN format: '{clean}'"}

        gstin_state = clean[:2]
        if state_code and str(state_code).zfill(2) != gstin_state:
            return {
                "valid": False,
                "is_b2c": False,
                "error": f"GSTIN state code '{gstin_state}' does not match customer state code '{state_code}'"
            }

        return {"valid": True, "is_b2c": False, "error": None, "state_code": gstin_state}

    @classmethod
    def calculate_invoice_gst(
        cls,
        seller_state_code: str,
        place_of_supply_state_code: str,
        items: List[GSTLineItem],
        custom_rates: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Any]:
        """
        Calculate complete GST breakdown:
        - Determine Intra-state vs Inter-state
        - Line-by-line tax computation
        - HSN-grouped tax table
        - Round-off and grand total
        - Words conversion
        """
        seller_state = str(seller_state_code).strip().zfill(2)
        pos_state = str(place_of_supply_state_code).strip().zfill(2)

        is_intra_state = (seller_state == pos_state)
        rates_map = dict(cls.DEFAULT_RATES)
        if custom_rates:
            rates_map.update({k: Decimal(str(v)) for k, v in custom_rates.items()})

        total_taxable = Decimal("0.00")
        total_cgst = Decimal("0.00")
        total_sgst = Decimal("0.00")
        total_igst = Decimal("0.00")

        line_results = []
        hsn_groups: Dict[str, Dict[str, Any]] = {}

        for item in items:
            rate_pct = item.gst_rate if item.gst_rate is not None else rates_map.get(item.hsn_code, Decimal("3.00"))
            taxable = item.taxable_amount
            total_taxable += taxable

            if is_intra_state:
                half_rate = rate_pct / Decimal("2")
                cgst_amt = round_cur(taxable * (half_rate / Decimal("100")))
                sgst_amt = round_cur(taxable * (half_rate / Decimal("100")))
                igst_amt = Decimal("0.00")
                line_tax = cgst_amt + sgst_amt

                total_cgst += cgst_amt
                total_sgst += sgst_amt

                line_info = {
                    "description": item.description,
                    "hsn_code": item.hsn_code,
                    "quantity": float(item.quantity),
                    "rate": float(item.rate),
                    "unit": item.unit,
                    "taxable_amount": float(taxable),
                    "cgst_rate": float(half_rate),
                    "cgst_amount": float(cgst_amt),
                    "sgst_rate": float(half_rate),
                    "sgst_amount": float(sgst_amt),
                    "igst_rate": 0.0,
                    "igst_amount": 0.0,
                    "total_line_tax": float(line_tax),
                    "line_total": float(taxable + line_tax)
                }
            else:
                cgst_amt = Decimal("0.00")
                sgst_amt = Decimal("0.00")
                igst_amt = round_cur(taxable * (rate_pct / Decimal("100")))
                line_tax = igst_amt

                total_igst += igst_amt

                line_info = {
                    "description": item.description,
                    "hsn_code": item.hsn_code,
                    "quantity": float(item.quantity),
                    "rate": float(item.rate),
                    "unit": item.unit,
                    "taxable_amount": float(taxable),
                    "cgst_rate": 0.0,
                    "cgst_amount": 0.0,
                    "sgst_rate": 0.0,
                    "sgst_amount": 0.0,
                    "igst_rate": float(rate_pct),
                    "igst_amount": float(igst_amt),
                    "total_line_tax": float(line_tax),
                    "line_total": float(taxable + line_tax)
                }

            line_results.append(line_info)

            # Group by HSN
            hsn = item.hsn_code
            if hsn not in hsn_groups:
                hsn_groups[hsn] = {
                    "hsn_code": hsn,
                    "taxable_amount": Decimal("0.00"),
                    "cgst_rate": half_rate if is_intra_state else Decimal("0.00"),
                    "cgst_amount": Decimal("0.00"),
                    "sgst_rate": half_rate if is_intra_state else Decimal("0.00"),
                    "sgst_amount": Decimal("0.00"),
                    "igst_rate": Decimal("0.00") if is_intra_state else rate_pct,
                    "igst_amount": Decimal("0.00"),
                    "total_tax_amount": Decimal("0.00")
                }
            hsn_groups[hsn]["taxable_amount"] += taxable
            hsn_groups[hsn]["cgst_amount"] += cgst_amt
            hsn_groups[hsn]["sgst_amount"] += sgst_amt
            hsn_groups[hsn]["igst_amount"] += igst_amt
            hsn_groups[hsn]["total_tax_amount"] += line_tax

        total_tax = total_cgst + total_sgst + total_igst
        pre_round_total = total_taxable + total_tax

        # Round off to nearest rupee
        # If pre_round is 400999.60 -> round_target = 401000.00 -> round_off = +0.40
        round_target = pre_round_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        round_off = round_cur(round_target - pre_round_total)
        grand_total = round_target

        # Format HSN tax table for response
        tax_table = []
        for hsn, data in hsn_groups.items():
            tax_table.append({
                "hsn_code": hsn,
                "taxable_amount": float(data["taxable_amount"]),
                "cgst_rate": float(data["cgst_rate"]),
                "cgst_amount": float(data["cgst_amount"]),
                "sgst_rate": float(data["sgst_rate"]),
                "sgst_amount": float(data["sgst_amount"]),
                "igst_rate": float(data["igst_rate"]),
                "igst_amount": float(data["igst_amount"]),
                "total_tax_amount": float(data["total_tax_amount"])
            })

        amount_words = cls.number_to_indian_words(grand_total)
        tax_words = cls.number_to_indian_words(total_tax)

        return {
            "is_intra_state": is_intra_state,
            "seller_state_code": seller_state,
            "place_of_supply": pos_state,
            "total_taxable_amount": total_taxable,
            "total_cgst_amount": total_cgst,
            "total_sgst_amount": total_sgst,
            "total_igst_amount": total_igst,
            "total_tax_amount": total_tax,
            "pre_round_total": pre_round_total,
            "round_off": round_off,
            "grand_total": grand_total,
            "lines": line_results,
            "hsn_tax_table": tax_table,
            "amount_chargeable_words": f"Indian Rupees {amount_words} Only",
            "tax_amount_words": f"Indian Rupees {tax_words} Only"
        }

    @classmethod
    def number_to_indian_words(cls, amount: Decimal) -> str:
        """
        Convert number to Indian Currency Words format (Lakh, Crore, paise).
        Matches GST Tax Invoice format:
        401000 -> "Four Lakh One Thousand"
        11679.60 -> "Eleven Thousand Six Hundred Seventy Nine and Sixty paise"
        """
        amt = Decimal(str(amount))
        rupees = int(amt)
        paise = int(round((amt - Decimal(rupees)) * 100))

        if rupees == 0 and paise == 0:
            return "Zero"

        rupees_words = cls._integer_to_indian_words(rupees) if rupees > 0 else ""
        if paise > 0:
            paise_words = cls._integer_to_indian_words(paise)
            if rupees > 0:
                return f"{rupees_words} and {paise_words} paise"
            else:
                return f"{paise_words} paise"
        return rupees_words

    @classmethod
    def _integer_to_indian_words(cls, n: int) -> str:
        if n == 0:
            return ""

        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                 "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                 "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        def two_digits(num: int) -> str:
            if num < 20:
                return units[num]
            t = tens[num // 10]
            u = units[num % 10]
            return f"{t} {u}".strip() if u else t

        def three_digits(num: int) -> str:
            h = num // 100
            rem = num % 100
            res = ""
            if h > 0:
                res = f"{units[h]} Hundred"
            if rem > 0:
                td = two_digits(rem)
                res = f"{res} {td}".strip() if res else td
            return res

        # Indian Numbering chunks: Crore (10^7), Lakh (10^5), Thousand (10^3), Hundred (10^2)
        crore = n // 10000000
        n %= 10000000
        lakh = n // 100000
        n %= 100000
        thousand = n // 1000
        n %= 1000
        remainder = n

        parts = []
        if crore > 0:
            parts.append(f"{cls._integer_to_indian_words(crore)} Crore")
        if lakh > 0:
            parts.append(f"{two_digits(lakh)} Lakh")
        if thousand > 0:
            parts.append(f"{two_digits(thousand)} Thousand")
        if remainder > 0:
            parts.append(three_digits(remainder))

        return " ".join(parts).strip()
