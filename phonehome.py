import json

import urllib3
import cfnresponse

http = urllib3.PoolManager()


def lambda_handler(event, context):
    props = event["ResourceProperties"]
    data = {
        "deprovision_arn": props.get("DeprovisionRole", ""),
        "provision_arn": props.get("ProvisionRole", ""),
        "maintenance_arn": props.get("MaintenanceRole", ""),
        "breakglass_arn": props.get("BreakGlassRole", ""),
        "runner_id": props.get("RunnerId", ""),
        "stack_id": event["StackId"],
        "state": event["RequestType"],
    }
    # TODO(sdboyer) replace this whole-URL injection with a static base + an install id, once the API exists
    # url = "https://api.nuon.io/v1/installs/cloudformation-event/%s" % data["install_id"]

    encoded_data = json.dumps(data).encode("utf-8")
    url = props["url"]

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