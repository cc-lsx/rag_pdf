import pickle
import sqlite3

import numpy as np

DB_NAME = "rag_app.db"

#定义链接函数
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

#创建图片表
def create_document_store():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS document_store
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     filename TEXT UNIQUE,
                     images_data BLOB,
                     upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def insert_document_record(filename,images):
    conn = get_db_connection()
    images_blob = pickle.dumps(images)#序列化图片列表
    cursor = conn.cursor()
    cursor.execute('INSERT INTO document_store (filename,images_data) VALUES (?,?)', (filename,images_blob))
    file_id = cursor.lastrowid
    conn.commit()
    print("图片插入数据库成功！")
    conn.close()
    return file_id

#获取文档列表函数
def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id,filename,upload_timestamp FROM document_store ORDER BY upload_timestamp DESC') #按时间顺序的降序排列
    documents = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in documents]

def delete_document_db(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM document_store WHERE id=?', (file_id,))
    conn.commit()
    conn.close()
    return True


#创建历史对话表
def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     user_query TEXT,
                     gpt_response TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

#获取历史对话消息
def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages

#插入对话记录
def insert_application_logs(session_id, user_query, gpt_response):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO application_logs (session_id, user_query, gpt_response) VALUES (?,?,?)",(session_id,user_query,gpt_response))
    conn.commit()
    conn.close()

#获取图像以及其他
def image_list(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT images_data FROM document_store WHERE id=?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    blob_data = row[0]
    images = pickle.loads(blob_data)
    if isinstance(images, np.ndarray):
        images = [images]
    return images




create_document_store()
create_application_logs()