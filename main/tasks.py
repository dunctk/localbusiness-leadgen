from django_q.tasks import async_task, result
import json
from django.contrib.gis.geos import Point
from django.db import IntegrityError
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
    ignore_words = ['privacy', 'applicants']

    companies_without_contacts = Company.objects.filter(contacts__isnull=True)
    print("Found", str(len(companies_without_contacts)), "companies without extracted contacts, attempting to extract...")
    
    created_count = 0
    duplicates_skipped_count = 0
    ignored_emails_count = 0

    for company in companies_without_contacts:
        # Loop through possible email keys and their corresponding full names.
        for i in range(1, 5): 
            should_ignore_contact = False

            email_key = f'email_{i}'
            full_name_key = f'email_{i}_full_name'

            email_value = company.outscraper_json.get(email_key)

            if not isinstance(email_value, str) or not email_value:
                # Skip if invalid or empty e-mail
                continue

            for word in ignore_words:
                if word.lower() in email_value.lower(): 
                    should_ignore_contact = True
                    ignored_emails_count += 1
                    break
            
            if should_ignore_contact:
                # Continue outer loop skipping this contact since it contains an ignored word.
                continue
            

            firstname, lastname = extract_name(full_name_key, company.outscraper_json)

            try:
                # Try to update or create the contact safely within try-except block
                contact_data = {
                    'firstname': firstname.title(),
                    'lastname': lastname.title(),
                }
                
                contact, created = Contact.objects.update_or_create(
                    defaults=contact_data,
                    email=email_value,
                    company=company
                )
                
                if created:
                    created_count += 1
                    
            except IntegrityError as e:
                duplicates_skipped_count += 1
                
    
    print(f"""
          Done, extracted {created_count} new contacts. 
          Skipped {duplicates_skipped_count} duplicates 
          and {ignored_emails_count} blacklisted word based emails.
          """)
    
    avg_contacts_per_company = Contact.objects.all().count() / Company.objects.all().count()
    avg_firstname_contacts_per_co = Contact.objects.exclude(
            firstname__isnull=True
        ).exclude(
            firstname=''
        ).count() / Company.objects.all().count()

    print(f"""
          On average there are now {avg_contacts_per_company} contacts per company in the db.
          And {avg_firstname_contacts_per_co} per company that have a known name.
          """)


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


def personlise_emails():
    pass