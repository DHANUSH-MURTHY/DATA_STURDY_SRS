import docx
import sys

def read_docx(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    file_path = r"d:\DATA_STURDY_2\Use Case 4 - Compete Analysis.docx"
    content = read_docx(file_path)
    # Write to file with utf-8 encoding
    with open(r"d:\DATA_STURDY_2\competitive-intelligence\doc_content_utf8.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("Done writing to doc_content_utf8.txt")
