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

# The maximum value OpsGenie's Alert can handle items.
OPSGENIE_ALERT_BATCH_LIMIT=100
OPSGENIE_API_KEY=""
OPSGENIE_TO_BQ_BATCH_SIZE=100000
OPSGENIE_API_BASE_URL="https://api.opsgenie.com/v2"

IS_TESTING = True

def remove_special_character(text):
    return text.encode('ascii', 'ignore').decode('ascii')


###################################################################################################
#                                    OpsGenie
###################################################################################################
class Opsgenie():

    def __init__(self):
        try:
            self.conf = self.conf = opsgenie_sdk.configuration.Configuration()
            # self.conf.api_key['Authorization'] = gcs_lib.get_service_secret(gcs_lib.SHARED_OPSGENIE_API_KEY)
            self.conf.api_key['Authorization'] = OPSGENIE_API_KEY

            self.api_client = opsgenie_sdk.api_client.ApiClient(configuration=self.conf)
            self.alert_api = opsgenie_sdk.AlertApi(api_client=self.api_client)
        except opsgenie_sdk.ApiException as err:
            print("Exception when calling AlertApi->opsgenie_alert: %s\n" % err)
                    
###################################################################################################
#                                    import_team_bq
###################################################################################################
    def import_team_bq(self):
        url = f'{OPSGENIE_API_BASE_URL}/teams'
        headers = {
                'Content-Type': 'application/json',
                'Authorization': 'GenieKey ' + OPSGENIE_API_KEY
        }
        try:
            r_teams = requests.get(f'{url}', headers=headers, timeout=60)
        except Exception as err:
            print("Exception when calling AlertApi->get team: %s\n" % err)
        if r_teams.status_code == 200:
            json_teams = r_teams.json()['data']
            csv_lines = []
            for team_rec in json_teams:
                csv_line = {}
                csv_line['team_id'] = team_rec['id']
                csv_line['team_name'] = team_rec['name']
                csv_line['description'] = remove_special_character(team_rec['description'])

                csv_lines.append(csv_line)
            try:
                gcs_lib.write_bq_table(csv_lines, gcs_lib.get_bq_field_mappings("opsgenie_team"), DATASET_NAME, "team", project='dh-gsre-jira-metrics', truncate=True)
            except Exception as e:
                gcs_lib.info_log(f"write_bq_table(opsgenie_team) error:  {e}")
                

        # return result
       
            
###################################################################################################
#                                    get_list_logs
###################################################################################################
    def get_list_logs(self, alert_id, alert_updated_at):
        logs_kwargs = { "limit" : 100 }
        alert_update_date = alert_updated_at.strftime("%Y-%m-%d")
        try:
            r_acti_logs = self.alert_api.list_logs(identifier=alert_id, **logs_kwargs)
        except Exception as err:
            print("Exception when calling activity log AlertApi->list_logs: %s\n" % err)
        csv_lines = []
        for acti_log_rec in r_acti_logs.data:
            if isinstance(acti_log_rec, AlertLog):
                create_at_date = acti_log_rec.created_at.strftime("%Y-%m-%d")
                # prevent duplicating from other dates
                if create_at_date < alert_update_date:
                    continue
                csv_line = {}
                csv_line['alert_id'] = alert_id
                # csv_line['log'] = acti_log_rec['log'].replace('"','').replace("’",'')
                csv_line['log'] = remove_special_character(acti_log_rec.log).replace('"', '')
                # csv_lines + json.dumps(list_log)
                # csv_line['log'] = json.dumps(list_log)
                csv_line['type'] = acti_log_rec.type
                csv_line['created_at'] = acti_log_rec.created_at.strftime("%Y-%m-%d %H:%M:%S")
                csv_line['owner'] = remove_special_character(acti_log_rec.owner)
                csv_line['offset'] = acti_log_rec.offset
                csv_lines.append(csv_line)
        return csv_lines
            
###################################################################################################
#                                    list_alerts
###################################################################################################
    def list_alerts(self, latest_date, limit=100, offset=0):
        # the reason why not greater than latest_date is if Maximum number of offset is 2000000, which can easily exceed a few days.
        update_at = latest_date.strftime("%d-%m-%Y")
        query = f'updatedAt={update_at}'
        try:
            list_response = self.alert_api.list_alerts(limit=limit, offset=offset, sort='updatedAt', order='asc', search_identifier_type='name', query=query)
            # print(list_response)
            return list_response
        except Exception as err:
            print("Exception when calling AlertApi->list_alerts: %s\n" % err)
            
###################################################################################################
#                                    import_bq
###################################################################################################
    def import_alert_bq(self, set_date):
        next_offset = 0
        list_alerts = self.list_alerts(set_date, limit=100, offset=next_offset) # list_alerts: ListAlertsResponse
        alert_paging = list_alerts.paging
        print(f"get_list_alerts to import from {set_date}")
        csv_lines_alert = []
        csv_lines_acti_logs = []  
        next_page = alert_paging.first
        print(alert_paging)
        
        while not next_page == None:
            alert_paging = list_alerts.paging
            next_page = alert_paging.next
            for alert_rec in list_alerts.data:
                if isinstance(alert_rec, BaseAlert):
                    csv_line_alert = {}
                    csv_line_alert['alert_id'] = alert_rec.id
                    csv_line_alert['tiny_id'] = alert_rec.tiny_id
                    # csv_line_alert['message'] = alert_rec.message
                    csv_line_alert['source'] = alert_rec.source
                    csv_line_alert['priority'] = alert_rec.priority
                    csv_line_alert['status'] = alert_rec.status
                    csv_line_alert['created_at'] = alert_rec.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    csv_line_alert['updated_at'] = alert_rec.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    # csv_line_alert['last_occurred_at'] = alert_rec.last_occurred_at.strftime("%Y-%m-%d %H:%M:%S")
                    csv_line_alert['owner'] = remove_special_character(alert_rec.owner)
                    responder_dic = {}
                    for i in alert_rec.responders:
                        responder_dic[i.type] = i.id
                    csv_line_alert["responders"] = responder_dic

                    # csv_line_alert['alias'] = alert_rec.alias
                    # csv_line_alert['message'] = alert_rec.message
                    # csv_line_alert['acknowledged'] = alert_rec.acknowledged
                    # csv_line_alert['is_seen'] = alert_rec.is_seen
                    csv_line_alert['tags'] = list(map(lambda x: remove_special_character(x.replace('"', '')), alert_rec.tags))
                    try:
                        if alert_rec.report.ack_time:
                            csv_line_alert['ack_time'] = alert_rec.report.ack_time
                    except:
                        csv_line_alert['ack_time'] = 0
                    try:
                        if alert_rec.report.close_time:
                            csv_line_alert['close_time'] = alert_rec.report.close_time
                    except:
                        csv_line_alert['close_time'] = 0
                    
                    csv_lines_acti_logs += self.get_list_logs(alert_rec.id, alert_rec.updated_at)
                    
                    
                    if len(csv_lines_acti_logs) > OPSGENIE_TO_BQ_BATCH_SIZE:
                        try:
                            gcs_lib.write_bq_table(csv_lines_acti_logs, gcs_lib.get_bq_field_mappings("opsgenie_alert_actlog"), DATASET_NAME, "alert_actlog", project='dh-gsre-jira-metrics',num_skip_leading_rows=0)
                            csv_lines_acti_logs = []  
                        except Exception as e:
                            gcs_lib.info_log(f"write_bq_table(opsgenie_alert_actlog_batch) error:  {e}")
                        
                    csv_lines_alert.append(csv_line_alert)
                    
            next_offset += 100
            list_alerts = self.list_alerts(set_date, limit=100, offset=next_offset)
        
        print(f'{DATASET_NAME}, alert: {len(csv_lines_alert)}, acti_log: {len(csv_lines_acti_logs)}')
        
        try:
            if len(csv_lines_alert) > 0:
                gcs_lib.write_bq_table_n(csv_lines_alert, gcs_lib.get_bq_field_mappings("opsgenie_alert"), DATASET_NAME, "alert", project='dh-gsre-jira-metrics',num_skip_leading_rows=0)
        except Exception as e:
            gcs_lib.info_log(f"write_bq_table(opsgenie_alert) error:  {e}")
        try:
            if len(csv_lines_acti_logs) > 0:
                gcs_lib.write_bq_table(csv_lines_acti_logs, gcs_lib.get_bq_field_mappings("opsgenie_alert_actlog"), DATASET_NAME, "alert_actlog", project='dh-gsre-jira-metrics',num_skip_leading_rows=0)
        except Exception as e:
            gcs_lib.info_log(f"write_bq_table(opsgenie_alert_actlog) error:  {e}")
            
        
        
###################################################################################################
#                                    handler
###################################################################################################      
def handler(event, context):
    gcs_lib.info_log('opsgenie_export_lambda.start')
    try:
        ## error occurs why..
        # gcs_lib.init_secrets(cred_type="_airflow", aws_default_creds = True)
        # gcs_lib.authenticate_gcp(project="dh-gsre-jira-metrics")
        
        ## need to change
        GCP_CREDENTIALS=''

        gcp_cred_file = gcs_lib.authenticate_gcp(project="dh-gsre-jira-metrics", gcpCreds=GCP_CREDENTIALS)
        # gcs_lib.init_service_secrets()
        client = Opsgenie()
        
        global DATASET_NAME
        if not IS_TESTING:
            DATASET_NAME = "opsgenie_metrics"
        else:
            DATASET_NAME = "opsgenie_metrics_test"
            
        gcs_lib.info_log(f'opsgenie_export_lambda.start dataset={DATASET_NAME}')

        # team import
        # client.import_team_bq()
        
        start_date = ""
        try:
            rows = gcs_lib.run_bq_query(f"select date(updated_at) as updated_at from `dh-gsre-jira-metrics.{DATASET_NAME}.alert` order by 1 desc limit 1", None, None)
            for row in rows:
                start_date = row["updated_at"] + timedelta(days=1)
        except: 
            print("No existing opsgenie metrics table:  Starting from 2021")
            start_date = date(2021, 1, 1).strftime('%Y-%m-%d')
        
        print(f"start_date: {start_date}")

        end_date = date.today() - timedelta(days=1)
        delta = end_date - start_date       # as timedelta

        for i in range(delta.days + 1):
            set_date = start_date + timedelta(days=i)
            client.import_alert_bq(set_date)
            
        gcs_lib.info_log('opsgenie_export_lambda.end')

        return { "statusCode": 200, "body": { "message": "OK" } }

    except Exception as e:
        gcs_lib.error_log("lambda_function_opsgenie_bq_export", e)
        raise 


if __name__ == '__main__':
    handler(None, None)
