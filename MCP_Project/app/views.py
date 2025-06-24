from django.shortcuts import render
import os
from django.conf import settings
from PyPDF2 import PdfReader
import ollama

# PDF read
def read_pdf_and_split(file_path, chunk_size=500):
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
    return chunks

# LLM
def ask_llm(question, chunks):
    context = "\n\n".join(chunks[:5])
    prompt = f"""Answer the question based on the context below:\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"""
    response = ollama.chat(
        model='mistral',
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

# Index page rendering
def index(request):
    return render(request, 'app/index.html')

# PDF to ans and questions
def process_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        file_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        chunks = read_pdf_and_split(file_path)
        question = request.POST.get('question')
        answer = ask_llm(question, chunks)

        return render(request, 'app/index.html', {
            'answer': answer,
            'question': question,
        })
    return render(request, 'app/index.html', {'error': 'No file uploaded'})
