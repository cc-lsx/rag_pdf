import base64
import io
import os

import easyocr
import pytesseract
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pdf2image import convert_from_path
from pix2text import MathFormulaDetector, LatexOCR
from langchain.docstore.document import Document


def encode_image(img: np.ndarray) -> str:
    """
    将 np.ndarray 图片转为 base64 字符串
    """
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    if img.ndim == 2:  # 灰度
        pil_img = Image.fromarray(img)
    elif img.ndim == 3 and img.shape[2] == 3:  # 彩色 BGR -> RGB
        pil_img = Image.fromarray(img[..., ::-1])
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()
#pdf解析
def pdf_formula_to_documents(file_path, device='cuda'):
    """
    返回 Document 列表和图片列表，每页文本对应一个 Document，图片按页组织
    file_path: 已经存在的 PDF 文件路径
    """
    documents = []
    images = []
    filename = os.path.basename(file_path).lower()
    if filename.endswith(".pdf"):
        text_lists, page_images_list = pdf_formula_to_textlist(file_path, device=device)
        for page_idx in range(len(text_lists)):
            page_text_list = text_lists[page_idx]
            page_image = page_images_list[page_idx]
            page_text = "\n".join(page_text_list)
            doc = Document(
                page_content=page_text,
                metadata={"page": page_idx + 1, "source": filename}
            )
            documents.append(doc)
            images.append(page_image)
    return documents, images


#识别pdf，并输出图片以及识别的文档
def pdf_formula_to_textlist(pdf_path, device='cuda'):
    """
    处理 PDF，返回：
    - all_text_lists: 每页文本列表（双栏按左列->右列阅读顺序）
    - all_images: 每页原始图片（仅框出公式，不修改）
    """
    print("处理 PDF:", pdf_path)
    pages = convert_from_path(pdf_path, dpi=200)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\lsx\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    det = MathFormulaDetector(device=device) #公式检测
    ocr = LatexOCR(device=device)   #公式识别
    easy_reader = easyocr.Reader(['en'])
    all_text_lists = []
    all_images = []

    for page_idx, page_image in enumerate(pages):
        print(f"处理第 {page_idx + 1} 页...")
        page_w, page_h = page_image.size

        # 原始图片（仅框出公式）
        original_image = page_image.convert('RGB')
        draw_original = ImageDraw.Draw(original_image)

        # 用于处理（覆盖公式、加标签）
        processed_image = page_image.convert('RGB')
        draw_processed = ImageDraw.Draw(processed_image)

        # 1️⃣ 公式检测与 LaTeX 识别
        outs = det.detect(original_image)
        page_formula_results = []

        for i, formula in enumerate(outs, start=1):
            box = formula['box']
            x1, y1 = int(np.min(box[:, 0])), int(np.min(box[:, 1]))
            x2, y2 = int(np.max(box[:, 0])), int(np.max(box[:, 1]))

            # 原始图片仅框出公式
            draw_original.rectangle([x1, y1, x2, y2], outline='red', width=2)

            # processed_image 上操作：裁切公式识别
            cropped = processed_image.crop((x1, y1, x2, y2))
            latex_text = ocr.recognize(cropped)
            page_formula_results.append(latex_text["text"])

            # 覆盖公式 + 添加标签
            draw_processed.rectangle([x1, y1, x2, y2], outline='red', width=2)
            draw_processed.rectangle([x1, y1, x2, y2], fill='white')

            font_size = max(10, min(40, int((y2 - y1) * 0.5)))
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            text_label = f"llm{i}"  # 保留原有标签
            bbox = draw_processed.textbbox((0, 0), text_label, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_x = x1 + (x2 - x1 - text_w) / 2
            text_y = y1 + (y2 - y1 - text_h) / 2
            draw_processed.text((text_x, text_y), text_label, fill='black', font=font)

        # 2️⃣ easyocr 识别 processed_image
        easyocr_results = easy_reader.readtext(np.array(processed_image))

        # 构建 OCR 行信息
        ocr_lines = []
        for item in easyocr_results:
            bbox, text, prob = item
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            x_center = float(np.mean(xs))
            y_top = float(np.min(ys))
            ocr_lines.append({'text': text, 'x_center': x_center, 'y_top': y_top})

        # 如果没有 OCR 结果
        if len(ocr_lines) == 0:
            all_text_lists.append([])
            all_images.append(np.array(original_image))
            continue

        # 3️⃣ 自动分列
        if len(ocr_lines) > 1:
            sorted_x = sorted([line['x_center'] for line in ocr_lines])
            gaps = [sorted_x[i+1]-sorted_x[i] for i in range(len(sorted_x)-1)]
            max_gap_idx = np.argmax(gaps)
            split_x = sorted_x[max_gap_idx]
            for line in ocr_lines:
                line['col_id'] = 0 if line['x_center'] <= split_x else 1
        else:
            for line in ocr_lines:
                line['col_id'] = 0

        # 4️⃣ 按列顺序（左->右）和列内 y_top 排序
        cols = sorted(list(set(line['col_id'] for line in ocr_lines)))
        ordered_texts = []
        for c in cols:
            lines_in_col = [l for l in ocr_lines if l['col_id'] == c]
            lines_in_col_sorted = sorted(lines_in_col, key=lambda l: l['y_top'])
            ordered_texts.extend([l['text'] for l in lines_in_col_sorted])

        # 5️⃣ 替换公式标签
        for idx, latex in enumerate(page_formula_results, start=1):
            ordered_texts = [line.replace(f"lm{idx}", latex) for line in ordered_texts]

        # 保存结果
        all_text_lists.append(ordered_texts)
        all_images.append(np.array(original_image))  # 仅框出公式的图片

    return all_text_lists, all_images