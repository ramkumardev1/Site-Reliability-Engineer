# -*- coding: utf-8 -*-
"""
Created on Fri Nov 04 20:05:59 2016

@author: ram
"""
import logging

import requests 
import json
from requests.auth import HTTPBasicAuth



BASE_URL = "https://services.mycompany.com"



def watch_resource_util(api_key,endpoint="/status"):
    """
    Module to watch the /staus/ end point hosted in https://services.mycompany.com/status
    The JSON result looks like 
    {"mem_usage": 0.98 , "disk_sapce": 1000,"cpu": 0.85}
    If the mem_usage (Memory Usage) is greater than 95.0 OR
    disk_space (Available Disk Space) is less than 1k OR
    cpu (CPU Usage) is greater than .97 a service ticket has to generated.
    This module cheks the basic limits and returns the stsus as True or False
    :param api_key: api_key to authenticate
    :return exceeds_limit: Bool . If the permissible limits exceeds it return True
    """
    headers = {'Accept': 'application/vnd.pagerduty+json;version=2',\
    'Authorization': 'Token token={token}'.format(token=api_key)}
    response = requests.get(BASE_URL + endpoint, headers=headers)
    status = response.json()
    
    risky_service = False
    
    if status.mem_usage >= .95 or status.disk_space <= 10000 or \
    status.cpu >= .97:
        risky_service = True
        logging.info("Risky Process identified ")
    return {"status":risky_service, "service_detail": status}

def create_ticket(service_msg,user_name,pass_word,api_key):
    """
    Module to create a service ticket
    :param service_msg: Details of the message 
    :param user_name: username to authenticate the service
    :param pass_word: password for the service 
    :param api_key: API key to the service
    :returns ticketed: Ticket number assigned 
    """
    headers = {'Accept': 'application/vnd.pagerduty+json;version=2',\
    'Authorization': 'Token token={token}'.format(token=api_key)}

    payload = {'note': {'content': "High CPU/Memory or Low Diskspace noticed. \
    Staus of the service is " + str(service_msg)}}    

    session = None    
    ticketed = None
    
    try:
        session = requests.get(BASE_URL + '/user', auth=HTTPBasicAuth('user', 'pass'))
    except:
        logging.error("Authenticating Error")

    if session.status_code == 202:
        ticketed = requests.post(BASE_URL + "/createTicket", \
        headers=headers, data=json.dumps(payload))
    else:
        logging.error("Ticket creation failed")
    return ticketed
    
if __name__ == "__main__":
    status = watch_resource_util("abcdefg")
    
    if status["status"] == True:
        ticket = create_ticket(status["service_detail"],"monitoring",\
        "f0th3win","abcdefg")
        logging.info(str(ticket))
    else:
        logging.error("Error in creating ticket")
