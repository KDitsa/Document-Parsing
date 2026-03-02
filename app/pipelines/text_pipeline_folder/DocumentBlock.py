from dataclasses import dataclass
from typing import Optional, Tuple, Union, Dict

@dataclass
class DocumentBlock:
    id: str
    type: str  # "text", "table", "image"
    content: Union[str, Dict]
    page_number: Optional[int] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    metadata: Optional[Dict] = None