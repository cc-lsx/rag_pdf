import streamlit as st
from api_utils import upload_document,list_documents,delete_document


#侧边栏设计
def display_sidebar():
    st.sidebar.header('🔑 API密钥配置')
    st.sidebar.warning("️⚠️ Deepseek API输入:")
    api_key = st.sidebar.text_input("API KEY",type="password",help="请输入API KEY,帮助阅读文献")
    if api_key:
        st.session_state.api_key = api_key
    uploader_file = st.sidebar.file_uploader("上传文件",type=["pdf","png"])
    if uploader_file and st.sidebar.button("加载"):
        with st.spinner("正在处理文档，请稍后"):
            uploader_response = upload_document(uploader_file)
            if uploader_response:
                st.sidebar.success(f"文件成功加载{uploader_response}")
                st.session_state.document = list_documents()

    #加载文件列表
    st.sidebar.header("加载的文件")
    if st.sidebar.button("刷新文件列表"):
        st.session_state.document = list_documents()

    #将文件名显示
    if "document" in st.session_state and st.session_state.document:
        for doc in st.session_state.document:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']})")
            st.session_state.file_id = st.session_state.document[0]['id'] #一直获取最新文件的id
            print(st.session_state.file_id)


        #这里显示删除文件的选项
        select_file_id = st.sidebar.selectbox("选择一个文件删除",options=[doc['id'] for doc in st.session_state.document])

        if st.sidebar.button("删除文件"):
            delete_response = delete_document(select_file_id)
            if delete_response:
                st.sidebar.success(f"文件成功删除.")
                st.session_state.documents = list_documents()




