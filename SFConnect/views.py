from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from urllib import request
import requests,json,schedule,time
from django.utils.safestring import mark_safe
import psycopg2
from background_task import background
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from config import *
from django.db import models,DatabaseError
from SFConnect.models import sf_auth,sf_leads,jwt_tokens
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib.auth import login as custom_login

def handler500(request, *args, **argv):
	return render(request, 'layout.html',{'error_message':"Srever error"})
def handler404(request, *args, **argv):
	return render(request, 'layout.html',{'error_message':"Not found"})
@login_required
def connect123(request):
	return render(request,"display_button.html")
@login_required
def index(request):
	return redirect(code_url)
def getaccess(request):
	code=request.GET.get('code',None)
	if code==None:
		return render(request,"layout.html", {'error_message':"Sorry! Unable to process your request"})
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
def login123(request):
	if request.method=='POST':
		form=LoginForm(request.POST)
		current_user=form.cleaned_data['username']
		current_password=form.cleaned_data['password']
		print(current_user,current_password)
		user = authenticate(username=current_user, password=current_password)
		if user:
			custom_login(request,user)
			print("this is if...")
			if request.GET.get('next',None):
				return HttpResponseRedirect(request.GET['next'])
		else:
			print("this is else.....")
			return redirect('login')
	return redirect('login')
def login_view(request):
	form=LoginForm()
	return render(request,'login.html',{'form':form})
@csrf_exempt
def connect(request):
	global current_user,current_password
	if request.method=='POST':
		form=LoginForm(request.POST)
		if form.is_valid():
			current_user=form.cleaned_data['username']
			current_password=form.cleaned_data['password']
	def access_token_update():
		jwt_refresh_token_url="http://127.0.0.1:8000/api/token/refresh/"
		refresh_token_info = jwt_tokens.objects.filter(username=current_user).values()
		for n in refresh_token_info:
			jwt_refresh_token=n.get("RefreshToken",None)
		refresh_access_token=requests.post(jwt_refresh_token_url,data = {"refresh" : jwt_refresh_token}).json()
		jwt_access_token=refresh_access_token.get("access",None)
		existing_user.update(AccessToken=jwt_access_token)
	def refresh_token_update():
		data={
		"username":current_user,
		"password":current_password
		}
		headers={"Content-Type":"application/x-www-form-urlencoded"}
		jwt_access_token_url="http://127.0.0.1:8000/api/token/"
		jwt_info=requests.post(jwt_access_token_url,data=data,headers=headers)
		jwt_info=jwt_info.json()
		jwt_access_token=jwt_info.get("access",None)
		jwt_refresh_token=jwt_info.get("refresh",None)
		jwt_details=jwt_tokens(username=current_user,AccessToken=jwt_access_token,RefreshToken=jwt_refresh_token)
		jwt_details.save()
	user = authenticate(username=current_user, password=current_password)
	if user:
		login(request,user)
		existing_user=jwt_tokens.objects.filter(username=current_user)
		if existing_user:
			access_token_update()
		else:
			refresh_token_update()
		return render(request,"display_leads.html")
	else:
		return redirect('login')
@login_required(login_url="/login123/")
@csrf_exempt
def fetchLeads(request):
	existing_auth_info=sf_leads.objects.filter().values()
	lead_list=[]
	for i in existing_auth_info:
		lead_id=i.get("LeadId",None)
		lead_name=i.get("Name",None)
		lead_email=i.get("Email",None)
		lead_company=i.get("Company",None)
		lead_source=i.get("LeadSource",None)
		created_date=i.get("CreatedDate",None)
		lead_city=i.get("City",None)
		lead_owner_id=i.get("OwnerId",None)
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
	return HttpResponse(lead_list)
def logout_view(request):
	if request.method=='POST':
		logout(request)
		return HttpResponseRedirect("http://127.0.0.1:8000/login")