import os

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek
from chroma_utils import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


contextualize_q_system_prompt = (
        "给定一段聊天历史和最新的用户提问（该提问可能会引用聊天历史中的内容），"
        "请将其改写为一个无需依赖聊天历史、也能够被独立理解的提问。"
        "不要回答该问题；如果需要，请对其进行改写，否则保持原样返回。"
    )

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])  # 这里的输出仅是一个问题

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的文献阅读助手，旨在帮住更好的阅读文献"),
    ("system", "Context: {context}"),  # context自动从向量数据库检索
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

def get_rag_chain(api_key):
    if api_key is not None:
        os.environ["DEEPSEEK_API_KEY"] = api_key
        llm = ChatDeepSeek(model="deepseek-chat")
        #上下文提示词
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)  # 生成检索器，即检索文档
        question_answer_chain = create_stuff_documents_chain(llm,qa_prompt)  # 文档问答链，通常指把多个检索到的文档片段“堆起来（stuff）”，一次性给模型处理，而不是逐个处理。
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)  # 把检索和问答组合起来
        return rag_chain
    else:
        print(f"api为空")
        return None