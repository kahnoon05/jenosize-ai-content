# 🚀 Execute Fine-Tuning - Step-by-Step Commands

## ✅ Current Status
- Dataset: ✅ Ready (24 examples in data/finetuning/jenosize_finetuning.jsonl)
- Scripts: ✅ Ready (finetune_local.py created)
- Integration: ✅ Ready (local_model_service.py created)
- GPU: ✅ Ready (NVIDIA 4GB with CUDA 11.6)

---

## 🎯 Execute Now (Copy-Paste These Commands)

### **Step 1: Install Dependencies (5-10 minutes)**

Open Command Prompt or PowerShell and run:

```bash
# Navigate to project
cd D:\test\trend_and_future_ideas_articles\backend

# Install PyTorch with CUDA 11.6
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu116

# Install Transformers and core libraries
pip install transformers==4.35.0 datasets==2.14.0 accelerate==0.24.0

# Install efficient fine-tuning libraries
pip install peft==0.6.0 bitsandbytes==0.41.1 trl==0.7.0

# Install supporting libraries
pip install scipy sentencepiece protobuf tensorboard nltk rouge-score

# Verify CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

**Expected output:**
```
CUDA: True
GPU: NVIDIA GeForce ...
```

---

### **Step 2: Start Fine-Tuning (20-30 minutes)**

```bash
# Still in backend directory
python scripts/finetune_local.py --model mistral --epochs 3
```

**What will happen:**
1. Downloads Mistral-7B (first time only, ~14GB) - 5-10 minutes
2. Loads model with 4-bit quantization
3. Applies LoRA adapters
4. Trains on your 24 articles - 15-20 minutes
5. Tests the model automatically
6. Saves to `models/jenosize-finetuned/`

**You'll see:**
```
============================================================
🚀 JENOSIZE LOCAL FINE-TUNING
============================================================

📥 Loading model: mistralai/Mistral-7B-v0.1
   Using 4-bit quantization: True
✅ Model loaded successfully
   Trainable params: 13,631,488 (0.36%)

⚙️  Configuring LoRA...
✅ LoRA configured

📚 Loading dataset...
   Examples: 24
✅ Dataset prepared

🏋️  Starting training...
   Epochs: 3
   Batch size: 2
   This will take approximately 15-30 minutes...

[Training progress bars]

✅ Training complete!
💾 Saving model...
✅ Model saved successfully

🧪 Testing fine-tuned model...
[Generates 2 test articles]

============================================================
✅ ALL DONE!
============================================================
```

---

### **Step 3: Verify Model Saved**

```bash
# Check model directory
dir models\jenosize-finetuned

# Should contain:
# - adapter_config.json
# - adapter_model.bin (or .safetensors)
# - config.json
# - special_tokens_map.json
# - tokenizer files
# - metadata.json
```

---

### **Step 4: Update Backend Configuration**

#### A. Update `.env` file

Add these lines at the end of `.env`:

```bash
# Local Fine-Tuned Model Configuration
USE_LOCAL_MODEL=true
LOCAL_MODEL_PATH=./models/jenosize-finetuned
LOCAL_MODEL_4BIT=true
LOCAL_MODEL_TYPE=mistral
```

#### B. Update `backend/app/core/config.py`

Add these fields to the `Settings` class (around line 40-50):

```python
# Local Model Configuration
use_local_model: bool = Field(
    default=False,
    description="Use locally fine-tuned model instead of Claude API"
)

local_model_path: str = Field(
    default="./models/jenosize-finetuned",
    description="Path to fine-tuned model directory"
)

local_model_4bit: bool = Field(
    default=True,
    description="Use 4-bit quantization for local model inference"
)

local_model_type: str = Field(
    default="mistral",
    description="Type of local model (mistral, gpt2, gpt2-large, tinyllama)"
)
```

**OR** see the complete example in `backend/app/core/config_update.py`

#### C. Replace `content_generator.py`

```bash
# Backup original
copy backend\app\services\content_generator.py backend\app\services\content_generator_backup.py

# Replace with updated version
copy backend\app\services\content_generator_updated.py backend\app\services\content_generator.py
```

---

### **Step 5: Restart Backend and Test**

```bash
# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs -f backend

# Look for:
# "🤖 Using LOCAL fine-tuned model"
# "✅ Local model loaded successfully"
```

**Test via curl:**

```bash
curl -X POST http://localhost:8000/api/v1/generate-article ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\":\"Future of AI in Retail\",\"industry\":\"technology\",\"audience\":\"executives\",\"keywords\":[\"AI\",\"automation\",\"innovation\"],\"target_length\":1500,\"tone\":\"professional\",\"use_rag\":true}"
```

**Test via browser:**
1. Open http://localhost:3000
2. Fill in form
3. Click "Generate Article"
4. Should see article from YOUR fine-tuned model!

---

## 🎉 Success Indicators

### ✅ Fine-Tuning Successful If:
- Training completes without errors
- Model saved to `models/jenosize-finetuned/`
- Test articles are generated and look reasonable
- No CUDA out of memory errors

### ✅ Integration Successful If:
- Backend starts with "Using LOCAL fine-tuned model" in logs
- Article generation works via API
- Frontend generates articles
- Generated content is in Jenosize style

---

## 🐛 Troubleshooting

### Problem: "CUDA out of memory"
**Solution:**
```bash
# Use smaller batch size
python scripts/finetune_local.py --model mistral --batch-size 1

# Or use smaller model
python scripts/finetune_local.py --model gpt2 --epochs 3
```

### Problem: "Model download too slow"
**Solution:**
- Just wait, Hugging Face downloads can be slow
- Download will resume if interrupted
- ~14GB for Mistral, ~1.5GB for GPT-2

### Problem: "bitsandbytes not working"
**Solution:**
```bash
# Install Windows-compatible version
pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl
```

### Problem: "Generated text quality poor"
**Solutions:**
1. Train longer: `--epochs 5`
2. Add more training data
3. Try different model: `--model gpt2-large`
4. Lower temperature in API calls

### Problem: "Backend won't start with local model"
**Solutions:**
1. Check logs: `docker-compose logs backend`
2. Verify model path in .env
3. Ensure all config updates were made
4. Try running backend locally first to see errors

---

## 📊 Performance Expectations

### Training:
- **Mistral-7B**: 20-30 minutes on your GPU
- **GPT-2**: 5-10 minutes

### Inference (Article Generation):
- **Mistral-7B**: 15-25 seconds per article
- **GPT-2**: 5-10 seconds per article

### Quality:
- **Mistral-7B**: ⭐⭐⭐⭐⭐ Excellent Jenosize style
- **GPT-2**: ⭐⭐⭐ Good but simpler

---

## 📝 What to Include in Assignment Report

After fine-tuning completes, document:

1. **Model Selected**: Mistral-7B (or GPT-2)
2. **Rationale**: Good balance of quality and efficiency for 4GB GPU
3. **Fine-Tuning Method**: LoRA + 4-bit quantization
4. **Dataset**: 24 Jenosize articles across F/U/T/U/R/E topics
5. **Training Time**: [Your actual time]
6. **Results**:
   - Training loss: [From tensorboard]
   - Sample outputs: [Include 2-3 generated articles]
   - Quality assessment: [Your evaluation]
7. **Challenges**:
   - GPU memory constraints (solved with 4-bit + LoRA)
   - Limited dataset size (acceptable for LoRA fine-tuning)
8. **Improvements**:
   - Expand dataset to 100+ articles
   - Experiment with hyperparameters
   - Try ensemble approaches

---

## ✅ Ready? Start Now!

**Copy and run Step 1 commands to begin! 🚀**

```bash
cd D:\test\trend_and_future_ideas_articles\backend
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu116
```

Then proceed to Step 2 for fine-tuning!

---

**Time estimate: 30-40 minutes total**
**Difficulty: Medium (mostly waiting for downloads and training)**
**Result: Your own fine-tuned model that meets assignment requirements!**
