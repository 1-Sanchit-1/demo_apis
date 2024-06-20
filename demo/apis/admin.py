from django.contrib import admin
from .models import PDFFile

@admin.register(PDFFile)
class PDFFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')
