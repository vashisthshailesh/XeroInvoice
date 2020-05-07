from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import requests
from xero.auth import OAuth2Credentials
# from xero.auth import PublicCredentials
from xero import Xero
import base64
import time 
import datetime
import json 
# Create your views here.

def start_xero_auth_view(request):

	client_id = "___________________________"
	client_secret = "_____________________________________"
	credentials = OAuth2Credentials(client_id, client_secret, callback_uri="http://localhost:8000/logged/")
	# credentials = PublicCredentials(client_id, client_secret)
	authorization_url = credentials.generate_url()
	# authorization_url = credentials.url
	request.session['xero_creds'] = credentials.state
	return HttpResponseRedirect(authorization_url)
	#return render(request,'form/home.html')
	


def process_callback_view(request):
	cred_state = request.session['xero_creds']
	credentials = OAuth2Credentials(**cred_state)
	auth_secret = request.get_raw_uri()
	code = request.GET.get('code', '')
	# credentials.verify(auth_secret)
	# credentials.set_default_tenant()
	client_id = credentials.client_id
	client_secret = credentials.client_secret
	encodedData = base64.b64encode(bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
	authorization_header_string = f"Basic {encodedData}"

	r =requests.post('https://identity.xero.com/connect/token', headers = {'Authorization':authorization_header_string , 'Content-Type' : 'application/x-www-form-urlencoded' }, data ={"code" : code, "redirect_uri":"http://localhost:8000/logged/", 'grant_type' : 'authorization_code'})
	request.session['actk'] = r.json()['access_token'];

	# caches['mycache'].set('xero_creds', credentials.state)
	print(request.session['actk'])


	request.session['xero_creds'] = credentials.state
	
	return render(request,'form/home.html')

def formDataFromHtml(request):
	# print(request.session['actk'])
	qrawdata = request.POST
	lement = datetime.datetime.strptime(str(qrawdata['dis']),"%Y-%m-%d") 
	timestamp = datetime.datetime.timestamp(lement)
	element = datetime.datetime.strptime(str(qrawdata['dd']),"%Y-%m-%d") 
	etimestamp = datetime.datetime.timestamp(element) 
	if(qrawdata['intype'] == '1'):
		ivt = "ACCPAY"
	else:
		ivt = "ACCREC"

	if(qrawdata['lat'] == '1'):
		pvt = "Exclusive"
	elif(qrawdata['lat'] == '2'):
		pvt = "Inclusive"
	else:
		pvt = "NoTax"

	ar = []
	for i in range(int(qrawdata['member'])):
		t1 = "a1"+str(i)
		t2 = "a2"+str(i)
		t3 = "a3"+str(i)
		t4 = "a4"+str(i)
		t5 = "a5"+str(i)
		dic = {"Description" : qrawdata[t1], "Quantity" : qrawdata[t2], "UnitAmount" : qrawdata[t3], "AccountCode" : qrawdata[t4], "DiscountRate" : qrawdata[t5]}
		ar.append(dic)

	qdata = {"Type": ivt
	,"Contact": { 
    "ContactID": qrawdata['contactid'],
    "Name" : "ffg"
	},
	"Date": "/Date("+str(lement)+")"+"/",
	"DueDate": "/Date("+str(element)+")"+"/",
	"DateString": qrawdata['dis']+"T"+"00:00:00",
	"DueDateString": qrawdata['dd']+"T"+"00:00:00",
	"LineAmountTypes": pvt,
	"LineItems":ar

	}
	x =json.dumps(qdata)
	print(x)
	pl = 'Bearer '+request.session['actk']
	r =requests.put('https://api.xero.com/api.xro/2.0/Invoices' ,headers={'Authorization': pl,'Content-Type' : 'application/json'}, data = x)
	print(r)
	print(pl)	
	return render(request,'form/success.html')


