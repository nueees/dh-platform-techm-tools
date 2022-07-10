#!/usr/bin/env python3

from datetime import date, timedelta
from datetime import datetime
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

