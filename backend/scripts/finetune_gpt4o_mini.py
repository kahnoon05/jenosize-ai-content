"""
Fine-tune GPT-4o-mini with Jenosize articles
"""

import os
import time
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
load_dotenv(env_file)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")

client = OpenAI(api_key=api_key)

# Paths
data_file = project_root / "data" / "finetuning" / "jenosize_finetuning.jsonl"
state_file = project_root / "data" / "finetuning" / "finetuning_state_gpt4o_mini.json"

print("=" * 60)
print("Fine-tuning GPT-4o-mini for Jenosize Content Generation")
print("=" * 60)

# Step 1: Upload training file
print(f"\n[1/4] Uploading training file: {data_file}")
print(f"File size: {data_file.stat().st_size / 1024:.1f} KB")

with open(data_file, "rb") as f:
    file_response = client.files.create(
        file=f,
        purpose="fine-tune"
    )

file_id = file_response.id
print(f"[OK] File uploaded successfully!")
print(f"File ID: {file_id}")

# Step 2: Create fine-tuning job
print(f"\n[2/4] Creating fine-tuning job for gpt-4o-mini-2024-07-18...")

job_response = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3  # Can adjust: 1-50, default is auto
    },
    suffix="jenosize"  # Model name will include this suffix
)

job_id = job_response.id
print(f"[OK] Fine-tuning job created successfully!")
print(f"Job ID: {job_id}")
print(f"Status: {job_response.status}")

# Save state
state = {
    "file_id": file_id,
    "job_id": job_id,
    "base_model": "gpt-4o-mini-2024-07-18",
    "status": job_response.status,
    "created_at": job_response.created_at,
}

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)

print(f"\n[OK] State saved to: {state_file}")

# Step 3: Monitor training
print(f"\n[3/4] Monitoring training progress...")
print("This may take 10-30 minutes depending on dataset size.")
print("You can close this and check later with: openai api fine_tuning.jobs.retrieve -i {job_id}")

last_status = None
while True:
    job = client.fine_tuning.jobs.retrieve(job_id)
    current_status = job.status

    if current_status != last_status:
        print(f"\n[{time.strftime('%H:%M:%S')}] Status: {current_status}")
        last_status = current_status

        # Update state file
        state["status"] = current_status
        if hasattr(job, 'fine_tuned_model') and job.fine_tuned_model:
            state["fine_tuned_model"] = job.fine_tuned_model

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    # Check if training is complete
    if current_status == "succeeded":
        fine_tuned_model = job.fine_tuned_model
        print(f"\n[SUCCESS] Training completed successfully!")
        print(f"Fine-tuned model ID: {fine_tuned_model}")

        # Save final state
        state["fine_tuned_model"] = fine_tuned_model
        state["status"] = "succeeded"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

        print(f"\n[4/4] Next steps:")
        print(f"1. Update .env file:")
        print(f"   LLM_MODEL={fine_tuned_model}")
        print(f"2. Restart backend:")
        print(f"   docker-compose restart backend")
        print(f"   # or")
        print(f"   git add .env && git push origin main")

        break

    elif current_status == "failed":
        print(f"\n[ERROR] Training failed!")
        if hasattr(job, 'error') and job.error:
            print(f"Error: {job.error}")
        break

    elif current_status == "cancelled":
        print(f"\n[WARNING] Training was cancelled")
        break

    # Wait before checking again
    time.sleep(30)  # Check every 30 seconds

print("\n" + "=" * 60)
print("Fine-tuning process complete!")
print("=" * 60)
