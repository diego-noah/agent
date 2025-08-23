import subprocess
import json
from typing import List, Dict
from .base import AbstractAdapter

class ManticoreAdapter(AbstractAdapter):
    def run(self, contract_path: str, **kwargs) -> List[Dict]:
        cmd = [
            "manticore", contract_path, "--no-progress", "--output", "mcore_out"
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=kwargs.get("timeout", 180))
            return self._parse_workspace("mcore_out")
        except Exception as e:
            return [{"title": "Manticore Error", "description": str(e), "severity": "Low", "swc_id": "", "line_numbers": [], "confidence": "Low", "tool": "Manticore"}]

    def _parse_workspace(self, workspace: str) -> List[Dict]:
        # Manticore writes findings to a JSON file in the workspace directory
        try:
            with open(f"{workspace}/global.findings", "r") as f:
                findings_json = json.load(f)
            findings = []
            for issue in findings_json.get("issues", []):
                finding = {
                    "title": issue.get("title", ""),
                    "description": issue.get("description", ""),
                    "severity": issue.get("severity", "Medium"),
                    "swc_id": issue.get("swc_id", ""),
                    "line_numbers": issue.get("lines", []),
                    "confidence": issue.get("confidence", "Medium"),
                    "tool": "Manticore"
                }
                findings.append(self.standardize_finding(finding))
            return findings
        except Exception:
            return []

    def parse_output(self, output: str) -> List[Dict]:
        # Not used, as Manticore writes to workspace
        return []
