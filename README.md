Project Title
Nirikṣaṇam: AI-Driven Plagiarism Detection – Empowering Academic Integrity

Overview:
Nirikṣaṇam is an advanced AI-powered plagiarism detection system designed to ensure originality and integrity in academic and professional writing. It integrates Natural Language Processing (NLP), web scraping, keyword extraction, and deep text similarity analysis to detect both direct and paraphrased content. With a Flask-based web interface, users can upload documents, analyze them for plagiarism, and download a detailed report in PDF format.

Installation & Setup:
1. Download the Project Folder
Ensure you have the project folder on your local system. No GitHub repository is required.

2. Install Python (if not installed)
Ensure Python 3.8+ is installed. You can check by running:
python --version
If not installed, download it from python.org.

3. Install Required Libraries
Navigate to the project directory and run:
pip install -r requirements.txt
This will automatically install all the necessary dependencies.

4. Run NLTK Resource Script (Mandatory)
To ensure proper functioning of text processing features, run the nltk_resources.py script:
python nltk_resources.py

Execution Steps:
1. Run the Flask Web Application
Inside the project folder, execute:
python app.py
This will start the Flask web server. You should see output like:
 Running on http://127.0.0.1:5000/

2. Open the Web Interface
Go to any browser and enter:
http://127.0.0.1:5000/
This will open the Nirikṣaṇam UI, Click on Detect button to move on Main Page.

3. Upload and Analyze a Document
Enter the title (mandatory).
Enter the text OR navigate to File Upload.
Upload a document (.txt, .pdf, .docx).
Click on Check Plagiarism.
The system will analyze the document. This step may take some time, depending on file size.

4. Download Plagiarism Report
Once the analysis is complete:
The result page will show the plagiarism report along with a pie chart.
You can download a detailed PDF report highlighting plagiarized content and source references.

Please consider following points while execution:
1. High-speed internet is recommended for better web scraping and similarity analysis performance.
2. Execution time depends on file size. Larger files may take longer to process.