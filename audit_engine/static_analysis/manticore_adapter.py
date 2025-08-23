import subprocess
import json
from typing import List, Dict
from .base import AbstractAdapter
import tempfile
import shutil
import os
class ManticoreAdapter(AbstractAdapter):
    def run(self, contract_path: str, **kwargs) -> List[Dict]:
        workspace = kwargs.get("workspace") or tempfile.mkdtemp(prefix="mcore_")
        cmd = ["manticore", contract_path, "--no-progress", "--output", workspace]
        try:
            subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=kwargs.get("timeout", 180), check=True
            )
            return self._parse_workspace(workspace)
        except subprocess.CalledProcessError as e:
            return [self.standardize_finding({
                "title": "Manticore Error",
                "description": (e.stderr or str(e)).strip(),
                "severity": "Low",
                "swc_id": "",
                "line_numbers": [],
                "confidence": "Low",
                "tool": "Manticore"
            })]
        except Exception as e:
            return [self.standardize_finding({
                "title": "Manticore Error",
                "description": str(e),
                "severity": "Low",
                "swc_id": "",
                "line_numbers": [],
                "confidence": "Low",
                "tool": "Manticore"
            })]
        finally:
            if kwargs.get("cleanup", True):
                shutil.rmtree(workspace, ignore_errors=True)

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
