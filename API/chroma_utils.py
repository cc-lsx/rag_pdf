from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings #使用HuggingFace的向量嵌入
from langchain_chroma import Chroma

def split_documents_by_page(docs, chunk_size=500, chunk_overlap=100):
    """
    输入 docs 可以是：
    - Document 列表
    - [(content, metadata), ...] 列表
    输出：Document 列表，每条 chunk 有 page、source、chunk_id
    """
    # 转成 Document 对象
    document_objects = []
    for d in docs:
        if isinstance(d, Document):
            document_objects.append(d)
        elif isinstance(d, tuple) and len(d) == 2:
            content, meta = d
            document_objects.append(Document(page_content=content, metadata=meta))
        else:
            raise ValueError("每个文档必须是 Document 或 (content, metadata) tuple")

    # 展平二维列表（如果有嵌套列表）
    document_objects = [d for sublist in document_objects for d in (sublist if isinstance(sublist, list) else [sublist])]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    new_docs = []

    for doc in document_objects:
        chunks = splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            new_docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "page": doc.metadata.get("page"),
                        "source": doc.metadata.get("source"),
                        "chunk_id": i,
                        **doc.metadata  # 保留原有其他 metadata
                    }
                )
            )
    return new_docs

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
def index_document_to_chroma(document, file_id: int) -> bool:
    """
    将文档拆分成 chunk 并嵌入到 Chroma 向量数据库
    document 可以是 Document 列表 或 (content, metadata) tuple 列表
    """
    try:
        new_docs = split_documents_by_page(document)
        # 添加 file_id
        for doc in new_docs:
            doc.metadata['file_id'] = file_id
        vectorstore.add_documents(new_docs)
        print("向量嵌入成功！")
        return True
    except Exception as e:
        print(f"向量嵌入失败: {e}")
        return False


#向量数据库的删除
def delete_document_chroma(file_id:int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        print(f"发现文件{file_id}的{len(docs['ids'])}。")
        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"文件{file_id}删除成功。")
        return True
    except Exception as e:
        print(f"文件{file_id}在删除时发生错误：{str(e)}。")
        return False
