from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactReturnSerializer, ContactIdentifySerializer

# Create your views here.

class IdentifyContactView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = ContactIdentifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        phone_number = serializer.data.get('phoneNumber')

        # Initial query to find matching contacts
        query = Q()
        if email:
            query |= Q(email=email)
        if phone_number:
            query |= Q(phone_number=phone_number)

        contacts = Contact.objects.filter(query)

        if contacts.exists():
            # Collect all linked contacts
            all_linked_contacts = set()
            contacts_to_process = set(contacts)
            while contacts_to_process:
                current_contact = contacts_to_process.pop()
                all_linked_contacts.add(current_contact)

                # Add linked contacts by email and phone number
                linked_by_email = Contact.objects.filter(email=current_contact.email) if current_contact.email else Contact.objects.none()
                linked_by_phone = Contact.objects.filter(phone_number=current_contact.phone_number) if current_contact.phone_number else Contact.objects.none()

                new_contacts = set(linked_by_email | linked_by_phone) - all_linked_contacts
                contacts_to_process.update(new_contacts)

            # Find the primary contact from all linked contacts
            primary_contacts = [contact for contact in all_linked_contacts if contact.link_precedence=='primary']
            if primary_contacts:
                primary_contact = sorted(all_linked_contacts, key=lambda x: x.created_at)[0]
                # primary_contacts.remove(primary_contact)
            else:
                raise ValueError("No primary contact found for the given data! Might be a DB issue.")
            
            # set the linked_id of all non-primary contacts
            for contact in primary_contacts:
                if contact!=primary_contact:
                    contact.linked_id = primary_contact
                    contact.link_precedence = 'secondary'
                    contact.save()

            # Populate response data
            emails = {c.email for c in all_linked_contacts if c.email}
            if email:
                emails = emails | {email}
            phones = {c.phone_number for c in all_linked_contacts if c.phone_number}
            if phone_number:
                phones = phones | {str(phone_number)}
            secondary_contacts = [c.id for c in all_linked_contacts if c.id != primary_contact.id]

            # Add a node if no node is present with the exact values
            if not Contact.objects.filter(email=email, phone_number=phone_number).exists():
                new_contact = Contact(
                    email=email,
                    phone_number=phone_number,
                    linked_id=primary_contact,
                    link_precedence='secondary'
                )
                new_contact.save()

            
            response_data = {
                'contact': ContactReturnSerializer({
                    'primaryContactId': primary_contact.id,
                    'emails': ([primary_contact.email] if primary_contact.email else []) + \
                        list(emails - {primary_contact.email}),
                    'phoneNumbers': ([str(primary_contact.phone_number)] if primary_contact.phone_number else []) + \
                        list(phones - {str(primary_contact.phone_number)}),
                    'secondaryContactIds': secondary_contacts
                }).data
            }
        else:
            # Create new primary contact if none exists
            new_contact = Contact(
                email=email,
                phone_number=phone_number,
                link_precedence='primary'
            )
            new_contact.save()
            response_data = {
                'contact': {
                    'primaryContactId': new_contact.id,
                    'emails': [new_contact.email] if new_contact.email else [],
                    'phoneNumbers': [new_contact.phone_number] if new_contact.phone_number else [],
                    'secondaryContactIds': []
                }
            }

        return Response(response_data)

