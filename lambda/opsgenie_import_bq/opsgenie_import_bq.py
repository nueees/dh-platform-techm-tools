#!/usr/bin/env python3

from datetime import date, timedelta
from datetime import datetime
from dh_gcs_lib import gcs_lib
import requests
import opsgenie_sdk
from opsgenie_sdk.api.alert.list_alerts_response import ListAlertsResponse
from opsgenie_sdk.api.alert.alert import Alert
from opsgenie_sdk.api.alert.get_alert_response import GetAlertResponse
from opsgenie_sdk.api.alert.base_alert import BaseAlert
from opsgenie_sdk.api.alert.alert_log import AlertLog
from opsgenie_sdk.models.page_details import PageDetails
from requests.models import Response
import random
import json

      
###################################################################################################
#                                    handler
###################################################################################################      
def handler(event, context):
    print('opsgenie_export_lambda.start')


    return { "statusCode": 200, "body": { "message": "OK" } }


if __name__ == '__main__':
    handler(None, None)
