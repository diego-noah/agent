import subprocess
import json
from typing import List, Dict
from .base import AbstractAdapter

class MythrilAdapter(AbstractAdapter):
    def run(self, contract_path: str, **kwargs) -> List[Dict]:
        cmd = [
            "myth", "analyze", contract_path,
            "-o", "json",
            "--execution-timeout", str(kwargs.get("timeout", 180))
        ]
        try:
            timeout = int(kwargs.get("timeout", 180))
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout + 10, check=True
            )
            output = result.stdout or result.stderr or ""
            return self.parse_output(output)
        except subprocess.CalledProcessError as e:
            return [self.standardize_finding({
                "title": "Mythril Error",
                "description": (e.stderr or str(e)).strip(),
                "severity": "Low",
                "swc_id": "",
                "line_numbers": [],
                "confidence": "Low",
                "tool": "Mythril"
            })]
        except Exception as e:
            return [self.standardize_finding({
                "title": "Mythril Error",
                "description": str(e),
                "severity": "Low",
                "swc_id": "",
                "line_numbers": [],
                "confidence": "Low",
                "tool": "Mythril"
            })]


    def parse_output(self, output: str) -> List[Dict]:
        try:
            data = json.loads(output) if output and output.strip() else {}
            findings: List[Dict] = []
            # Support both dict-with-issues and top-level list formats
            issues = []
            if isinstance(data, dict):
                issues = data.get("issues", []) or data.get("findings", [])
            elif isinstance(data, list):
                issues = data
            for issue in issues:
                # Prefer explicit integer line info if provided
                line_numbers: List[int] = []
                lines_val = issue.get("lines")
                if isinstance(lines_val, list):
                    line_numbers.extend([ln for ln in lines_val if isinstance(ln, int)])
                for key in ("line", "lineno"):
                    v = issue.get(key)
                    if isinstance(v, int):
                        line_numbers.append(v)
                finding = {
                    "title": issue.get("title", ""),
                    "description": issue.get("description", ""),
                    "severity": issue.get("severity", "Medium"),
                    "swc_id": issue.get("swc-id") or issue.get("swc_id", ""),
                    "line_numbers": line_numbers,
                    "confidence": issue.get("confidence", "Medium"),
                    "tool": "Mythril",
                }
                findings.append(self.standardize_finding(finding))
            return findings
        except Exception:
            return []

