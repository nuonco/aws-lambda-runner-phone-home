import json

import urllib3
import cfnresponse

http = urllib3.PoolManager()

def lambda_handler(event, context):
	data = event["ResourceProperties"] | {
        "deprovision_arn": data.get("DeprovisionRole", ""),
        "provision_arn": data.get("ProvisionRole", ""),
        "maintenance_arn": data.get("MaintenanceRole", ""),
        "breakglass_arn": data.get("BreakGlassRole", ""),
		"stack_id": event["StackId"],
		"state": event["RequestType"],
	}
    # TODO(sdboyer) replace this whole-URL injection with a static base + an install id, once the API exists
    # url = "https://api.nuon.io/v1/installs/cloudformation-event/%s" % data["install_id"]
    url = event["url"]
	encoded_data = json.dumps(data).encode('utf-8')

	try:
		response = http.request(
			"POST",
			url,
			body=encoded_data,
			headers={"Content-Type": "application/json"},
		)
		print("Response: ", response.data)
		cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
	except Exception as e:
		print("Error: ", str(e))
		# It's OK if notifying Nuon fails on deletion
		if event["RequestType"] in ["Create", "Update"]:
			cfnresponse.send(event, context, cfnresponse.FAILED, {"Error": str(e)})
		else:
			cfnresponse.send(event, context, cfnresponse.SUCCESS, {})