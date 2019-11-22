from django.db import models

# Create your models here.
class sf_auth(models.Model):
	SalesforceEdition=models.CharField(max_length=30,null=True)
	SalesforceOrgID=models.CharField(max_length=20,primary_key=True,blank=True)
	OrgName=models.CharField(max_length=20,null=True)
	ConnectedUserName=models.CharField(max_length=20,null=True)
	AccessToken=models.CharField(max_length=120,null=True)
	RefreshToken=models.CharField(max_length=120,null=True)
	SalesforceUserID=models.CharField(max_length=20,null=True)


class sf_leads(models.Model):
	LeadId=models.CharField(max_length=50,primary_key=True,blank=True)
	Name=models.CharField(max_length=50,null=True)
	Email=models.CharField(max_length=50,null=True)
	Company=models.CharField(max_length=50,null=True)
	OwnerID=models.CharField(max_length=20,null=True)
	LeadSource=models.CharField(max_length=50,null=True)
	CreatedDate=models.DateTimeField(max_length=50,null=True)
	City=models.CharField(max_length=50,null=True)
	auth_info = models.ForeignKey(sf_auth, on_delete=models.CASCADE,null=True)


class jwt_tokens(models.Model):
	username=models.CharField(max_length=50,primary_key=True,blank=True)
	AccessToken=models.CharField(max_length=250,null=True)
	RefreshToken=models.CharField(max_length=250,null=True)