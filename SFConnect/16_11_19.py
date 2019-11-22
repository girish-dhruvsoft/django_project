from django.shortcuts import render,redirect
from django.http import HttpResponse
from urllib import request
import requests,json
import psycopg2
from django.contrib.auth.decorators import login_required
from config import *
from django.db import models,DatabaseError
from SFConnect.models import sf_auth,sf_leads
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

def error_500(request):
	return render(request, 'layout.html', error_message="Sorry please try again!!")
def error_404(request):
	return render(request,'layout.html', error_message="Sorry please try again!!")
@login_required
def connect123(request):
	#<button onclick="location.href='http://localhost:8000/index/';">Connect to Salesforce</button>""")
	return render(request,"display_button.html")
@login_required
def index(request):
	return redirect(code_url)
def getaccess(request):
	"""code_params={
												'response_type':'code',
												'client_id': consumer_key,
												'redirect_uri': redirect_uri
												}
								print('------------------------------------------',codeUrl,code_params)
								code_response=requests.post(codeUrl,data=code_params)
								print(type(code_response))
								print("Hello...........")
								r=json.loads(code_response.content)
								print(r['code'])
								code = r['code']	"""				#
	code=request.GET.get('code',None)
	if code==None:
		return render(request,"layout.html", error_message="Sorry! Unable to process your request")
	params = {
		"grant_type":"authorization_code",
	    "client_id":consumer_key,
	    "client_secret":consumer_secret,
        "redirect_uri":redirect_uri,
	    "code":code
	     }
	try:
		access_token_response=requests.post(access_token_url,data=params)
		access_token_response=json.loads(access_token_response.content)
		access_token=access_token_response.get('access_token',None)
		refresh_token=access_token_response.get("refresh_token",None)
		your_instance=access_token_response.get('instance_url',None)
		if access_token==None or refresh_token==None:
			return render(request,"layout.html",{'error_message':"Sorry unable establish connection to Salesforce"})
		user_info= requests.get(User_info_url,headers= {"Authorization":"Bearer "+ access_token})
		result=user_info.json()
		user_id=result.get('user_id',None)
		user_fullName=result.get('name',None)
		if user_fullName==None:
			return render(request,"layout.html",{'error_message':"Sorry! Unable to get current user name from Salesforce"})
		org_url = your_instance+"/services/data/v47.0/query/?q=SELECT+Id,Name,OrganizationType+from+Organization"
		org_data= requests.get(org_url,headers = {"Authorization":"Bearer " + access_token})
		org_details=org_data.json()
		for i in org_details.get('records'):
			org_name=i.get('Name',None)
			org_type=i.get('OrganizationType',None)
			org_id=i.get('Id',None)
		if org_name==None or org_type==None or org_id==None:
			return render(request,"layout.html",{'error_message':"Sorry! Unable to get Organization information"})
	except (requests.exceptions.RequestException,json.decoder.JSONDecodeError):
		return render(request,"layout.html", {'error_message':"Sorry! Unable to get required information from Salesforce"})
	except:
			return render(request,"layout.html", {'error_message':"Sorry! Unable to get required information from Salesforce"})
	authorization_details={
		"Salesforce Edition: " : org_type,
		"Salesforce User ID: " : user_id,
		"Salesforce Org ID: " : org_id,
		"Salesforce Org Name: " : org_name,
		"Connected by User Name: " : user_fullName,
		"Access Token: " : access_token,
		"Refresh Token: " : refresh_token
		}
	try:
		existing_auth_info=sf_auth.objects.filter(SalesforceOrgID=org_id)
		if existing_auth_info:
			existing_auth_info.update(SalesforceEdition=org_type,OrgName=org_name,ConnectedUserName=user_fullName,AccessToken=access_token,RefreshToken=refresh_token,SalesforceUserID=user_id)
		else:
			auth_details=sf_auth(SalesforceEdition=org_type,SalesforceOrgID=org_id,OrgName=org_name,ConnectedUserName=user_fullName,AccessToken=access_token,RefreshToken=refresh_token,SalesforceUserID=user_id)
			auth_details.save()
			print("Authorization information added to the database.")
	except DatabaseError:
		return render(request,"layout.html", {'error_message':"Sorry! Unable to store the information in the database"})
	return render(request,"layout.html",{"authorization_details":authorization_details})
@login_required(login_url='/accounts/login/')
def connect(request):
	return render(request,"display_leads.html")
@login_required(login_url='/accounts/login/')
def fetchLeads(request):
	try:
		refresh_token1 = sf_auth.objects.filter().values()
		for x in refresh_token1:
			org_id=x.get("SalesforceOrgID",None)
			org_name=x.get("OrgName",None)
			user_fullName=x.get("OrgName",None)
			refresh_token=x.get("RefreshToken",None)
			if org_id==None or org_name==None or user_fullName==None or refresh_token==None:
				return render(request,"layout.html", {'error_msg':"0001"})
		refresh_accessToken={
			"client_id": consumer_key,
			"client_secret":consumer_secret,
			"grant_type":"refresh_token",
			"refresh_token" : refresh_token
			}
		refresh_token_response=requests.post(access_token_url,data=refresh_accessToken)
		refresh_token_response=refresh_token_response.json()
		access_token=refresh_token_response.get("access_token",None)
		if access_token==None:
			return render(request,"layout.html", {'error_msg':"0001"})
	except:
		return render(request,"layout.html", {'error_msg':"0001"})
	existing_auth_info=sf_auth.objects.filter(SalesforceOrgID=org_id)
	if existing_auth_info:
		existing_auth_info.update(AccessToken=access_token)
	lead_url=instance_url+"/services/data/v47.0/query?q=SELECT+Id,Name,Email,Company,LeadSource,CreatedDate,city,OwnerId+from+Lead"
	lead_list=[]
	def getRecords(lead_url):
		lead_response=requests.get(lead_url,headers = {"Authorization":"Bearer " + access_token})
		lead_response=lead_response.json()
		for i in lead_response.get('records'):
			lead_id=i.get("Id",None)
			lead_name=i.get("Name",None)
			lead_email=i.get("Email",None)
			lead_company=i.get("Company",None)
			lead_source=i.get("LeadSource",None)
			created_date=i.get("CreatedDate",None)
			lead_city=i.get("City",None)
			lead_owner_id=i.get("OwnerId",None)
			#if None in (lead_id,lead_name,lead_email,lead_company,lead_source,created_date,lead_city,lead_owner_id):
				#return render(request,"layout.html", {'error_msg':"0002"})
			existing_lead_info=sf_leads.objects.filter(LeadId=lead_id)
			if existing_lead_info:
				existing_lead_info.update(Name=lead_name,Email=lead_email,Company=lead_company,LeadSource=lead_source,CreatedDate=created_date,City=lead_city,OwnerID=lead_owner_id)
			else:
				lead_details=sf_leads(LeadId=lead_id,Name=lead_name,Email=lead_email,Company=lead_company,LeadSource=lead_source,CreatedDate=created_date,City=lead_city,OwnerID=lead_owner_id)
				lead_details.save()
			lead_info={
			"Leadid ":lead_id,
			"Name ":lead_name,
			"Email ":lead_email,
			"Company ":lead_company,
			"LeadSource ":lead_source,
			"CreatedDate ":created_date,
			"City ":lead_city,
			"LeadownerId":lead_owner_id
				}
			lead_list.append(lead_info)
			nextRecordsUrl=lead_response.get('nextRecordsUrl',None)
			if nextRecordsUrl != None:
				lead_next_url=instance_url+nextRecordsUrl
				getRecords(lead_next_url)
	getRecords(lead_url)

	#except DatabaseError:
		#return render(request,"layout.html", {'error_msg':"0001"})
	#except:
		#return render(request,"layout.html", {'error_msg':"0004"})
	return render(request,"display.html", {'lead_list':lead_list})


	#existing_lead_info1=sf_leads.objects.filter().values()
		#existing_lead_list=[]
		#for x in existing_lead_info1:
								#	existing_lead_id=x.get("LeadId")
									#existing_lead_list.append(existing_lead_id)
								#print(existing_lead_list)

class LoginView(APIView):
	def post(self, request):
		content = {'message': 'Hello, World!'}
		return Response(content)