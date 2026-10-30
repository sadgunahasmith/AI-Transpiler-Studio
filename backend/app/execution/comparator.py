"""
Execution Output Comparator: Tests behavioral and semantic equivalence between source and target outputs.
"""
import difflib
from typing import Dict, Any

class OutputComparator:
    """Verifies output equivalence and formats visual diffs between program executions."""

    def compare(
        self,
        source_stdout: str,
        target_stdout: str,
        source_stderr: str = "",
        target_stderr: str = "",
        source_success: bool = True,
        target_success: bool = True
    ) -> Dict[str, Any]:
        # Normalize trailing whitespaces and line endings
        s_clean = source_stdout.strip().replace("\r\n", "\n")
        t_clean = target_stdout.strip().replace("\r\n", "\n")

        # An execution error (including a security block) must never be reported
        # as equivalent just because both programs produced empty stdout.
        execution_failed = (not source_success) or (not target_success) or bool(source_stderr or target_stderr)
        exact_match = (s_clean == t_clean) and not execution_failed

        # Similarity is undefined when either program failed to execute.
        if execution_failed:
            similarity = None
        else:
            seq = difflib.SequenceMatcher(None, s_clean, t_clean)
            similarity = round(seq.ratio() * 100, 1)

        # Generate line-by-line diff
        diff_lines = list(difflib.unified_diff(
            s_clean.splitlines(keepends=True),
            t_clean.splitlines(keepends=True),
            fromfile="source_output",
            tofile="target_output"
        ))
        diff_text = "".join(diff_lines)

        status = "RUNTIME_ERROR" if execution_failed else ("MATCH" if exact_match else ("CLOSE_MATCH" if similarity > 80.0 else "MISMATCH"))

        return {
            "is_equivalent": exact_match,
            "status": status,
            "similarity_percentage": similarity,
            "diff": ("Cannot compare outputs because at least one program failed to execute." if execution_failed else (diff_text if not exact_match else "Exact character-for-character output match.")),
            "source_length": len(s_clean),
            "target_length": len(t_clean)
        }
