"""
Local Model Fine-Tuning Script for Jenosize Content Generation
===============================================================

Fine-tunes a pre-trained language model on your local computer using:
- Mistral-7B (or GPT-2 for faster training)
- 4-bit quantization (fits in 4GB VRAM)
- LoRA (Low-Rank Adaptation) for efficient training
- Your Jenosize dataset

Hardware Requirements:
- GPU: 4GB+ VRAM (NVIDIA with CUDA)
- RAM: 16GB+ recommended
- Storage: 20GB free space

Usage:
    python scripts/finetune_local.py --model mistral  # Best quality (20-30 min)
    python scripts/finetune_local.py --model gpt2     # Faster (5-10 min)
"""

import os
import json
import torch
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import argparse

# Check CUDA availability
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType


class JenosizeLocalFineTuner:
    """
    Fine-tunes language models locally for Jenosize content generation
    """

    # Model configurations optimized for 4GB GPU
    MODELS = {
        "mistral": {
            "name": "mistralai/Mistral-7B-v0.1",
            "description": "Best quality, 20-30 min training",
            "use_4bit": True,
        },
        "gpt2": {
            "name": "gpt2-medium",  # 355M parameters
            "description": "Faster training, 5-10 min",
            "use_4bit": False,
        },
        "gpt2-large": {
            "name": "gpt2-large",  # 774M parameters
            "description": "Good balance, 10-15 min",
            "use_4bit": True,
        },
        "tinyllama": {
            "name": "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
            "description": "Very fast, 5-10 min",
            "use_4bit": False,
        }
    }

    def __init__(
        self,
        model_key: str = "mistral",
        output_dir: str = "./models/jenosize-finetuned",
        dataset_path: str = "./data/finetuning/jenosize_finetuning.jsonl"
    ):
        """
        Initialize fine-tuner

        Args:
            model_key: Model to use (mistral, gpt2, gpt2-large, tinyllama)
            output_dir: Where to save fine-tuned model
            dataset_path: Path to training dataset
        """
        self.model_key = model_key
        self.model_config = self.MODELS[model_key]
        self.model_name = self.model_config["name"]
        self.use_4bit = self.model_config["use_4bit"]

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.dataset_path = Path(dataset_path)
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {dataset_path}\n"
                f"Run: python scripts/scrape_jenosize_articles.py first"
            )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"\n🚀 Using device: {self.device}")

    def load_model_and_tokenizer(self):
        """Load pre-trained model and tokenizer with optimization"""
        print(f"\n📥 Loading model: {self.model_name}")
        print(f"   Using 4-bit quantization: {self.use_4bit}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        # Configure 4-bit quantization if needed
        if self.use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )

            # Load model with quantization
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )

            # Prepare model for k-bit training
            self.model = prepare_model_for_kbit_training(self.model)
        else:
            # Load model without quantization (for smaller models)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                trust_remote_code=True
            )

        print(f"✅ Model loaded successfully")

        # Display model size
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        all_params = sum(p.numel() for p in self.model.parameters())
        print(f"   Trainable params: {trainable_params:,}")
        print(f"   Total params: {all_params:,}")

    def setup_lora(self):
        """Configure LoRA for efficient fine-tuning"""
        print(f"\n⚙️  Configuring LoRA...")

        # LoRA configuration
        lora_config = LoraConfig(
            r=16,  # Rank - controls adapter size
            lora_alpha=32,  # Scaling factor
            target_modules=["q_proj", "v_proj"] if "mistral" in self.model_key else ["c_attn"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )

        # Apply LoRA to model
        self.model = get_peft_model(self.model, lora_config)

        # Display trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        all_params = sum(p.numel() for p in self.model.parameters())
        trainable_percent = 100 * trainable_params / all_params

        print(f"✅ LoRA configured")
        print(f"   Trainable params: {trainable_params:,} ({trainable_percent:.2f}%)")
        print(f"   Total params: {all_params:,}")

    def load_and_prepare_dataset(self):
        """Load and prepare training dataset"""
        print(f"\n📚 Loading dataset: {self.dataset_path}")

        # Load JSONL dataset
        dataset = load_dataset('json', data_files=str(self.dataset_path))

        print(f"   Examples: {len(dataset['train'])}")

        # Prepare prompts for training
        def format_example(example):
            """
            Convert dataset example to training format
            Expected format from JSONL:
            {
                "messages": [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."}
                ]
            }
            """
            messages = example['messages']

            # Combine into single training text
            text = ""
            for msg in messages:
                role = msg['role']
                content = msg['content']

                if role == "system":
                    text += f"<|system|>\n{content}\n\n"
                elif role == "user":
                    text += f"<|user|>\n{content}\n\n"
                elif role == "assistant":
                    text += f"<|assistant|>\n{content}<|endoftext|>"

            return {"text": text}

        # Format dataset
        self.dataset = dataset['train'].map(format_example, remove_columns=['messages'])

        print(f"✅ Dataset prepared")

        # Tokenize dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=1024,  # Reduced for 4GB VRAM
                padding="max_length"
            )

        print(f"\n🔤 Tokenizing dataset...")
        self.tokenized_dataset = self.dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text"]
        )

        print(f"✅ Dataset tokenized")

    def train(self, epochs: int = 3, batch_size: int = 2):
        """
        Train the model

        Args:
            epochs: Number of training epochs
            batch_size: Batch size (2 for 4GB GPU, increase if you have more VRAM)
        """
        print(f"\n🏋️  Starting training...")
        print(f"   Epochs: {epochs}")
        print(f"   Batch size: {batch_size}")

        # Training arguments optimized for 4GB GPU
        training_args = TrainingArguments(
            output_dir=str(self.output_dir / "checkpoints"),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,  # Effective batch size = 2 * 4 = 8
            learning_rate=2e-4,
            fp16=True,  # Mixed precision for speed
            save_steps=50,
            logging_steps=10,
            save_total_limit=2,  # Keep only 2 checkpoints to save space
            report_to="tensorboard",
            warmup_steps=10,
            optim="paged_adamw_8bit" if self.use_4bit else "adamw_torch",
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal language modeling
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.tokenized_dataset,
            data_collator=data_collator,
        )

        # Train!
        print(f"\n⏱️  Training started at {datetime.now().strftime('%H:%M:%S')}")
        print(f"   This will take approximately {epochs * 5}-{epochs * 10} minutes...")
        print(f"   Monitor progress: tensorboard --logdir {self.output_dir}/checkpoints")

        trainer.train()

        print(f"\n✅ Training complete!")

        # Save model
        self.save_model()

    def save_model(self):
        """Save fine-tuned model"""
        print(f"\n💾 Saving model to: {self.output_dir}")

        # Save model
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)

        # Save metadata
        metadata = {
            "base_model": self.model_name,
            "model_key": self.model_key,
            "finetuned_at": datetime.now().isoformat(),
            "dataset": str(self.dataset_path),
            "use_4bit": self.use_4bit,
        }

        with open(self.output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Model saved successfully")
        print(f"\n📁 Model location: {self.output_dir.absolute()}")

    def test_model(self, prompts: Optional[List[str]] = None):
        """
        Test the fine-tuned model

        Args:
            prompts: List of test prompts (optional)
        """
        print(f"\n🧪 Testing fine-tuned model...")

        if prompts is None:
            prompts = [
                "<|system|>\nYou are a Jenosize content writer specializing in trend analysis and future ideas for businesses.\n\n<|user|>\nWrite a Futurist article about Retail trends. Focus on: AI, personalization, customer experience. Target word count: 200 words.\n\n<|assistant|>\n",
                "<|system|>\nYou are a Jenosize content writer specializing in trend analysis and future ideas for businesses.\n\n<|user|>\nWrite a Transformation & Technology article about Healthcare trends. Focus on: telemedicine, digital health, innovation. Target word count: 200 words.\n\n<|assistant|>\n"
            ]

        for i, prompt in enumerate(prompts, 1):
            print(f"\n{'─' * 60}")
            print(f"Test {i}:")
            print(f"{'─' * 60}")

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=300,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the assistant's response
            if "<|assistant|>" in generated_text:
                response = generated_text.split("<|assistant|>")[-1].strip()
            else:
                response = generated_text

            print(f"\n{response}\n")

        print(f"{'=' * 60}")
        print(f"✅ Testing complete!")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Fine-tune language model locally")

    parser.add_argument(
        "--model",
        type=str,
        default="mistral",
        choices=list(JenosizeLocalFineTuner.MODELS.keys()),
        help="Model to fine-tune (default: mistral)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs (default: 3)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="Batch size (default: 2 for 4GB GPU)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./models/jenosize-finetuned",
        help="Output directory for fine-tuned model"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="./data/finetuning/jenosize_finetuning.jsonl",
        help="Path to training dataset"
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Only test existing model without training"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models"
    )

    args = parser.parse_args()

    # List models
    if args.list_models:
        print("\n📋 Available Models:")
        print("=" * 60)
        for key, config in JenosizeLocalFineTuner.MODELS.items():
            print(f"\n{key}:")
            print(f"  Name: {config['name']}")
            print(f"  Description: {config['description']}")
            print(f"  4-bit quantization: {config['use_4bit']}")
        print("\n" + "=" * 60)
        return 0

    try:
        # Initialize fine-tuner
        tuner = JenosizeLocalFineTuner(
            model_key=args.model,
            output_dir=args.output_dir,
            dataset_path=args.dataset
        )

        if args.test_only:
            # Load existing model and test
            print(f"\n🧪 Testing existing model at: {args.output_dir}")
            tuner.load_model_and_tokenizer()
            tuner.test_model()
        else:
            # Full training pipeline
            print("\n" + "=" * 60)
            print("🚀 JENOSIZE LOCAL FINE-TUNING")
            print("=" * 60)

            # Load model
            tuner.load_model_and_tokenizer()

            # Setup LoRA
            tuner.setup_lora()

            # Load dataset
            tuner.load_and_prepare_dataset()

            # Train
            tuner.train(epochs=args.epochs, batch_size=args.batch_size)

            # Test
            tuner.test_model()

            print("\n" + "=" * 60)
            print("✅ ALL DONE!")
            print("=" * 60)
            print(f"\n📁 Fine-tuned model saved to: {Path(args.output_dir).absolute()}")
            print(f"\n💡 Next steps:")
            print(f"   1. Test the model: python scripts/finetune_local.py --test-only --model {args.model}")
            print(f"   2. Integrate into API: Update backend/app/services/langchain_service.py")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
