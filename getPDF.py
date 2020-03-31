import os
import re
import requests
from datetime import datetime
from io import BytesIO
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

# https://ecourse2.ccu.edu.tw/mod/resource/view.php?id=28275


class PDF():
    def __init__(self):
        self.pdf_text = ''
        self.__fp = None
        self.key = [r'deadline.*\d', r'Due Date.*\d']
        self.format = [r'\d{2}.\d{2}', r'\d{4}.\d{2}.\d{2}']

    def path_pdf(self, file_path, file_name):
        self.path = file_path
        self.name = os.path.join(file_path, file_name)
        self.__fp = open(self.name, 'rb')
        self.read_pdf()

    def url_pdf(self, rb_file):
        self.__fp = BytesIO(rb_file)
        self.read_pdf()

    def read_pdf(self):
        self.pdf_text = ''
        parser = PDFParser(self.__fp)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize(' ')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        laparams.char_margin = 1.0
        laparams.word_margin = 1.0
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    self.pdf_text += lt_obj.get_text()
        self.__fp.close()

    def write_pdf_utf(self, file_name):
        with open(file_name, 'w', encoding= 'utf-8') as output:
            output.write(self.pdf_text + '\n')
            output.close()

    def find_deadline(self):
        for key in self.key:
            key_word = re.findall(key, self.pdf_text)
            if key_word:
                dead_line = key_word[0]
                break
        # print(dead_line)

        # to deal the format respectively
        if re.search(self.format[0], dead_line, re.IGNORECASE):
            tmp = re.search(self.format[0], dead_line, re.IGNORECASE).group()
            date = f'{datetime.now().year}/{tmp}'
        else:
            date = re.search(self.format[1], dead_line, re.IGNORECASE).group()

        time = re.search(r'\d{2}\:\d{2}', dead_line)

        # print(f'{date.group()} {time.group()}')

        return f'{date} {time.group()}'


if __name__ == '__main__':
   pdf_file = PDF()
   pdf_file.read_pdf()
   date = pdf_file.find_deadline()
   print(date)