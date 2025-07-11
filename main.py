import Functions as fun
import multiprocessing as mp
import os

def process(title,path, text=None):
    input_content = ""

    if text:  
        input_content = text  
    elif path:  
        if path.endswith('.pdf'):
            input_content = fun.extract_text_from_pdf(path)
        elif path.endswith('.txt'):
            input_content = fun.extract_text_from_txt_file(path)
        elif path.endswith('.docx'):
            input_content = fun.extract_text_from_word_file(path)
        elif path.endswith('.doc'):
            input_content = fun.extract_text_from_doc_file(path)
        else:
            raise ValueError(f"Unsupported file format: {path}")  
    else:
        raise ValueError("No valid input provided")
            
    prepocessed_text = fun.preprocessing_text(input_content)
    keywords = fun.keyword_extraction(prepocessed_text)
    search_query = " ".join(keywords)
    urls = fun.google_search(title+search_query)
    length = min(20,len(urls))
    urls = urls[:length]
    with mp.Manager() as manager:
        urls_content = manager.dict()
        dic = manager.dict()       # dic =   {line_index:[line,URL]}
        p1 = mp.Process(target=fun.extract_text_from_url,args=(urls,urls_content))  
        p2 = mp.Process(target=fun.check_plagiarism, args=(input_content,urls_content,dic))
        p1.start()   
        p1.join()
        p2.start()
        p2.join()

        content = input_content
        words = content.split(" ")
        input_word_len = len(words)
        plagiarized_word_len=0
        text_lines = fun.sent_tokenize(input_content)
        site_wise_perc={}
        site_colors={}
        text_colors={}
        colors=[(1,0.8,0.8),(0.8,1,0.8),(0.8,0.8,1),(0.8,1,1),(1,0.8,1),(0.95,0.95,0.95),(0.9,0.7,0.7),(0.9,0.9,0.7),(0.7,0.9,0.7),(0.9,0.7,0.9), 
            (0.7,0.9,0.9),(0.7,0.7,0.9),(1,0.85,0.7),(1,0.9,0.9),(1,1,0.8)]
        text_color=[(1,0,0),(0,1,0),(0,0,1),(0,1,1),(1,0,1),(0.75,0.75,0.75),(0.5,0,0),(0.5,0.5,0),(0,0.5,0),(0.5,0,0.5),(0,0.5,0.5),(0,0,0.5)
                    ,(1,0.65,0),(1,0.75,0.8),(1,1,0)]
        c=0
        for key,value in dic.items():
            words_in_line=value[0].split(" ")
            if value[1] in site_wise_perc:
                site_wise_perc[value[1]]=site_wise_perc[value[1]]+len(words_in_line)
            else:
                site_wise_perc[value[1]]=len(words_in_line)
                site_colors[value[1]]=colors[c]
                text_colors[value[1]]=text_color[c]
                c=c+1
            plagiarized_word_len+=len(words_in_line)

        site_perc="Sources of Plagiarism\n\n"
        for key in site_wise_perc:
            if input_word_len == 0:
               site_wise_perc[key] = 0
            else: 
                site_wise_perc[key]=round((site_wise_perc[key]/input_word_len)*100,2)
        total_plag=0
        if len(text_lines)==0:
            total_plag=0
        else:
            total_plag=round((plagiarized_word_len/input_word_len)*100,2)
            
        total_perc="\nTotal Plagiarism: "+(str)(total_plag)

        plagiarized_text_list = {}    # {line:url}
        for key, value in dic.items():
            plagiarized_text_list[value[0]]=value[1]
        output_filename = f"{title}_report.pdf"
        output_pdf_path = os.path.join("Output", output_filename)
        footer_text= None
        if path:
            input_content = None
        fun.highlight_text_in_pdf(input_content,path, plagiarized_text_list, output_pdf_path,site_wise_perc,footer_text,site_colors,total_perc,text_colors)
        plagiarism_score = total_plag

    return output_pdf_path,plagiarism_score
                                           



