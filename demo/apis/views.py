from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PDFFile
from .serializers import PDFFileSerializer

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .models import QuestionAnswer 
from .serializers import QuestionAnswerSerializer,PDFFileSerializer
from models.pdfanalyser.pdf import create_vector_database, ChatGroq, Chroma, groq_api_key, PromptTemplate, RetrievalQA
from django.shortcuts import render
from rest_framework import permissions
import os
from django.conf import settings
from django.http import JsonResponse

def get_question_answers(request):
    # Assuming you want to fetch all QuestionAnswer objects
    qas = QuestionAnswer.objects.all()
    serializer = QuestionAnswerSerializer(qas, many=True)
    return JsonResponse(serializer.data, safe=False)



custom_prompt_template = """Use the following pieces of information to answer questions of the user.

# Context: {context}
# Question: {question}

# Only return the helpful content below and nothing else.
# Helpful answer:
# """

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

lines=''

class PDFFileViewSet(viewsets.ModelViewSet):
    queryset = PDFFile.objects.all()
    serializer_class = PDFFileSerializer
    permission_classes = (permissions.AllowAny,)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            # Handle PDF File creation and processing
            pdf_file = serializer.validated_data['file']
            file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', pdf_file.name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)

            # Process the PDF with the machine learning model
            vectorstore, embed_model = create_vector_database(file_path)
            chat_model = ChatGroq(
                temperature=0.0,
                model_name="mixtral-8x7b-32768",
                api_key=groq_api_key
            )

            vectorstore = Chroma(
                embedding_function=embed_model,
                persist_directory="chroma_db_llamaparse1",
                collection_name="rag"
            )
            retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

            custom_prompt_template = """
                Use the following pieces of information to answer questions of the user.
                Context: {context}
                Question: {question}
                Only return the helpful content below and nothing else.
                Helpful answer:
            """
            prompt = set_custom_prompt()

            qa = RetrievalQA.from_chain_type(
                llm=chat_model,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )

            response = qa.invoke({
                "query": "Generate 20 technical interview questions and answers suitable for a candidate with 0 years of experience "
                         "in the field, based on the provided content. Include a mix of basic, intermediate, tricky, and logical "
                         "questions. Follow a coherent order in the question formation. Provide the source documents."
            })

            # Save questions and answers to the database
            QuestionAnswer.objects.all().delete()  # Clear existing entries
            lines = response['result'].split("\n")
            
            for line in lines:
                question_part = ''
                answer_part = ''
                if 'Answer:' in line:
                    answer_part = line.split('Answer:')[1].strip()
                if 'Answer' not in line:
                    question_part = line.strip()
                if question_part or answer_part:
                    qa_entry = QuestionAnswer(question=question_part, answer=answer_part)
                    qa_entry.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        List all the QuestionAnswer items.
        """
        qa_items = QuestionAnswer.objects.all()
        serializer = QuestionAnswerSerializer(qa_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
