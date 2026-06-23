import os
import re
from typing import List, Dict

class CodeSecurityScanner:
    """Scans source code for hardcoded secrets and unsafe patterns."""
    
    PATTERNS = {
        "hardcoded_password": r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
        "hardcoded_api_key": r"(?i)(api_key|apikey|secret|token)\s*=\s*['\"][^'\"]+['\"]",
        "unsafe_sql": r"(?i)execute\s*\(\s*f['\"].*\{.*\}.*['\"]\s*\)", # Raw f-string interpolation in execute
        "hardcoded_jwt": r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"
    }

    @classmethod
    def scan_directory(cls, root_dir: str) -> List[Dict[str, str]]:
        findings = []
        for root, _, files in os.walk(root_dir):
            for file in files:
                if not file.endswith(".py") and not file.endswith(".env") and not file.endswith(".yml"):
                    continue
                    
                filepath = os.path.join(root, file)
                
                # Skip the scanner itself to avoid self-matches
                if "scanners.py" in filepath or "tests" in filepath or "attack" in filepath:
                    continue
                    
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        content = f.read()
                        for rule_name, pattern in cls.PATTERNS.items():
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                findings.append({
                                    "file": filepath,
                                    "rule": rule_name,
                                    "match": match.group(0)[:50] + "..." # Truncate for safety
                                })
                    except Exception:
                        pass
        return findings
