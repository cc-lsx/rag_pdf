import os
import streamlit as st

from api_utils import get_api_response, images_document

def display_main():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("## Viewer")
        html_content = """
        <div style="
            height:1000px;
            overflow-y:scroll;
            border:1px solid #ccc;
            border-radius:8px;
            padding:10px;
        ">
        """
        # 获取数据库中的 image
        if st.session_state.file_id:
            print("获取file_id:", st.session_state.file_id)
            result = images_document(st.session_state.file_id)
            st.session_state.images = result["images_data"]
            if st.session_state.get("images"):
                for page_idx, page_imgs in enumerate(st.session_state.images):
                    # 确保每页是列表
                    if not isinstance(page_imgs, (list, tuple)):
                        page_imgs = [page_imgs]
                    html_content += f"<h4>第 {page_idx + 1} 页</h4>"
                    for img_idx, b64 in enumerate(page_imgs):
                        # 这里直接用接口返回的 base64
                        html_content += f"""
                        <div style="
                            border:2px solid #e63946;
                            border-radius:8px;
                            padding:10px;
                            margin-bottom:15px;
                        ">
                            <img src="data:image/png;base64,{b64}" style="width:100%; border-radius:6px;">
                            <p>第 {page_idx + 1} 页 - 第 {img_idx + 1} 张</p>
                        </div>
                        """
            else:
                st.warning("请导入你的 PDF 文件")
        html_content += "</div>"
        st.html(html_content)

    with col2:
        # 容器用于显示聊天消息
        chat_container = st.container()
        # 渲染已有消息
        for message in st.session_state.get("messages", []):
            with chat_container:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        # 使用 st.markdown 注入 CSS
        st.markdown(
            """
            <style>
            .stChatInput > div {
                position: fixed;
                bottom: 20px;
                width: 40%;
                z-index: 999;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # 输入栏固定在底部
        prompt = st.chat_input("请输入问题：")
        if prompt:
            # 添加用户消息
            if "messages" not in st.session_state:
                st.session_state["messages"] = []
            st.session_state["messages"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            # 调用 API 获取响应
            with st.spinner("推理中。。。"):
                response = get_api_response(
                    prompt,
                    st.session_state.get("session_id"),
                    st.session_state.get("api_key")
                )
                if response:
                    # 更新 session_id 和 assistant 消息
                    st.session_state["session_id"] = response.get("session_id")
                    st.session_state["messages"].append({"role": "assistant", "content": response["answer"]})
                    with st.chat_message("assistant"):
                        st.markdown(response["answer"])
                        with st.expander("细节"):
                            st.subheader("生成答案")
                            st.code(response["answer"])
                            st.subheader("用户 ID")
                            st.code(response["session_id"])
                else:
                    st.error("回复响应 API 失效，请重试")
