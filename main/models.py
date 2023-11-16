from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class OutscraperTask(models.Model):
	outscraper_id = models.CharField(unique=True, max_length=50)
	created_time = models.DateTimeField(auto_now_add=True)
	response_json = models.JSONField(blank=True, null=True)
	search_category = models.CharField(max_length=200, blank=True, null=True)
	was_processed = models.BooleanField(default=False)

	def __str__(self):
		return str(self.created_time)


class Company(models.Model):
	name = models.CharField()
	location = models.PointField(geography=True, default=Point(0.0, 0.0))
	website = models.URLField(unique=True, blank=True, null=True)
	outscraper_task = models.ForeignKey(OutscraperTask, on_delete=models.CASCADE)
	generic_email = models.EmailField(unique=True, blank=True, null=True)
	google_cid = models.CharField(unique=True, blank=True, null=True)
	outscraper_json = models.JSONField(blank=True, null=True)


	def __str__(self):
		return self.name


	@property
	def longitude(self):
		return self.location.x    
	@property
	def latitude(self):
		return self.location.y

	

class Contact(models.Model):
	email = models.EmailField(unique=True)
	role = models.CharField(blank=True, null=True, max_length=100)
	firstname = models.CharField(blank=True, null=True, max_length=100)
	lastname = models.CharField(blank=True, null=True, max_length=100)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')	

	def __str__(self):
		if self.firstname and self.lastname:
			return self.firstname + ' ' + self.lastname
		else:
			return self.email
		
	
	@property
	def ps_text(self):
		other_contacts_with_names = Contact.objects.filter(
			company=self.company
		).exclude(
			pk=self.id
		).exclude(
			firstname=''
		).exclude(
			firstname__isnull=True
		)

		# Convert the QuerySet into a list of first names.
		other_firstnames = [contact.firstname for contact in other_contacts_with_names]

		if not other_firstnames:
			return None  # Return nothing if no names

		# Format the sentence based on number of contact names available.
		if len(other_firstnames) == 1:
			name_str = f"{other_firstnames[0]}."
		else:
			# Join all but last name with comma, append "and" before last name followed by full stop.
			name_str = ", ".join(other_firstnames[:-1]) + " and " + f"{other_firstnames[-1]}."

			ps_text = f"""
			P.S Hopefully you're the right person to chat to about this, but I did also reach out to {name_str}
			"""

			return ps_text.strip()
		

