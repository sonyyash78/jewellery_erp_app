with open(r'C:\Users\YASH SONI\Desktop\jeweller-app\tests\test_storage_and_sequence.py', 'a', encoding='utf-8') as f:
    f.write('''
    def test_sequence_zero_pad_and_rollback(self):
        from app.services.sequence_service import SequenceService
        from app.models.company import CompanyNumberSequence
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
''')
print("Successfully appended test")
