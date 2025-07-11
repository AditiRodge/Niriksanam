from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory
import os
from main import process

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fileUpload')
def fileUpload():
    return render_template('fileupload.html')

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/faqs')
def faqs():
    return render_template('FAQs.html')

@app.route('/result')
def result():
    score = request.args.get('score', "No score provided")
    filename = request.args.get('filename', None)
    download_link = None
    pdf_link = None

    if filename:
        download_link = url_for('download_file', filename=filename)
        pdf_link = url_for('serve_pdf', filename=filename)

    print("Score =", score)
    print("Filename =", filename)
    print("Download Link =", download_link)
    print("PDF Link =", pdf_link)  

    return render_template('result.html', score=score, download_link=download_link, pdf_link=pdf_link)

@app.route('/Output/<filename>')
def serve_pdf(filename):
    return send_from_directory('Output', filename, mimetype='application/pdf')

@app.route('/download/<filename>')
def download_file(filename):
    output_path = os.path.join('Output', filename)  

    if not os.path.exists(output_path):
        return "Error: File not found!", 404

    return send_file(output_path, as_attachment=True, mimetype='application/pdf')

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    title = request.form.get('title')
    text_input = request.form.get('text')
    uploaded_file = request.files.get('file')

    #print(title)
    #print(text_input)
    if not title:
        return "Error: Title is required", 400

    if not text_input and not uploaded_file:
        return "Error: No input provided (file or text required)", 400

    file_path = None
    if uploaded_file and uploaded_file.filename != '':
        file_path = os.path.join('Uploads', uploaded_file.filename)
        uploaded_file.save(file_path)

    try:
        if file_path:  
            output_path, plagiarism_score = process(title=title, path=file_path)
        elif text_input:  
            output_path, plagiarism_score = process(title=title, text=text_input ,path=None)
        else:
            return "Error: Invalid input", 400
    except Exception as e:
        return f"Error processing input: {str(e)}", 500

    filename = os.path.basename(output_path)
    return redirect(url_for('result', score=plagiarism_score, filename=filename))

if __name__ == '__main__':
    app.run(debug=True)
