import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.audit import init_audit_db

if __name__ == "__main__":
    init_audit_db()
    print("Audit database initialized.")