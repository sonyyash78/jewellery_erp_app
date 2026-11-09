p_pur = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py"
with open(p_pur, "r", encoding="utf-8") as f:
    cp = f.read()
cp = cp.replace("from typing import Any, List", "from typing import Any, List, Optional")
with open(p_pur, "w", encoding="utf-8") as f:
    f.write(cp)
print("Added Optional to purchases.py")

p_ex = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py"
with open(p_ex, "r", encoding="utf-8") as f:
    ce = f.read()
ce = ce.replace("from typing import Dict, Any, List", "from typing import Dict, Any, List, Optional")
ce = ce.replace("from fastapi import APIRouter, Depends, HTTPException, Query", "from fastapi import APIRouter, Depends, HTTPException, Query, Header")
with open(p_ex, "w", encoding="utf-8") as f:
    f.write(ce)
print("Added Optional and Header to exchanges.py")
