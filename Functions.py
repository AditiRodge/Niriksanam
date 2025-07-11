import re
import fitz
import docx
import nltk
import requests
import numpy as np
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from bs4 import BeautifulSoup
from io import BytesIO
from bs4 import UnicodeDammit
from nltk.tokenize import sent_tokenize
from difflib import SequenceMatcher
import yake
import warnings
warnings.filterwarnings('ignore')
import tensorflow as tf
import logging
import os
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
tf.get_logger().setLevel('ERROR')
logging.getLogger('tensorflow').setLevel(logging.CRITICAL)
import tensorflow_hub as hub
from scipy.spatial.distance import cosine
import shutil
import win32com.client
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Loading USE 
def load_USE():
    try:
        embed=hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')
    except Exception as e:
        temp_dir = os.getenv('TMP') or os.getenv('TEMP') or '/tmp'
        tfhub_cache_dir = os.path.join(temp_dir, 'tfhub_modules')
        if os.path.exists(tfhub_cache_dir):
            shutil.rmtree(tfhub_cache_dir)
        embed = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')

    return embed

embed=load_USE()

# Text extraction from PDF
def extract_text_from_pdf(path):
    doc=fitz.open(path)
    noOfPages=doc.page_count
    text=""                                                                                 
    for i in range(0,noOfPages):
        text+=doc.load_page(i).get_text()
    return text

# Text extraction from Text File
def extract_text_from_txt_file(path):
    encodings = ['utf-8','latin-1','cp1252']
    for encoding in encodings:
        try:
            file=open(path,'r',encoding=encoding)
            return file.read()
        except UnicodeDecodeError:
            continue

# Text extraction from Word File
def extract_text_from_word_file(path):
    text=""
    doc=docx.Document(path)
    for para in doc.paragraphs:
        text+=(para.text)
    return text

# Preprocessing of text
def preprocessing_text(text):
    text=text.lower()                                                                   # Lower Case
    text=re.sub(r'<.*?>',' ',text)                                                      # Remove HTML tags
    text=re.sub(r'[^a-zA-Z]',' ',text)                                                  # Remove Special Char & Digits
    text=word_tokenize(text)                                                            # Tokenization(Separating the words by commas)
    stop_words=set(stopwords.words('english'))                                          # Total Stopwords in English=179                                
    text=[word for word in text if word not in stop_words]                              # Remove StopWords
    text=[word for word in text if len(word)>3]                                         # Remove words having len less than 3   
    text=' '.join(text)                                                                 # Converting list to string
    return text
# print(preprocessing_text(text))

# Keyword Extraction
def keyword_extraction(text):
    keyword_extractor=yake.KeywordExtractor(lan="en", n=1, dedupLim=0.9, top=20, features=None)
    keywords=keyword_extractor.extract_keywords(text)
    top_keywords=[]
    for word,score in keywords:
        top_keywords.append(word)
    return top_keywords

# Query Google
def google_search(search_query):
    API_KEY=open('API_KEY').read()
    SEARCH_ENGINE_ID=open('SEARCH_ENGINE_ID').read()
    url='https://www.googleapis.com/customsearch/v1'
    params={
        'q':search_query,
        'key':API_KEY,
        'cx':SEARCH_ENGINE_ID,
    }
    response=requests.get(url,params=params)
    results=response.json().get('items',[])
    urls=[]
    for result in results:
        urls.append(result['link'])
    return urls

# Extract text from URL
def extract_text_from_url(urls,urls_content):
    for url in urls:
        try:
            response=requests.get(url)
            soup=BeautifulSoup(UnicodeDammit(response.content, ["latin-1", "iso-8859-1", "windows-1251"]).unicode_markup,"html.parser")
            paragraphs=soup.find_all('p')
            all_paragraphs_text = "\n".join(p.get_text() for p in paragraphs)
            if response.status_code==200:
                html_content=response.text
                soup=BeautifulSoup(html_content,'html.parser')
                pdf_links=[]
                for link in soup.find_all('a'):
                    href=link.get('href')
                    if href and href.endswith('.pdf'):
                        pdf_links.append(href)
                if len(pdf_links)!=0:
                    all_paragraphs_text+=download_and_extract_pdf_text(pdf_links[:1])
                if "pdf" in url:
                    all_paragraphs_text+=download_and_extract_pdf_text(url)
            sentences = sent_tokenize(all_paragraphs_text)
            sentences = sentences[0:min(7000,len(sentences))]
            all_paragraphs_text = " ".join(sentences)
            urls_content[url]=all_paragraphs_text
        except Exception as e:
            urls_content[url]=""
    #print(urls_content)                                    


# Extract text from PDF 
def download_and_extract_pdf_text(url):
    try:
        response=requests.get(url)   
        if response.status_code==200:                                                               
            pdf_content=BytesIO(response.content)
            doc=fitz.open(stream=pdf_content,filetype="pdf")
            noOfPages=doc.page_count
            text="" 
            noOfPages=min(noOfPages,10)                                                                                
            for i in range(0,noOfPages):
                text+=doc.load_page(i).get_text()
            
            return text
        else:
            return " "
    except Exception as e:
        return " "

# SequenceMatcher for word-to-word plagiarsm detection
def get_similarity_ratio(line1,line2):
    return SequenceMatcher(None,line1,line2).ratio()

# # Getting score from SequenceMatcher for paraphrased or reworded plagiarsm detection
def get_use_embedding(text):
    return embed([text]).numpy()[0]

def check_plagiarism(text,urls_content,dic):
    text_lines=sent_tokenize(text)
    for url,site_content in urls_content.items():   
        if(len(site_content)==0):
            continue     
        site_lines=sent_tokenize(site_content)
        for i, line in enumerate(text_lines):
            if i in dic:
                continue
            embedding1 = get_use_embedding(line)
            for site_line in site_lines:
                seq_similarity = get_similarity_ratio(line.lower(), site_line.lower())
                embedding2 = get_use_embedding(site_line)
                use_similarity = 1 - cosine(embedding1, embedding2)                                      
                if seq_similarity>=0.75 or use_similarity>=0.5:                                   
                    words=line.split(" ")
                    if (len(words)>3):                             
                        dic[i] = [line,url,site_line]
                        # print("input:",line,"\nsite:",site_line,"\nUSE:",use_similarity,"SeqMatcher:",seq_similarity)

# Highlight text
def highlight_text_in_pdf(text,input_path,plagiarized_text_list, output_pdf_path,site_wise_perc,footer_text,site_colors,total,text_colors):
    pdf_document = fitz.open()
    text_content = ""

    if text:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "Output")
        temp = os.path.join(output_dir, "temp.pdf")
        pdf = SimpleDocTemplate(temp, pagesize=letter,
                                leftMargin=50, rightMargin=50,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "Helvetica"
        style.fontSize = 12
        style.leading = 16  
        style.alignment = 4  
        paragraphs = text.split("\n")
        elements = []

        for para in paragraphs:
            if para.strip():  
                elements.append(Paragraph(para, style))
                elements.append(Spacer(1, 12))  

        pdf.build(elements)
        pdf_document = fitz.open(temp)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
                
            for key in plagiarized_text_list:
                text_instances = page.search_for(key)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors({"stroke": site_colors[plagiarized_text_list[key]]})
                    highlight.update()
            width = page.rect.width
            height = page.rect.height
            footer_position = fitz.Point(72, height - 50)  
            footer_fontsize = 10
            footer_font = "helv"
            footer_color = (0.5, 0.5, 0.5)
            page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
        new_page = pdf_document.new_page()
        text_rect = fitz.Rect(72, 72, new_page.rect.width - 72, new_page.rect.height - 72)
        new_page.insert_textbox(text_rect,"Sources of Plagiarism\n\n",fontsize=14)
        i=3
        for key in site_wise_perc:
            position = fitz.Rect(72, 72+i*14, new_page.rect.width - 72, new_page.rect.height - 72)
            new_page.insert_textbox(position,key+" : "+(str)(site_wise_perc[key])+"%",fontsize=12,color=text_colors[key])
            i=i+2
        position = (72,72 + i * 14)
        new_page.insert_text(position,total,fontsize=12)
        width = new_page.rect.width
        height = new_page.rect.height
        footer_position = fitz.Point(72, height - 50)  
        footer_fontsize = 10
        footer_font = "helv"
        footer_color = (0.5, 0.5, 0.5)
        new_page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
        pdf_document.save(output_pdf_path, garbage=4, deflate=True)
        pdf_document.close()
        os.remove(temp)

    
    elif input_path.endswith(".pdf"):  
        pdf_document = fitz.open(input_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
            
            for key in plagiarized_text_list:
                text_instances = page.search_for(key)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors({"stroke": site_colors[plagiarized_text_list[key]]})
                    highlight.update()
            width = page.rect.width
            height = page.rect.height
            footer_position = fitz.Point(72, height - 50)  
            footer_fontsize = 10
            footer_font = "helv"
            footer_color = (0.5, 0.5, 0.5)
            page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
        new_page = pdf_document.new_page()
        text_rect = fitz.Rect(72, 72, new_page.rect.width - 72, new_page.rect.height - 72)
        new_page.insert_textbox(text_rect,"Sources of Plagiarism\n\n",fontsize=14)
        i=3
        for key in site_wise_perc:
            position = fitz.Rect(72, 72+i*14, new_page.rect.width - 72, new_page.rect.height - 72)
            new_page.insert_textbox(position,key+" : "+(str)(site_wise_perc[key])+"%",fontsize=12,color=text_colors[key])
            i=i+2
        position = (72,72 + i * 14)
        new_page.insert_text(position,total,fontsize=12)
        width = new_page.rect.width
        height = new_page.rect.height
        footer_position = fitz.Point(72, height - 50)  
        footer_fontsize = 10
        footer_font = "helv"
        footer_color = (0.5, 0.5, 0.5)
        new_page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
        pdf_document.save(output_pdf_path, garbage=4, deflate=True)
        pdf_document.close()

    
    elif input_path.endswith(".docx"):  
        # input_path=os.path.join(r"C:\Users\HP\OneDrive\Desktop\FinalYearProject\Integration",input_path)
        #input_path=r("C:\Users\HP\OneDrive\Desktop\FinalYearProject\Integration"+input_path)
        # print(input_path)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(base_dir, input_path)
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False  # Run Word in the background
            doc = word.Documents.Open(input_path)
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(base_dir, "Output")
            temp = os.path.join(output_dir, "temp.pdf")
            doc.SaveAs(temp, FileFormat=17)
            doc.Close()
            word.Quit()
            pdf_document = fitz.open(temp)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text = page.get_text("text")
                
                for key in plagiarized_text_list:
                    text_instances = page.search_for(key)
                    for inst in text_instances:
                        highlight = page.add_highlight_annot(inst)
                        highlight.set_colors({"stroke": site_colors[plagiarized_text_list[key]]})
                        highlight.update()
                width = page.rect.width
                height = page.rect.height
                footer_position = fitz.Point(72, height - 50)  
                footer_fontsize = 10
                footer_font = "helv"
                footer_color = (0.5, 0.5, 0.5)
                page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
            new_page = pdf_document.new_page()
            text_rect = fitz.Rect(72, 72, new_page.rect.width - 72, new_page.rect.height - 72)
            new_page.insert_textbox(text_rect,"Sources of Plagiarism\n\n",fontsize=14)
            i=3
            for key in site_wise_perc:
                position = fitz.Rect(72, 72+i*14, new_page.rect.width - 72, new_page.rect.height - 72)
                new_page.insert_textbox(position,key+" : "+(str)(site_wise_perc[key])+"%",fontsize=12,color=text_colors[key])
                i=i+2
            position = (72,72 + i * 14)
            new_page.insert_text(position,total,fontsize=12)
            width = new_page.rect.width
            height = new_page.rect.height
            footer_position = fitz.Point(72, height - 50)  
            footer_fontsize = 10
            footer_font = "helv"
            footer_color = (0.5, 0.5, 0.5)
            new_page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
            pdf_document.save(output_pdf_path, garbage=4, deflate=True)
            pdf_document.close()
            os.remove(temp)

        except Exception as e:
            print(f"Error: {e}")
    
    elif input_path.endswith(".txt"):  
        with open(input_path, "r", encoding="utf-8") as file:
            text = file.read()  

        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "Output")
        temp = os.path.join(output_dir, "temp.pdf")
        pdf = SimpleDocTemplate(temp, pagesize=letter,
                                leftMargin=50, rightMargin=50,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "Helvetica"
        style.fontSize = 12
        style.leading = 16  
        style.alignment = 4  
        paragraphs = text.split("\n")
        elements = []

        for para in paragraphs:
            if para.strip():  
                elements.append(Paragraph(para, style))
                elements.append(Spacer(1, 12))  

        # Build PDF
        pdf.build(elements)
        pdf_document = fitz.open(temp)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
                
            for key in plagiarized_text_list:
                text_instances = page.search_for(key)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors({"stroke": site_colors[plagiarized_text_list[key]]})
                    highlight.update()
            width = page.rect.width
            height = page.rect.height
            footer_position = fitz.Point(72, height - 50)  
            footer_fontsize = 10
            footer_font = "helv"
            footer_color = (0.5, 0.5, 0.5)
            page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
        new_page = pdf_document.new_page()
        text_rect = fitz.Rect(72, 72, new_page.rect.width - 72, new_page.rect.height - 72)
        new_page.insert_textbox(text_rect,"Sources of Plagiarism\n\n",fontsize=14)
        i=3
        for key in site_wise_perc:
            position = fitz.Rect(72, 72+i*14, new_page.rect.width - 72, new_page.rect.height - 72)
            new_page.insert_textbox(position,key+" : "+(str)(site_wise_perc[key])+"%",fontsize=12,color=text_colors[key])
            i=i+2
        position = (72,72 + i * 14)
        new_page.insert_text(position,total,fontsize=12)
        width = new_page.rect.width
        height = new_page.rect.height
        footer_position = fitz.Point(72, height - 50)  
        footer_fontsize = 10
        footer_font = "helv"
        footer_color = (0.5, 0.5, 0.5)
        new_page.insert_text(footer_position, footer_text, fontsize=footer_fontsize, fontname=footer_font, color=footer_color)
        pdf_document.save(output_pdf_path, garbage=4, deflate=True)
        pdf_document.close()
        os.remove(temp)

    
        
    
    