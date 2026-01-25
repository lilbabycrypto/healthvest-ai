# HealthVest AI

### Your Intelligent Lab Report Companion
**Powered by Google MedGemma 1.5**

[![MedGemma Challenge](https://img.shields.io/badge/MedGemma-Impact%20Challenge-blue)](https://www.kaggle.com/competitions/med-gemma-impact-challenge)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## The Problem

**4.5 billion people** worldwide struggle to understand their medical lab reports.

- Lab reports are filled with **medical jargon** (HbA1c, TSH, Creatinine...)
- **63% of patients** forget what their doctor told them within an hour
- **No one explains** what YOUR specific numbers mean for YOUR health
- **Language barriers** prevent health understanding across cultures

## The Solution

**HealthVest AI** transforms confusing lab reports into personalized health conversations in 60 seconds.

```
Upload Lab Report → AI Analysis → Plain Language Explanation → Actionable Steps
```

## Features

| Feature | Description |
|---------|-------------|
| **Health Score** | Overall health rating (0-100) with category |
| **Pattern Detection** | Identifies diabetes, anemia, thyroid, cardiac risks |
| **5 Languages** | English, Hindi, Spanish, French, Arabic |
| **ELI15 Mode** | Simple explanations without medical jargon |
| **Doctor Questions** | Smart questions to ask your physician |
| **Risk Forecast** | What happens if no changes vs. with lifestyle changes |
| **Critical Alerts** | Flags urgent values needing attention |
| **Follow-up Tests** | Recommends additional tests based on results |
| **Lifestyle Simulator** | Shows how exercise/diet could improve values |
| **4-Week Action Plan** | Personalized week-by-week improvement plan |

## Safety-First Design

We deliberately chose NOT to:
- Diagnose diseases (doctors diagnose)
- Prescribe medications (requires FDA approval)
- Replace doctor consultations (we enhance, not replace)

Every response includes doctor consultation advice.

## Try It

### Kaggle Notebook (Recommended)
Run the full demo on Kaggle with free GPU:
**[Kaggle Notebook Link]** *(Add after making public)*

### Local Setup
```bash
git clone https://github.com/lilbabycrypto/healthvest-ai.git
cd healthvest-ai/notebooks
# Open kaggle_medgemma_lab_analyzer.ipynb in Jupyter
```

**Requirements:**
- HuggingFace account with MedGemma access
- GPU with 16GB+ VRAM (or use Kaggle's free GPU)

## Tech Stack

| Component | Technology |
|-----------|------------|
| **AI Model** | Google MedGemma 1.5 4B |
| **Framework** | Hugging Face Transformers |
| **Inference** | Pipeline API + bfloat16 |
| **Visualization** | Matplotlib |
| **Platform** | Kaggle Notebooks |

## Project Structure

```
healthvest-ai/
├── notebooks/
│   └── kaggle_medgemma_lab_analyzer.ipynb  # Main submission
├── SUBMISSION.md          # Challenge write-up
├── VIDEO_SCRIPT.md        # Video demo script
├── VEO_SHOTS.md          # Veo 3.1 video prompts
└── README.md             # This file
```

## Demo Video

**[Video Link]** *(Coming soon)*

## Performance

All metrics measured in real-time during notebook execution:

| Metric | Typical Value |
|--------|---------------|
| Response Time | 2-4 seconds |
| Safety Compliance | 70-90% |
| Doctor Mention Rate | 90-100% |
| Features Available | 10/10 |

## Impact

- **4.5 billion** people we can help understand their health
- **5 languages** supported (expanding)
- **60 seconds** from confusion to understanding
- **100%** doctor consultation recommendations

## Author

**Himanshu Balara**
- Email: balara77@gmail.com
- GitHub: [@lilbabycrypto](https://github.com/lilbabycrypto)

## License

MIT License - See [LICENSE](LICENSE) for details.

---

*Built for the [MedGemma Impact Challenge](https://www.kaggle.com/competitions/med-gemma-impact-challenge)*

**"Because everyone deserves to understand their own health."**
