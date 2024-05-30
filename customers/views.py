from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Contact

# Create your views here.

class IdentifyContactView(APIView):

    def post(self, request, *args, **kwargs):
        pass

