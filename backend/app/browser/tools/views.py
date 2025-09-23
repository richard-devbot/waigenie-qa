from typing import Optional
from pydantic import BaseModel, Field


class HoverAction(BaseModel):
    """Parameters for hover action"""
    index: Optional[int] = None
    xpath: Optional[str] = None
    selector: Optional[str] = None


class ExtractionAction(BaseModel):
    query: str = Field(
        default="summary this page",
        description='Extraction goal',
    )
    extract_links: Optional[bool] = Field(
        default=False,
        description='Set to true to extract links from the page',
    )
    tab_id: Optional[str] = Field(
        default=None,
        description='Tab ID to extract from',
    )


class FileExtractionAction(BaseModel):
    file_path: str = Field(
        description='Path to the file to extract content from',
    )