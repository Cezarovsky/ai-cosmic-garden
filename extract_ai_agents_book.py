#!/usr/bin/env python3
"""Extract full text from AI Agents in Action PDF"""

import PyPDF2
import sys

pdf_path = '/Users/cezartipa/Downloads/Nova Carti/AI_Agents_in_Action.pdf'
output_path = 'AI_Agents_in_Action_full.txt'

print(f"📚 Reading: {pdf_path}")

try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        print(f"Total pages: {num_pages}")
        print("Extracting text...")
        
        all_text = []
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            all_text.append(f"\n{'='*80}\nPAGE {i+1}/{num_pages}\n{'='*80}\n{text}")
            
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i+1}/{num_pages} pages")
        
        # Save to file
        print(f"\n💾 Saving to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write('\n'.join(all_text))
        
        total_chars = sum(len(t) for t in all_text)
        total_words = sum(len(t.split()) for t in all_text)
        
        print(f"\n✅ Extraction complete!")
        print(f"   Pages: {num_pages}")
        print(f"   Characters: {total_chars:,}")
        print(f"   Words (approx): {total_words:,}")
        print(f"   Output file: {output_path}")
        
except FileNotFoundError:
    print(f"❌ Error: PDF file not found at {pdf_path}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
