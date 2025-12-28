"""
OpenAI GPT-3.5 Fine-Tuning Script for Jenosize Content Generation
================================================================

This script automates the process of fine-tuning GPT-3.5 on Jenosize-style articles.

Usage:
    python scripts/finetune_openai.py --upload      # Upload training file
    python scripts/finetune_openai.py --train       # Start fine-tuning job
    python scripts/finetune_openai.py --status      # Check training status
    python scripts/finetune_openai.py --test        # Test fine-tuned model
"""

import os
import json
import time
import argparse
from pathlib import Path
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv


class JenosizeFineTuner:
    """
    Handles OpenAI fine-tuning workflow for Jenosize content generation
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize fine-tuner with OpenAI API key

        Args:
            api_key: OpenAI API key (or set via OPENAI_API_KEY env var)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.state_file = Path("./data/finetuning/finetuning_state.json")
        self.training_file = Path("./data/finetuning/jenosize_finetuning.jsonl")

    def load_state(self) -> dict:
        """Load saved state (file IDs, job IDs, etc.)"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def save_state(self, state: dict):
        """Save state to file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def upload_training_file(self) -> str:
        """
        Upload training file to OpenAI

        Returns:
            File ID from OpenAI
        """
        print("\n" + "=" * 60)
        print("📤 UPLOADING TRAINING FILE")
        print("=" * 60)

        if not self.training_file.exists():
            raise FileNotFoundError(
                f"Training file not found: {self.training_file}\n"
                f"Run: python scripts/scrape_jenosize_articles.py first"
            )

        print(f"\n📁 File: {self.training_file}")
        print(f"📊 Size: {self.training_file.stat().st_size / 1024:.2f} KB")

        # Count examples
        with open(self.training_file, 'r', encoding='utf-8') as f:
            num_examples = sum(1 for _ in f)
        print(f"📝 Examples: {num_examples}")

        # Upload
        print("\n⏳ Uploading to OpenAI...")
        with open(self.training_file, 'rb') as f:
            response = self.client.files.create(
                file=f,
                purpose="fine-tune"
            )

        file_id = response.id
        print(f"✅ Upload complete!")
        print(f"📋 File ID: {file_id}")

        # Save state
        state = self.load_state()
        state['file_id'] = file_id
        state['uploaded_at'] = time.time()
        self.save_state(state)

        print("\n" + "=" * 60)
        return file_id

    def create_finetuning_job(self, file_id: Optional[str] = None, n_epochs: int = 3) -> str:
        """
        Create fine-tuning job

        Args:
            file_id: Training file ID (or load from state)
            n_epochs: Number of training epochs (default: 3)

        Returns:
            Job ID
        """
        print("\n" + "=" * 60)
        print("🚀 CREATING FINE-TUNING JOB")
        print("=" * 60)

        # Get file ID from state if not provided
        if not file_id:
            state = self.load_state()
            file_id = state.get('file_id')

        if not file_id:
            raise ValueError(
                "No file ID provided. Run upload step first:\n"
                "  python scripts/finetune_openai.py --upload"
            )

        print(f"\n📋 Training file ID: {file_id}")
        print(f"🔢 Epochs: {n_epochs}")
        print(f"🤖 Base model: gpt-3.5-turbo-0125")

        # Create job
        print("\n⏳ Creating fine-tuning job...")
        job = self.client.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-3.5-turbo-0125",
            hyperparameters={
                "n_epochs": n_epochs
            },
            suffix="jenosize"  # Model will be named: ft:gpt-3.5-turbo:...:jenosize:...
        )

        job_id = job.id
        print(f"✅ Job created!")
        print(f"📋 Job ID: {job_id}")
        print(f"📊 Status: {job.status}")

        # Save state
        state = self.load_state()
        state['job_id'] = job_id
        state['created_at'] = time.time()
        self.save_state(state)

        print("\n💡 Monitor progress with:")
        print(f"   python scripts/finetune_openai.py --status")

        print("\n" + "=" * 60)
        return job_id

    def check_status(self, job_id: Optional[str] = None, follow: bool = False):
        """
        Check fine-tuning job status

        Args:
            job_id: Job ID (or load from state)
            follow: If True, poll until complete
        """
        print("\n" + "=" * 60)
        print("📊 FINE-TUNING STATUS")
        print("=" * 60)

        # Get job ID from state if not provided
        if not job_id:
            state = self.load_state()
            job_id = state.get('job_id')

        if not job_id:
            raise ValueError(
                "No job ID found. Create a fine-tuning job first:\n"
                "  python scripts/finetune_openai.py --train"
            )

        while True:
            # Get job details
            job = self.client.fine_tuning.jobs.retrieve(job_id)

            print(f"\n📋 Job ID: {job_id}")
            print(f"📊 Status: {job.status}")
            print(f"🤖 Model: {job.model}")

            if job.fine_tuned_model:
                print(f"✅ Fine-tuned model: {job.fine_tuned_model}")

                # Save to state
                state = self.load_state()
                state['fine_tuned_model'] = job.fine_tuned_model
                state['completed_at'] = time.time()
                self.save_state(state)

            if job.trained_tokens:
                print(f"📝 Tokens trained: {job.trained_tokens:,}")

            # Get recent events
            print("\n📜 Recent events:")
            events = self.client.fine_tuning.jobs.list_events(job_id, limit=5)
            for event in events.data:
                print(f"   • {event.message}")

            # Check if complete
            if job.status in ['succeeded', 'failed', 'cancelled']:
                print("\n" + "=" * 60)
                if job.status == 'succeeded':
                    print("✅ Fine-tuning complete!")
                    print(f"\n🎉 Your fine-tuned model: {job.fine_tuned_model}")
                    print("\n💡 Test it with:")
                    print(f"   python scripts/finetune_openai.py --test")
                else:
                    print(f"❌ Fine-tuning {job.status}")
                print("=" * 60)
                break

            if not follow:
                print("\n💡 Add --follow to poll until complete")
                print("=" * 60)
                break

            # Wait before next check
            print("\n⏳ Checking again in 60 seconds...")
            time.sleep(60)

    def test_model(self, model_id: Optional[str] = None):
        """
        Test the fine-tuned model

        Args:
            model_id: Fine-tuned model ID (or load from state)
        """
        print("\n" + "=" * 60)
        print("🧪 TESTING FINE-TUNED MODEL")
        print("=" * 60)

        # Get model ID from state if not provided
        if not model_id:
            state = self.load_state()
            model_id = state.get('fine_tuned_model')

        if not model_id:
            raise ValueError(
                "No fine-tuned model found. Complete fine-tuning first:\n"
                "  python scripts/finetune_openai.py --status"
            )

        print(f"\n🤖 Model: {model_id}")

        # Test cases
        test_cases = [
            {
                "topic": "Futurist",
                "industry": "Retail",
                "keywords": ["AI", "personalization", "customer experience"]
            },
            {
                "topic": "Transformation & Technology",
                "industry": "Healthcare",
                "keywords": ["telemedicine", "digital health", "patient care"]
            },
            {
                "topic": "Real-time Marketing",
                "industry": "Finance",
                "keywords": ["social media", "influencer", "engagement"]
            }
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n{'─' * 60}")
            print(f"Test Case {i}: {test['topic']} - {test['industry']}")
            print(f"{'─' * 60}")

            user_prompt = (
                f"Write a {test['topic']} article about {test['industry']} trends. "
                f"Focus on: {', '.join(test['keywords'])}. "
                f"Target word count: 200 words."
            )

            print(f"\n📝 Prompt:\n{user_prompt}\n")
            print("⏳ Generating...")

            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Jenosize content writer specializing in trend analysis and future ideas for businesses."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content
            word_count = len(content.split())

            print(f"📄 Generated Article ({word_count} words):")
            print(f"\n{content}\n")

        print("=" * 60)
        print("✅ Testing complete!")
        print("=" * 60)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Fine-tune GPT-3.5 for Jenosize content")

    parser.add_argument("--upload", action="store_true",
                       help="Upload training file to OpenAI")
    parser.add_argument("--train", action="store_true",
                       help="Create fine-tuning job")
    parser.add_argument("--status", action="store_true",
                       help="Check fine-tuning status")
    parser.add_argument("--follow", action="store_true",
                       help="Poll status until complete (use with --status)")
    parser.add_argument("--test", action="store_true",
                       help="Test fine-tuned model")
    parser.add_argument("--epochs", type=int, default=3,
                       help="Number of training epochs (default: 3)")
    parser.add_argument("--api-key", type=str,
                       help="OpenAI API key (or set OPENAI_API_KEY env var)")

    args = parser.parse_args()

    try:
        tuner = JenosizeFineTuner(api_key=args.api_key)

        if args.upload:
            tuner.upload_training_file()

        elif args.train:
            tuner.create_finetuning_job(n_epochs=args.epochs)

        elif args.status:
            tuner.check_status(follow=args.follow)

        elif args.test:
            tuner.test_model()

        else:
            parser.print_help()
            print("\n💡 Quick Start:")
            print("   1. python scripts/finetune_openai.py --upload")
            print("   2. python scripts/finetune_openai.py --train")
            print("   3. python scripts/finetune_openai.py --status --follow")
            print("   4. python scripts/finetune_openai.py --test")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
