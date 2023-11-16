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
		

