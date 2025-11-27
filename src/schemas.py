from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import uuid

def generate_id():
    return str(uuid.uuid4())

class BaseKnowledgeItem(BaseModel):
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    author: str = "user"
    tags: List[str] = Field(default_factory=list)

class GlossaryItem(BaseKnowledgeItem):
    term: str
    definition: str
    category: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)

class DatasetItem(BaseKnowledgeItem):
    name: str
    description: str
    schema_info: Optional[str] = None
    location: Optional[str] = None

class RuleItem(BaseKnowledgeItem):
    title: str
    rule_content: str
    context: Optional[str] = None

class AnalysisItem(BaseKnowledgeItem):
    title: str
    summary: str
    findings: str
    related_files: List[str] = Field(default_factory=list)

KnowledgeType = Literal["glossary", "dataset", "rule", "analysis"]
