import logging
import os
import json
import azure.functions as func
import openai

# Configure Azure OpenAI using environment variables.
# These variables should be set in your Azure Function App's Application Settings.
openai.api_type = "azure"
openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://https://salesforce-open-ai-agent.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview")
openai.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
openai.api_key = os.environ.get("AZURE_OPENAI_KEY", "")

# Get the deployment name (must match the name you used in Azure OpenAI)
deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing HTTP request for email draft generation.")

    # Parse the incoming request for JSON payload.
    try:
        req_body = req.get_json()
    except ValueError:
        logging.error("Invalid JSON payload received.")
        return func.HttpResponse("Invalid JSON payload.", status_code=400)

    # Get the first name from the request, defaulting to 'Valued Customer' if not provided.
    first_name = req_body.get("firstName", "Valued Customer")

    # Construct the conversation for chat-based completions.
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": (
            f"Compose a professional email addressed to {first_name} "
            "thanking them for their interest and inviting them to schedule a meeting."
        )}
    ]

    try:
        # Call the Chat Completion API using your deployment from Azure OpenAI.
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=messages,
            max_tokens=150000,
            temperature=0.7,
            top_p=1.0
        )
        # Extract the email draft from the response.
        email_draft = response.choices[0].message.content.strip()
        logging.info("Email draft generated successfully.")
    except Exception as e:
        # Log and return an error response in case of failure.
        logging.error(f"Error generating email from OpenAI: {str(e)}")
        error_response = {
            "error": "Error generating email",
            "details": str(e)
        }
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )

    # Return the generated email draft as a JSON response.
    result = {"emailDraft": email_draft}
    return func.HttpResponse(
        json.dumps(result),
        status_code=200,
        mimetype="application/json"
    )
