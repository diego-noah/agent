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
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=kwargs.get("timeout", 180)+10)
            return self.parse_output(result.stdout)
        except Exception as e:
            return [{"title": "Mythril Error", "description": str(e), "severity": "Low", "swc_id": "", "line_numbers": [], "confidence": "Low", "tool": "Mythril"}]

    def parse_output(self, output: str) -> List[Dict]:
        try:
            data = json.loads(output)
            findings = []
            for issue in data.get("issues", []):
                finding = {
                    "title": issue.get("title", ""),
                    "description": issue.get("description", ""),
                    "severity": issue.get("severity", "Medium"),
                    "swc_id": issue.get("swc-id", ""),
                    "line_numbers": [loc.get("sourceMap", "") for loc in issue.get("locations", [])],
                    "confidence": issue.get("confidence", "Medium"),
                    "tool": "Mythril"
                }
                findings.append(self.standardize_finding(finding))
            return findings
        except Exception:
            return []
