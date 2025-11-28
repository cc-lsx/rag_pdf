##  PDF 多人在线文献阅读助手

一款基与MCP、langchain、streamlit、sqlite构建的pdf文献阅读助手，可以识别文献中的公式，将之识别为latex格式，并交给大模型处理。

## ✨ 特点

### pdf识别
- **可进行pdf的公式识别**: 使用 MathFormulaDetector 检测公式并通过 LatexOCR 识别为 LaTeX，同时在处理图像上覆盖公式并添加占位标签，再用 easyocr 识别整页文本，自动分栏排序后将公式占位符替换为真实公式，最终生成每页文本对应的 Document 对象并保留标记公式的图片，支持多页、多列 PDF，并可在 GPU 上加速处理。


### FastApi后端
- **使用FastApi编写后端** 使用FastApi编写、高性能、类型安全的接口，且基于异步的接口使得在进行多人对话交互时，加速处理速度。


### RAG检索
- **具有历史记忆的RAG** 构建历史记忆的rag，构建双提示词，使得在进行长对话时，有效减少模型的幻觉问题。



## 设置

### 需求
1. **API Keys** (您需要有Deepseek与高德mcp的API KEY):
    - **Deepseek API Key**: 可点击 [Deepseek Platform](https://platform.deepseek.com/api_keys)
    - **pytesseract.pytesseract.tesseract_cmd**: 该路径为默认为："C:\Users\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

2. **Python 3.11+**: 确保您的py版本在3.11+以上.
3. **若需要使用GPU版本的公式检测与识别，请确保Pytorch为2.4.0+cu118+以上**


### 安装

1. 克隆到本地:
   ```bash
   git clone https://github.com/cc-lsx/rag_pdf.git
   cd rag_pdf
   ```

2. 安装项目所需需求的包:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

1. Start the Streamlit app:
   ```bash
   cd APP
   streamlit streamlit_app.py
   ```
   ```bash
   cd API
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```
   


