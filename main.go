package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/aws/aws-lambda-go/cfn"
	"github.com/aws/aws-lambda-go/lambda"
)

func handler(ctx context.Context, event cfn.Event) (any, error) {
	resp := cfn.NewResponse(&event)
	resp.Data = make(map[string]any)

	data := map[string]any{
		"stack_id":        event.StackID,
		"state":           string(event.RequestType),
		"provision_arn":   event.ResourceProperties["ProvisionRole"],
		"deprovision_arn": event.ResourceProperties["DeprovisionRole"],
		"maintenance_arn": event.ResourceProperties["MaintenanceRole"],
		"breakglass_arn":  event.ResourceProperties["BreakGlassRole"],
	}

	// Smooth out empty values by at least ensuring everything is strings
	for k, v := range data {
		if _, ok := v.(string); !ok {
			data[k] = ""
		}
	}

	// TODO(sdboyer) replace this whole-URL injection with a static base + an install id, once the API exists
	// url := fmt.Sprintf("https://api.nuon.io/v1/installs/cloudformation-event/%s", event.ResourceProperties["InstallID"])
	url := event.ResourceProperties["url"].(string)
	byts, err := json.Marshal(data)
	if err != nil {
		resp.Status = cfn.StatusFailed
		resp.Data["Message"] = "Failed to marshal data from cfn stack into JSON"
	} else {
		_, err = http.Post(url, "application/json", bytes.NewBuffer(byts))

		resp.Data["Message"] = "Nuon API informed of state change to stack"
		resp.Status = cfn.StatusSuccess
		if err != nil {
			if event.RequestType == cfn.RequestDelete {
				// It's OK if informing the API fails on deletion, we don't want that to block stack removal
				resp.Status = cfn.StatusSuccess
			}
			resp.Data["Message"] = "Failed to inform Nuon API of state change to stack"
		}
	}

	err = resp.Send()
	if err != nil {
		fmt.Println("Failed to send response:", err)
	}

	return nil, nil
}

func main() {
	lambda.Start(handler)
}
