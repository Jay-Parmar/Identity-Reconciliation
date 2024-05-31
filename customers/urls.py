from django.urls import path
from customers.views import IdentifyContactView

urlpatterns = [
    path('identify/', IdentifyContactView.as_view(), name='identify-contact'),
]
