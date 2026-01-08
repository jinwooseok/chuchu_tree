from dataclasses import dataclass


@dataclass
class GetTagInfoCommand:
    tag_id: int | None = None
    tag_code: str | None = None