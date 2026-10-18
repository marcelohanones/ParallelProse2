"""Typed stops for ingestion. A stop carries a rule id, a file, and a chapter where one applies (M15)."""


class IngestError(Exception):
    def __init__(self, rule_id: str, file: str, chapter: str | None = None):
        self.rule_id = rule_id
        self.file = file
        self.chapter = chapter
        super().__init__(self.error_line())

    def error_line(self) -> str:
        parts = [self.rule_id, f"file={self.file}"]
        if self.chapter is not None:
            parts.append(f"chapter={self.chapter}")
        return " ".join(parts)
