# backend/app/rubric_engine.py
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

class RubricEngine:
    """
    Loads a YAML rubric and evaluates a structured LLM response.
    The LLM is asked to output a markdown table:
        | Dimension | Score (0‑max) | Comments |
    """
    def __init__(self, rubric_path: Path = Path(__file__).parent / "rubric.yaml"):
        with open(rubric_path, "r", encoding="utf8") as f:
            self.rubric = yaml.safe_load(f)

    def _parse_table(self, text: str) -> List[Dict[str, str]]:
        """
        Very tolerant parser – works even if the model adds extra spaces or markdown fences.
        Returns a list of dicts: [{ "Dimension": "...", "Score": "...", "Comments": "..." }, ...]
        """
        rows = []
        # Grab the part between the first and last pipe‑line that looks like a table
        table_match = re.search(r"\|.*\|\s*\n(\|.*\|\s*\n)+", text)
        if not table_match:
            raise ValueError("No markdown table detected in LLM output")
        lines = [ln.strip() for ln in table_match.group(0).splitlines() if ln.strip()]
        # Remove the header separator line (---)
        if len(lines) > 1 and set(lines[1].replace("|", "")) <= {"-"}:
            lines.pop(1)
        for line in lines[1:]:            # skip header row
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 3:
                rows.append({"Dimension": cols[0],
                             "Score": cols[1],
                             "Comments": cols[2]})
        return rows

    def evaluate(self, llm_output: str) -> Tuple[float, Dict[str, Any]]:
        """
        Returns:
            - overall numeric grade (0‑100)
            - detailed dict with per‑dimension scores + comments
        """
        table = self._parse_table(llm_output)

        # Build a lookup: dimension → (score, comment)
        lookup = {row["Dimension"].lower(): (float(row["Score"]), row["Comments"])
                  for row in table}

        total_weighted = 0.0
        max_total = 0.0
        details = {}

        for dim in self.rubric["final_grade"]["dimensions"]:
            dim_name = dim["name"]
            key = dim_name.lower()
            max_score = dim["max_score"]
            weight = dim["weight"]
            max_total += weight * max_score

            if key not in lookup:
                # Missing dimension – treat as 0 with a warning comment
                score, comment = 0.0, "Dimension not reported by LLM"
            else:
                score, comment = lookup[key]

            # Clamp score to the allowed max
            score = max(0.0, min(score, max_score))
            total_weighted += weight * score

            details[dim_name] = {
                "score": score,
                "max_score": max_score,
                "weight": weight,
                "comment": comment,
            }

        overall = round(100.0 * total_weighted / max_total, 2)
        return overall, {"overall": overall, "details": details}