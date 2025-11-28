import requests
import streamlit as st


#文件加载
def upload_document(file):
    print("加载中。。。")
    try:
        files = {"file":(file.name,file, file.type)}
        response = requests.post("http://localhost:8001/upload_doc", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"文件加载失败。ERROR：{response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"加载文件时出现错误：{str(e)}")
        return None

#文件列表展示,返回列表，若无东西，即返回空列表
def list_documents():
    try:
        response = requests.get("http://localhost:8001/list_docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"文件列表获取失败，ERROR: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"文件列表获取发生错误{str(e)}")
        return []

#文件删除
def delete_document(file_id):
    print("删除文件")
    #请求头，希望用户端返回的是json，以及自己的输入格式为json
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {"file_id": file_id}
    try:
        response = requests.post("http://localhost:8001/delete_doc", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"删除文件失败,ERROR:{response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"删除文件时发生错误:{str(e)}")
        return None

#聊天函数
def get_api_response(question,session_id,api_key):
    print("推理中")
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    print(question)
    print(session_id)
    print(api_key)
    data = {"question":question,"api_key":api_key}
    if session_id:
        data["session_id"] = session_id
    try:
        response = requests.post("http://localhost:8001/chat", headers=headers, json=data)
        if response.status_code == 200:#响应成功
            return response.json()
        else:
            st.error(f"api 请求失败{response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"请求出现错误{str(e)}")
        return None


#获取数据库的image字段
def images_document(file_id):
    print("找ocr")
    headers ={
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post("http://localhost:8001/image_ocr", headers=headers, json={"file_id": file_id} )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"ocr 请求失败{response.status_code} - {response.text}")
            return {"images_data": []}
    except Exception as e:
        st.error(f"图片ocr出现错误{str(e)}")
        return {"images_data": []}

