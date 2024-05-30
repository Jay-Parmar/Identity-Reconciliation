from django.db import models
from django.core.exceptions import ValidationError

class Contact(models.Model):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    linked_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_contacts')
    link_precedence = models.CharField(max_length=10, choices=(('primary', 'Primary'), ('secondary', 'Secondary')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def clean(self):
        """
        Ensure that either phone number or email is provided.
        """
        if not (self.phone_number or self.email):
            raise ValidationError('Either a phone number or an email must be provided.')

    def __str__(self):
        return f"{self.email if self.email else 'No Email'} | {self.phone_number if self.phone_number else 'No Phone Number'}"
    
