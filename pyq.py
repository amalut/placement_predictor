import os

# Function to get a list of available papers
def get_paper_list():
    papers_dir = 'papers/'
    papers = []
    for filename in os.listdir(papers_dir):
        if filename.endswith('.pdf'):
            papers.append({'name': filename[:-4], 'filename': filename})
    return papers


