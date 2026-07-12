
# LocateAnything

**LocateAnything** is a vision-language grounding model by NVIDIA that locates any object in images or videos using natural language descriptions.

## Goal

This repo has two objectives:

1. **Demo** — Host the official Gradio demo as a HuggingFace Space so users can interactively try LocateAnything on their own images and videos.
2. **Microscopy evaluation** — Benchmark LocateAnything on electron microscopy segmentation tasks and compare against domain-specific baselines (e.g. Micro-SAM), with the long-term goal of exploring microscopy-specific fine-tuning to assess whether general-purpose vision-language grounding can compete with or surpass specialized models in connectomics.

## Demo

The Space lets users upload an image or video and provide a text query (e.g. *"the red car on the left"*). The model returns bounding boxes drawn over the matching regions. Powered by [LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) with ZeroGPU acceleration on HuggingFace Spaces.

![Demo](assets/demo.gif)

## Project Structure

```
HF_LocateAnything/
├── app.py                  # Gradio app — model loading, inference, UI
├── run_app.py              # Optional launcher with Trackio telemetry
├── requirements.txt        # Python dependencies
├── index.html              # Custom landing page (Tailwind + vanilla JS)
├── assets/                 # Example images
├── datasets/
│   └── Lucchi++/           # Electron microscopy benchmark (git-ignored)
└── docs/
    ├── architecture/       # Deep-dive into model architecture
    └── discussions/        # Experiment design for microscopy evaluation
```

## Microscopy Experiments

An ongoing effort to benchmark LocateAnything against domain-specific baselines on electron microscopy data:

- **Lucchi++** — binary mitochondria segmentation in FIB-SEM mouse hippocampus
- **Kasthuri++** — cell/synapse detection in ATUM-SEM cortex
- **Baseline**: [Micro-SAM](https://github.com/computational-cell-analytics/micro-sam) ([Nature Methods 2024](https://www.nature.com/articles/s41592-024-02580-4))

### Dataset Downloads

- **Lucchi++**: [sites.google.com/view/connectomics](https://sites.google.com/view/connectomics) (Casser, Kang et al. 2018 — Fast Mitochondria Detection for Connectomics)
- **Kasthuri++**: [sites.google.com/view/connectomics](https://sites.google.com/view/connectomics) (Kasthuri et al. / Allen Institute — ATUM-SEM cortex)

See `docs/discussions/experiment_design.html` for the full experimental design.

## Setup & Reproduce

> **Note**: This project targets **Python 3.10**. Using a different Python version may cause dependency conflicts (see [Debug](#debugtroubleshooting) below).

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/ththamid/HF_LocateAnything.git
cd HF_LocateAnything
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> The `datasets/` directory is git-ignored. If you plan to run the microscopy experiments, download the data separately — see [Dataset Downloads](#dataset-downloads) above.

### 3. Run the demo locally

```bash
python app.py
```

The Gradio interface will be available at `http://localhost:7860`.

### 4. (Optional) Run with Trackio telemetry

```bash
pip install trackio psutil pynvml
python run_app.py
```

---

## Debug / Troubleshooting

### Issue 1 — Missing build tools for source compilation

**Symptom**: `pip` tries to build `numpy==1.25.0` from source (`.tar.gz`) and fails because `setuptools` and `wheel` are missing from the virtual environment.

**Fix**: Install build tools first, then install requirements:

```bash
pip install setuptools wheel
pip install -r requirements.txt
```

### Issue 2 — Python 3.13 compatibility failure with older NumPy

**Symptom**: Python 3.13 removed the legacy `imp` module. Older `setuptools` (pulled in by `numpy==1.25.0` at build time) cannot run on Python 3.13, causing the installation to fail even with build tools present.

**Fix**: Lift the strict version constraint on NumPy so pip fetches a modern, pre-compiled wheel. Update the line in `requirements.txt`:

```
numpy>=2.1.0
```

### Issue 3 — Missing optional hardware tracking dependencies

**Symptom**: Trackio runs but cannot report CPU, RAM, GPU, or VRAM metrics.

**Fix**: Install Trackio alongside its optional hardware dependencies:

```bash
pip install trackio psutil pynvml
```

- `psutil` — collects CPU and RAM metrics
- `pynvml` — interfaces with NVIDIA drivers for GPU and VRAM metrics

### Issue 4 — Version conflict (`transformers` vs `huggingface-hub`)

**Symptom**: `transformers 4.57.1` requires `huggingface-hub < 1.0`, but Trackio requires `huggingface-hub >= 1.0`. pip's resolver overwrites one with the other, breaking `transformers` imports.

**Fix**: Upgrade `transformers` to a version compatible with the modern `huggingface-hub` ecosystem:

```bash
pip install --upgrade transformers huggingface-hub trackio
```

---

## References

- **Paper**: [Fast and High-Quality Vision-Language Grounding with Parallel Box Decoding](https://arxiv.org/abs/2605.27365) (arXiv:2605.27365)
- **Model**: [nvidia/LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) on HuggingFace
- **Official Space**: [nvidia/LocateAnything](https://huggingface.co/spaces/nvidia/LocateAnything)
- **NVIDIA Research**: [research.nvidia.com/labs/lpr/locate-anything](https://research.nvidia.com/labs/lpr/locate-anything/)

## Acknowledgements

- [Micro-SAM](https://github.com/computational-cell-analytics/micro-sam) — microscopy baseline
- [Moon-ViT](https://huggingface.co/moonshotai/MoonViT-SO-400M) by Moonshot AI
- [Qwen2.5-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct) base model
- [Eagle (Embodied)](https://github.com/NVlabs/Eagle/tree/main/Embodied) by NVlabs
- [locate-anything.cpp](https://github.com/mudler/locate-anything.cpp) — C++ port
