import streamlit as st
from chat_main import display_main
from sidebar import display_sidebar

#页面标题
st.set_page_config(
    page_title="AI 文献阅读助手",
    page_icon="📚",
    layout="wide",
)

#消息列表
if "messages" not in st.session_state:
    st.session_state["messages"] = []

#用户 id
if "session_id" not in st.session_state:
    st.session_state.session_id = None

#获取api_key
if "api_key" not in st.session_state:
    st.session_state.api_key = None

#获取公式化图片
if "images" not in st.session_state:
    st.session_state.images = []

#获取当前的文件id
if "file_id" not in st.session_state:
    st.session_state.file_id = None

#侧边栏
display_sidebar()
display_main()

