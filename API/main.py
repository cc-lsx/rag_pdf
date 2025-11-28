import logging
import os
import shutil
import uuid
from typing import List
from langchain_utils import get_rag_chain
from pydantic_models import DocumentInfo, FileRequest,Query_Input,Query_Answer,Image_OCR
from db_utils import insert_document_record, get_all_documents, delete_document_db, get_chat_history, \
    insert_application_logs, image_list
from fastapi import FastAPI, File, UploadFile, HTTPException
from chroma_utils import index_document_to_chroma, delete_document_chroma
from pdf_recognize import pdf_formula_to_documents,encode_image

app = FastAPI()
#调试日志
logging.basicConfig(filename='app.log', level=logging.INFO)
#文档加载
@app.post('/upload_doc')
def upload_and_index_document(file: UploadFile = File(...)):
    print("111222")
    allowed_extensions = ['.pdf', '.png']
    file_extension = os.path.splitext(file.filename)[1].strip().lower()  # 去掉空格
    print("文件扩展名:", file_extension)
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持该文件类型：{', '.join([ext.lstrip('.') for ext in allowed_extensions])}"
        )

    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        document, images = pdf_formula_to_documents(temp_file_path)
        file_id = insert_document_record(file.filename, images)
        success = index_document_to_chroma(document, file_id)
        if success:
            return {"message": f"文件 {file.filename} 已经成功加载.", "file_id": file_id}
        else:
            delete_document_chroma(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


#获取文档名称列表
@app.get('/list_docs',response_model=List[DocumentInfo])
def list_documents():
    return get_all_documents()

#删除文件,既需要删除向量数据库，也需要删除文件数据库,由于前端需要返回json
@app.post('/delete_doc')
def delete_document(request: FileRequest):
    #删除向量数据库
    success_chroma = delete_document_chroma(request.file_id)
    if success_chroma:
        delete_document = delete_document_db(request.file_id)
        if delete_document:
            return {"message":f"成功删除文件{request.file_id}。"}
        else:
            return {"error":f"文件数据库删除失败{request.file_id}。"}
    else:
        return {"error":f"向量数据库删除失败{request.file_id}。"}


#聊天路由
@app.post("/chat",response_model=Query_Answer)
def chat(query_input:Query_Input):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"session_id:{session_id}，user query:{query_input.question}")
    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.api_key)
    answer = rag_chain.invoke(
        {
            'input': query_input.question,
            "chat_history": chat_history,
        }
    )['answer']
    #用户回答日志
    #用户问答日志
    insert_application_logs(session_id, query_input.question, answer)
    logging.info(f"用户id: {session_id}, AI 回复: {answer}")
    return Query_Answer(answer=answer, session_id=session_id,)

#获取图片列表
@app.post('/image_ocr', response_model=Image_OCR)
def image_ocr(request: FileRequest):
    print("接口被调用，file_id:", request.file_id)
    images_list_data = image_list(request.file_id)
    if images_list_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    # 转为 base64
    images_serializable = []
    for img in images_list_data:
        try:
            b64 = encode_image(img)
            images_serializable.append(b64)
        except Exception as e:
            print(f"图片转换失败: {e}")
    print("返回图片数量:", len(images_serializable))
    return {"images_data": images_serializable}


#用于端口测试
@app.get("/ping")
def ping():
    print("ping接口被调用")
    return {"msg": "pong"}