import urllib.request
import time
import boto3
import os
import json
from datetime import datetime,timezone
from urllib.error import URLError, HTTPError
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
tablename = os.environ["TABLE_NAME"]
table = dynamodb.Table(tablename)

sns = boto3.client("sns")
sns_topic_arn = os.environ["SNS_TOPIC_ARN"]

def save_result(result):
    item = result.copy()
    item["time_elapsed_ms"] = Decimal(str(item["time_elapsed_ms"]))
    table.put_item(Item = item)

def send_alert(result):
    if result["healthy"]:
        return
    else:
        response = sns.publish(
            TopicArn=sns_topic_arn, 
            Subject=f"Health Alert: {result['service_id']}", 
            Message=json.dumps(result, indent=2)
            )
        
        print({"alert_sent": True, "sns_message_id": response["MessageId"], "service_id": result["service_id"]})

def lambda_handler(event, context):
    try:
        service_id = event["service_id"]
        url = event["url"]
        checked_at = (datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"))
        start_time = time.perf_counter()
        response = urllib.request.urlopen(url, timeout = 5)
        time_elapsed = round((time.perf_counter() - start_time) * 1000 , 2)
        result = {
            "service_id" : service_id,
            "checked_at" : checked_at,
            "url" : url,
            "status_code" : response.status,
            "time_elapsed_ms" : time_elapsed,
            "healthy" : 200 <= response.status < 400
        }
        print({"request_id": context.aws_request_id, "result": result})
        save_result(result)
        return result
    except HTTPError as error_response:
        time_elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        result = {
            "service_id" : service_id,
            "checked_at" : checked_at,
            "url": url,
            "status_code": error_response.code,
            "time_elapsed_ms": time_elapsed,
            "healthy": False,
            "failure_type": "HTTP_ERROR",
            "error": str(error_response)
        }
        print({"request_id": context.aws_request_id, "result": result})
        save_result(result)
        send_alert(result)
        return result
    except URLError as error_response:
        time_elapsed = round((time.perf_counter() - start_time) * 1000,2)
        result ={
            "service_id" : service_id,
            "checked_at" : checked_at,
            "url":url, 
            "time_elapsed_ms": time_elapsed, 
            "healthy": False, 
            "failure_type": "URL_ERROR",
            "error": str(error_response)
        }
        print({"request_id": context.aws_request_id, "result": result})
        save_result(result)
        send_alert(result)
        return result
    except TimeoutError as error_response:
        time_elapsed = round((time.perf_counter() - start_time) * 1000,2)
        result = {
            "service_id" : service_id,
            "checked_at" : checked_at,
            "url": url,
            "time_elapsed_ms": time_elapsed, 
            "healthy": False,
            "failure_type": "TIMEOUT",
            "error": str(error_response)
        }
        print({"request_id": context.aws_request_id, "result": result})
        save_result(result)
        send_alert(result)
        return result

    
