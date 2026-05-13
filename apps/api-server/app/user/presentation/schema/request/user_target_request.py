from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class UpdateUserTargetRequest(BaseModel):
    target_code: str = Field(...)
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )