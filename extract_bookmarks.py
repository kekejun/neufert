import PyPDF2

def extract_bookmarks_to_md(pdf_path, output_md_path):
   def get_bookmark_level(bookmark, _pdf):
       if isinstance(bookmark, list):
           return [get_bookmark_level(b, _pdf) for b in bookmark]
       
       page_num = _pdf.get_destination_page_number(bookmark) + 1
       title = bookmark.title.strip('\r')
       return {'title': title, 'page': page_num}

   with open(pdf_path, 'rb') as file:
       pdf = PyPDF2.PdfReader(file)
       outlines = pdf.outline
       
       structure = get_bookmark_level(outlines, pdf)
       
       with open(output_md_path, 'w', encoding='utf-8') as md_file:
           def write_level(items, level=1):
               for item in items:
                   if isinstance(item, list):
                       write_level(item, level + 1)
                   else:
                       md_file.write(f"{'#' * level} {item['title']} {item['page']}\n")

           write_level(structure)

extract_bookmarks_to_md('./pdf/Neufert-4th-edition.pdf', 'neufert_chapters.md')