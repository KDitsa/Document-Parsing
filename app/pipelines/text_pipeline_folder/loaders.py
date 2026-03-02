import os
import pdfplumber
import json
import uuid
from docx2pdf import convert
from pathlib import Path
from .DocumentBlock import DocumentBlock
import logging

logging.basicConfig(level=logging.INFO)

# ---------------- Utility ----------------
def generate_id():
    return str(uuid.uuid4())

# ------------- Table to HTML -------------  
def table_to_html(table_data):
    html = "<table border=\"1\">"

    for row in table_data[0:]:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table>"
    return html

# ---------------- PDF ----------------
def load_pdf(path, image_dir="pdf_images", paragraph_thresh=3):
    blocks = []
    base_dir = Path(__file__).resolve().parent
    image_dir = base_dir / image_dir
    image_dir.mkdir(exist_ok=True, parents=True)

    try:
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_blocks = []

                # --- Tables ---
                table_bboxes = []
                for tbl in page.find_tables():
                    table_bboxes.append(tbl.bbox)
                    table_html_data = []
                    try:
                        table_data = tbl.extract()
                        table_html_data = table_to_html(table_data)
                        logging.info(table_data)
                        logging.info(table_html_data)
                    except:
                        table_html_data = ""
                        
                    page_blocks.append(DocumentBlock(
                        generate_id(),
                        "table",
                        table_html_data,
                        page_number=page_num,
                        bbox=tbl.bbox
                    ))
    

                # --- Text paragraphs ---
                words = page.extract_words(use_text_flow=True) or []
                def intersects(box1, box2):
                    return not (
                        box1[2] < box2[0] or
                        box1[0] > box2[2] or
                        box1[3] < box2[1] or
                        box1[1] > box2[3]
                    )
                current_para = []
                inside_table = False

                for w in words:
                    word_bbox = (w['x0'], w['top'], w['x1'], w['bottom'])
                    inside_table = False
                    for tb in table_bboxes:
                        if intersects(word_bbox, tb):
                            inside_table = True
                            break
                    
                    if inside_table:
                        if current_para:
                            left = min(word['x0'] for word in current_para)
                            right = max(word['x1'] for word in current_para)
                            top = min(word['top'] for word in current_para)
                            bottom = max(word['bottom'] for word in current_para)
                            para_text = " ".join(word['text'] for word in current_para)
        
                            page_blocks.append(DocumentBlock(
                                generate_id(),
                                "text",
                                para_text,
                                page_number=page_num,
                                bbox=[left, top, right, bottom]
                            ))
                            current_para = []
                        continue
                    
                    current_para.append(w)
    
                if current_para:
                    left = min(word['x0'] for word in current_para)
                    right = max(word['x1'] for word in current_para)
                    top = min(word['top'] for word in current_para)
                    bottom = max(word['bottom'] for word in current_para)
                    para_text = " ".join(word['text'] for word in current_para)
    
                    page_blocks.append(DocumentBlock(
                        generate_id(),
                        "text",
                        para_text,
                        page_number=page_num,
                        bbox=[left, top, right, bottom]
                    ))
    
                # --- Images ---
                for img_idx, img in enumerate(page.images):
                    try:
                        bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                        image_path = image_dir / f"{path.stem}{page_num}_{img_idx}.png"
                        page.crop(bbox).to_image(resolution=150).save(image_path)
    
                        page_blocks.append(DocumentBlock(
                            generate_id(),
                            "image",
                            str(image_path.resolve()),
                            page_number=page_num,
                            bbox=[img['x0'], img['top'], img['x1'], img['bottom']]
                        ))
                    except Exception as e:
                        logging.warning(f"Failed to save image on page {page_num}: {e}")
    
                # --- Sort blocks by vertical position ---
                page_blocks.sort(key=lambda b: b.bbox[1] if b.bbox else float('inf'))
                blocks.extend(page_blocks)
    
        return blocks
        
    except Exception as e:
        logging.error(f"Failed to load pdf file '{path}': {e}")
        return []

def convert_docx_to_pdf(docx_path: str, output_dir: str = "docx2pdf") -> Path:
    """
    Converts DOCX to PDF using Microsoft Word engine.
    Returns path to generated PDF.
    """
    docx_path = Path(docx_path)
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    pdf_path = output_dir / f"{docx_path.stem}.pdf"

    try:
        convert(str(docx_path), str(pdf_path))
        logging.info(f"Converted DOCX to PDF: {pdf_path}")
        return pdf_path
    except Exception as e:
        logging.error(f"DOCX to PDF conversion failed: {e}")
        return None
        
"""
# ---------------- DOCX ----------------
def load_docx(path, image_dir="docx_images"):
    blocks = []
    base_dir = Path(__file__).resolve().parent
    image_dir = base_dir / image_dir
    image_dir.mkdir(exist_ok=True, parents=True)
    
    try:
        doc = Document(path)
    
        position_counter = 0
    
        # --- Text paragraphs ---
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                blocks.append(DocumentBlock(
                    generate_id(),
                    "text",
                    text,
                    page_number=1,
                    bbox=[0, position_counter, 1000, position_counter + 10]
                ))
                position_counter += 10
    
        # --- Tables ---
        table_html_data = []
        for table in doc.tables:
            table_data = []
            
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]  # clean each cell text
                table_data.append(row_data)
                
            if(table_data):
                table_html_data = table_to_html(table_data)
            
            blocks.append(DocumentBlock(
                generate_id(),
                "table",
                table_html_data,
                page_number=1,
                bbox=[0, position_counter, 1000, position_counter + len(table.rows) * 2]
            ))
            position_counter += len(table.rows) * 2
    
        # --- Images ---
        for i, rel_id in enumerate(doc.part._rels):
            rel = doc.part._rels[rel_id]
            if rel.reltype == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image":
                try:
                    img = rel.target_part.blob
                    img_name = image_dir / f"{i}.png"
                    with open(img_name, "wb") as f:
                        f.write(img)
    
                    blocks.append(DocumentBlock(
                        generate_id(),
                        "image",
                        str(img_name.resolve()),
                        page_number=1,
                        bbox=[0, position_counter, 1000, position_counter + 20]
                    ))
                    position_counter += 20
                except Exception as e:
                    logging.warning(f"Failed to save image from DOCX: {e}")
    
        # --- Sort by vertical position ---
        blocks.sort(key=lambda b: b.bbox[1] if b.bbox else float('inf'))
        return blocks
    except Exception as e:
        logging.error(f"Failed to load docx file '{path}': {e}")
        return []
"""
# ---------------- Text ----------------
def load_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Treat as single block with approximate bbox
        return [DocumentBlock(generate_id(), "text", content, page_number=1, bbox=[0,0,1000,10])]
    except Exception as e:
        logging.error(f"Failed to load text file '{path}': {e}")
        return []
