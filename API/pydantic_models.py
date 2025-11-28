#接口类型
from datetime import datetime
from typing import List
import numpy as np
from pydantic import BaseModel, Field

#文件列表参数
class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime

#文件删除参数
class FileRequest(BaseModel):
    file_id: int

#问题回答参数
class Query_Answer(BaseModel):
    answer:str
    session_id:str

class Query_Input(BaseModel):
    question: str
    session_id: str = Field(default=None) #表示默认值
    api_key: str

class Image_OCR(BaseModel):
    images_data: List[str]   # 或 int，根据你的 np.array dtype