import logging
import os
import json
import azure.functions as func
import openai

# Configure the Azure OpenAI service using environment variables.
openai.api_type = "azure"
openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")  # e.g., "https://<your-resource-name>.openai.azure.com/"
openai.api_version = "2023-03-15-preview"  # Adjust this version if necessary
openai.api_key = os.environ.get("AZURE_OPENAI_KEY")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a request to generate an email draft.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON payload.", status_code=400)

    first_name = req_body.get("firstName", "Valued Customer")

    # Define the prompt for GPT‑4
    prompt = (
        f"Compose a professional email addressed to {first_name}, thanking them for their interest "
        "and inviting them to schedule a meeting for further discussion. Keep the tone friendly yet professional."
    )
    
    try:
        # Call the Azure OpenAI GPT‑4 endpoint.
        response = openai.Completion.create(
            engine="gpt-4",  # Ensure that your deployment in Azure OpenAI uses this engine name
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        email_draft = response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Error generating email: {str(e)}")
        return func.HttpResponse(f"Error generating email: {str(e)}", status_code=500)

    return func.HttpResponse(
        json.dumps({"emailDraft": email_draft}),
        mimetype="application/json",
        status_code=200
    )
