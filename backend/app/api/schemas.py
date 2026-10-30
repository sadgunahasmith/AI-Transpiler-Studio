"""
Pydantic Request and Response Models for REST API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AnalyzeRequest(BaseModel):
    language: str
    code: str

class DetectErrorsRequest(BaseModel):
    language: str
    code: str

class CorrectRequest(BaseModel):
    language: str
    code: str
    compiler_errors: Optional[List[Dict[str, Any]]] = None
    ai_mode: Optional[str] = "hybrid_correction"

class TranspileRequest(BaseModel):
    source_language: str
    target_language: str
    code: str
    optimize: bool = True
    ai_mode: Optional[str] = "compiler_only"

class ExecuteRequest(BaseModel):
    language: str
    code: str
    stdin: Optional[str] = ""

class CompareRequest(BaseModel):
    source_language: str
    target_language: str
    source_code: str
    target_code: str
    stdin: Optional[str] = ""
