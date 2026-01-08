from dataclasses import dataclass


@dataclass
class GetTargetInfoCommand:
    target_id: int | None = None
    target_code: str | None = None