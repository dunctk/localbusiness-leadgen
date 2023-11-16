from django_q.tasks import async_task, result
import json
from django.contrib.gis.geos import Point
from .models import OutscraperTask, Company, Contact


def extract_name(full_name_key, outscraper_json):
    # Helper function to split the full name into first and last name
    if isinstance(outscraper_json.get(full_name_key), str):
        parts = outscraper_json[full_name_key].split(' ')
        if len(parts) > 1:
            return parts[0], ' '.join(parts[1:])
        return parts[0], ''
    return '', ''


def extract_contacts():
    companies_without_contacts = Company.objects.filter(contacts__isnull=True)
    print("Found", str(len(companies_without_contacts)), "companies without extracted contacts, attempting to extract...")
    
    created_count = 0
    for company in companies_without_contacts:
        # Loop through possible email keys and their corresponding full names.
        for i in range(1, 5): 
            email_key = f'email_{i}'
            full_name_key = f'email_{i}_full_name'

            email_value = company.outscraper_json.get(email_key)
            
            if isinstance(email_value, str) and email_value:  # Check that there's an actual string email present.
                firstname, lastname = extract_name(full_name_key, company.outscraper_json)

                contact_data = {
                    'firstname': firstname,
                    'lastname': lastname,
                }

                # Update or create the contact
                contact, created = Contact.objects.update_or_create(
                    email=email_value,
                    company=company,
                    defaults=contact_data
                )
                
        if created:
            created_count += 1
    
    print("Done, extracted", str(created_count), "new contacts.")


def process_outscraper_response():
    created_count = 0
    print("Checking for companies to add from completed OutScraper tasks...")
    for task_object in OutscraperTask.objects.filter(was_processed=False):
        tasks_json = task_object.response_json
        for company in tasks_json:
            #print(json.dumps(company),'\n')
            obj, created = Company.objects.update_or_create(
                google_cid=company['cid'],
                defaults={
                    'name' : company['name'],
                    'outscraper_json': company,
                    'outscraper_task': task_object,
                    'location': Point(company['longitude'], company['latitude']),
                    'website': company['site'],
                    'generic_email': company['email_1']
                }
            )
            if created:
                created_count += 1
        task_object.was_processed = True
        task_object.save()
    print("Done,", str(created_count), "companies added")
