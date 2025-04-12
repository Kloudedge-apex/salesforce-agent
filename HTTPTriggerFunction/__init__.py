import logging
import os
import json
import azure.functions as func
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Get credentials and endpoint from environment
api_key = os.environ.get("AZURE_INFERENCE_CREDENTIAL")
endpoint = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ENDPOINT")  # Full endpoint including /deployments/<deployment-name>

if not api_key or not endpoint:
    raise ValueError("Both AZURE_INFERENCE_CREDENTIAL and AZURE_OPENAI_DEPLOYMENT_ENDPOINT must be set.")

# Initialize Azure ChatCompletionsClient
client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to generate an email draft.")

    try:
        req_body: dict = req.get_json()
    except ValueError:
        logging.warning("Invalid JSON payload received.")
        return func.HttpResponse("Invalid JSON payload.", status_code=400)

    first_name = req_body.get("firstName", "Valued Customer")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": (
                f"Compose a professional email addressed to {first_name}, thanking them for their interest and inviting "
                "them to schedule a meeting for further discussion. Maintain a friendly yet professional tone."
            )
        }
    ]

    try:
        response = client.complete({
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.7,
            "top_p": 1.0,
            "stop": []
        })
        email_draft = response.choices[0].message.content.strip()
        logging.info("Successfully generated email draft.")
    except Exception as e:
        logging.error("Error generating email draft.", exc_info=True)
        return func.HttpResponse("Internal server error while generating email.", status_code=500)

    return func.HttpResponse(
        json.dumps({"emailDraft": email_draft}),
        mimetype="application/json",
        status_code=200
    )
