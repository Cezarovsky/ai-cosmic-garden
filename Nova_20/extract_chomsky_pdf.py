#!/usr/bin/env python3
"""
Extragere text din PDF Chomsky "Language and Mind" → txt file
"""
import sys
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    print("❌ Instalează: pip install PyPDF2")
    sys.exit(1)

# Paths
PDF_PATH = Path("/Users/cezartipa/Documents/ai-cosmic-garden/Nova_20/Nova Carti/Language and Mind.pdf")
OUTPUT_PATH = Path("/Users/cezartipa/Documents/ai-cosmic-garden/Nova_20/corpus/chomsky_language_and_mind.txt")

def extract_pdf_text():
    """Extract text from Chomsky PDF"""
    print(f"📖 Extragere text din: {PDF_PATH.name}")
    
    if not PDF_PATH.exists():
        print(f"❌ PDF nu există: {PDF_PATH}")
        sys.exit(1)
    
    text_lines = []
    
    with open(PDF_PATH, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        print(f"   Total pagini: {total_pages}")
        
        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            if text.strip():
                text_lines.append(f"\n--- Page {page_num + 1} ---\n")
                text_lines.append(text)
            
            if (page_num + 1) % 10 == 0:
                print(f"   Procesat: {page_num + 1}/{total_pages}")
    
    # Combine și salvează
    full_text = '\n'.join(text_lines)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(full_text, encoding='utf-8')
    
    lines_count = len(full_text.split('\n'))
    char_count = len(full_text)
    
    print(f"\n✅ Text extras cu succes!")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Linii: {lines_count:,}")
    print(f"   Caractere: {char_count:,}")

if __name__ == '__main__':
    try:
        extract_pdf_text()
    except Exception as e:
        print(f"❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
