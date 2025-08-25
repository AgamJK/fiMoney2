from pydantic import BaseModel

class Msg(BaseModel):
    """Generic message response schema"""
    msg: str
