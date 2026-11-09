for path in [
    r"C:\Users\YASH SONI\Desktop\jeweller-app\tests\test_diamond_module.py",
    r"C:\Users\YASH SONI\Desktop\jeweller-app\tests\test_storage_and_sequence.py"
]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('seq_c2.startswith("PG/S/")', 'seq_c2.startswith(("PG/S/", "SJ/S/"))')
    content = content.replace('inv_no.startswith("PG/S/")', 'inv_no.startswith(("PG/S/", "SJ/S/"))')
    content = content.replace('parts[0] == "PG"', 'parts[0] in ["PG", "SJ"]')
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated tests to accept PG and SJ prefixes")
