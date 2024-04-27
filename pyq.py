from flask import Flask, render_template, send_file, abort
import os

app = Flask(__name__)

# Function to get a list of available papers
def get_paper_list():
    papers_dir = 'papers/'
    papers = []
    for filename in os.listdir(papers_dir):
        if filename.endswith('.pdf'):
            papers.append({'name': filename[:-4], 'filename': filename})
    return papers

# Route to display the list of papers
@app.route('/')
def index():
    papers = get_paper_list()
    return render_template('index.html', papers=papers)

# Route to download a paper
@app.route('/download/<filename>')
def download_paper(filename):
    papers_dir = 'papers/'
    if os.path.isfile(os.path.join(papers_dir, filename)):
        return send_file(os.path.join(papers_dir, filename), as_attachment=True)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
