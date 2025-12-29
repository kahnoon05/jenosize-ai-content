import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get status
job = client.fine_tuning.jobs.retrieve("ftjob-Jm6aaGKV1pXN6h10ODVvHdlA")

print(f"Status: {job.status}")
print(f"Created: {job.created_at}")

if hasattr(job, 'finished_at') and job.finished_at:
    print(f"Finished: {job.finished_at}")

if hasattr(job, 'fine_tuned_model') and job.fine_tuned_model:
    print(f"Model ID: {job.fine_tuned_model}")

if hasattr(job, 'trained_tokens') and job.trained_tokens:
    print(f"Trained tokens: {job.trained_tokens}")

if hasattr(job, 'error') and job.error:
    print(f"Error: {job.error}")
