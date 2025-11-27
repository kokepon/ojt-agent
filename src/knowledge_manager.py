import json
from pathlib import Path
from typing import List, Type
from pydantic import ValidationError
from .schemas import GlossaryItem, DatasetItem, RuleItem, AnalysisItem, KnowledgeType

SCHEMA_MAP = {
    "glossary": GlossaryItem,
    "dataset": DatasetItem,
    "rule": RuleItem,
    "analysis": AnalysisItem
}

def validate_line(line: str, schema: Type) -> bool:
    try:
        data = json.loads(line)
        schema.model_validate(data)
        return True
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation error: {e}")
        return False

def validate_file(file_path: Path, knowledge_type: KnowledgeType) -> bool:
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False

    schema = SCHEMA_MAP.get(knowledge_type)
    if not schema:
        print(f"Unknown knowledge type: {knowledge_type}")
        return False

    all_valid = True
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            if not validate_line(line, schema):
                print(f"Line {i} is invalid in {file_path}")
                all_valid = False

    return all_valid
