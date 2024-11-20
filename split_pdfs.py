import PyPDF2
import os
import re

def clean_filename(title):
    clean = ' '.join(word.capitalize() for word in title.split())
    return re.sub(r'[^\w\s-]', '', clean).strip().replace(' ', '-')

def get_bookmark_level(bookmark, _pdf):
    if isinstance(bookmark, list):
        return [get_bookmark_level(b, _pdf) for b in bookmark]
    
    page_num = _pdf.get_destination_page_number(bookmark)
    title = bookmark.title.strip('\r')
    return {'title': title, 'page': page_num}

def extract_chapters(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    chapter_info = []

    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        outlines = pdf.outline
        structure = get_bookmark_level(outlines, pdf)
        total_pages = len(pdf.pages)

        i = 0
        while i < len(structure):
            chapter = structure[i]
            if isinstance(chapter, list):
                i += 1
                continue

            next_start = total_pages
            j = i + 1
            while j < len(structure):
                next_item = structure[j]
                if not isinstance(next_item, list):
                    if isinstance(next_item, dict):
                        next_start = next_item['page']
                    break
                j += 1

            start_page = chapter['page']
            end_page = next_start
            
            chapter_pdf = PyPDF2.PdfWriter()
            for p in range(start_page, end_page):
                chapter_pdf.add_page(pdf.pages[p])
            
            # Add bookmarks for subchapters
            subchapters = []
            if i + 1 < len(structure) and isinstance(structure[i + 1], list):
                for sub in structure[i + 1]:
                    new_page = sub['page'] - start_page
                    subchapters.append({
                        'title': sub['title'],
                        'page': new_page + 1  # For display
                    })
                    # Add bookmark to PDF
                    chapter_pdf.add_outline_item(sub['title'], new_page)
                i += 2
            else:
                i += 1
            
            clean_title = clean_filename(chapter['title'])
            output_path = os.path.join(output_dir, f"{clean_title}.pdf")
            with open(output_path, 'wb') as output_file:
                chapter_pdf.write(output_file)
            
            chapter_info.append({
                'filename': clean_title,
                'title': chapter['title'],
                'subchapters': subchapters
            })
    
    return chapter_info

def create_chapter_index(chapter_info, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for chapter in chapter_info:
            f.write(f"- {chapter['filename']}\n")
            if chapter['subchapters']:
                for sub in chapter['subchapters']:
                    f.write(f"  - {sub['page']} {sub['title']}\n")

pdf_path = './pdf/Neufert-4th-edition.pdf'
output_dir = './chapters'
index_path = './chapters.md'

chapter_info = extract_chapters(pdf_path, output_dir)
create_chapter_index(chapter_info, index_path)