from django.db import models

class PDFFile(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class QuestionAnswer(models.Model):
    question = models.TextField()
    answer = models.TextField()
    
    def __str__(self):
        return self.question