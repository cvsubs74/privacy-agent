# Deploying Privacy Assessment Agent to GCP

This guide explains how to deploy the Privacy Assessment Agent to Google Cloud Platform (GCP) using Vertex AI Agent Engine.

## Prerequisites

1. **Google Cloud Project**: You need a GCP project with billing enabled
2. **Google Cloud Storage Bucket**: For storing deployment artifacts
3. **Required APIs enabled**:
   - Vertex AI API
   - Generative AI API
   - Cloud Storage API

## Setup Environment Variables

Create a `.env` file in the project root with the following variables:

```
# API Keys
GOOGLE_API_KEY=your_google_api_key_here

# GCP Configuration
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1  # or your preferred region
GOOGLE_CLOUD_STORAGE_BUCKET=your_gcp_bucket_name
```

## Installation

Install the deployment dependencies:

```bash
pip install -e ".[deployment]"
```

## Deployment Commands

### Deploy the Agent

```bash
python deployment/deploy.py --create
```

When the deployment finishes, it will print a line like this:

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

Save the `AGENT_ENGINE_ID` for future reference.

### List Deployed Agents

```bash
python deployment/deploy.py --list
```

### Delete a Deployed Agent

```bash
python deployment/deploy.py --delete --resource_id=<AGENT_ENGINE_ID>
```

## Using the Deployed Agent

You can interact with the deployed agent programmatically in Python:

```python
import dotenv
dotenv.load_dotenv()  # Load environment variables
from vertexai import agent_engines

agent_engine_id = "AGENT_ENGINE_ID"  # Replace with your agent's ID
user_input = "Analyze the privacy policy for example.com and check its compliance with GDPR"

agent_engine = agent_engines.get(agent_engine_id)
session = agent_engine.create_session(user_id="new_user")
for event in agent_engine.stream_query(
    user_id=session["user_id"], 
    session_id=session["id"], 
    message=user_input
):
    for part in event["content"]["parts"]:
        print(part["text"])
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all required packages are installed with `pip install -e ".[deployment]"`
2. **API Not Enabled**: Make sure all required APIs are enabled in your GCP project
3. **Authentication Issues**: Verify that you've set up authentication correctly with `gcloud auth application-default login`
4. **Permission Issues**: Ensure your GCP account has the necessary permissions to create and manage Agent Engine resources

### Logs

Check GCP logs for detailed error information:

1. Go to the GCP Console
2. Navigate to Logging > Logs Explorer
3. Filter for your agent's resource name

## Additional Resources

- [Vertex AI Agent Builder documentation](https://cloud.google.com/vertex-ai/docs/agent-builder/overview)
- [ADK documentation](https://github.com/google/adk)
