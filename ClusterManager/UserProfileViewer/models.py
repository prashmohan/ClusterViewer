from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=30, unique=True, primary_key=True)
    email = models.EmailField(null=True)

    def __unicode__(self):
        return str(self.name) + " <" + str(self.email) + ">"

