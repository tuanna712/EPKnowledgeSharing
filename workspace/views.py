from django.shortcuts import render
from django.conf import settings
from .forms import UploadForm
from django.http import HttpResponseRedirect
import os
from app.io.extractor.pdf_extractor import PdfExtractor
from app.connection.mongodb import MongoConnector
from app.io.iomanager import IOManager, MongoManager, LocalManager


# Create your views here.

