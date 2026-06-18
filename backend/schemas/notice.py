from pydantic import BaseModel

class NoticeRequest(BaseModel):
    context:   str
    sender:    str = ""
    recipient: str = ""
    tone:      str = "Professional"