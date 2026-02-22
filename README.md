# Live Motion Detection – Motion Signal Refactor (WIP)

## 📌 Project Status
 **Work in Progress**  
This project is actively under development.  
Recent commits focus on **architectural cleanup** and **signal-level stability**, not feature completion.

---

## 🎯 Project Goal
Build a **robust real-time motion detection system** that can reliably detect:
- motion start
- motion presence
- motion end  

without being sensitive to:
- camera shake
- lighting noise
- small irrelevant movements

The system is designed with **engineering-grade signal processing**, not just raw frame-based decisions.

---

## 🧠 Recent Changes (Current Focus)

### ✅ 1. MotionSignal Layer (NEW)
A new abstraction layer called `MotionSignal` has been introduced.

**Purpose:**
- Decouple FSM logic from raw motion detection
- Convert noisy motion areas into a **stable, meaningful signal**

FSM no longer reacts directly to frame-level data.

---

### ✅ 2. Signal Processing Pipeline
The motion area signal is now processed using a multi-stage pipeline:
Raw Motion Area
↓
Median Filter (noise suppression)
↓
Dead Zone (ignore micro-changes)
↓
EMA – Exponential Moving Average
↓
Trend Extraction
↓
Hysteresis-based Motion State

This significantly improves stability and prevents false triggers.

---

### ✅ 3. EMA (Exponential Moving Average)
EMA is used to smooth motion area over time:
EMA_t = α · x_t + (1 − α) · EMA_(t−1)

- Reduces sensitivity to sudden spikes
- Preserves long-term motion trends
- Makes FSM decisions reliable

---

### ✅ 4. Dead Zone Logic
Small fluctuations under a defined threshold are ignored:

- Prevents jitter
- Stabilizes trend direction
- Avoids rapid ENTER/EXIT oscillations

---

### ✅ 5. Motion Hysteresis
Two thresholds are used:
- `enter_threshold`
- `exit_threshold`

This avoids frequent toggling when motion level is near the boundary.

---

## 🏗 Current Architecture (Simplified)
Camera
↓
MotionDetector  →  raw motion area
↓
MotionSignal    →  stable motion signal
↓
FSM             →  ENTER / INSIDE / EXIT
↓
EventLogger

Each layer has **one clear responsibility**.

---

## ❗ What This Is NOT (Yet)
- ❌ Final detection logic
- ❌ Optimized thresholds
- ❌ Production-ready ROI system
- ❌ Machine learning model

These are planned next steps.

---

## 🧩 Next Planned Steps
- Fine-tuning MotionSignal parameters
- FSM refinement based on signal-level events
- Optional background stability improvements
- Better visualization & debugging tools

---

## 📝 Notes
This refactor prioritizes **correctness, clarity, and extensibility** over speed of implementation.

The goal is to **understand and control the signal**, not just detect motion.

---

## 👤 Author
Actively developed and refactored as part of an academic and learning-oriented project.

Contributions and feedback are welcome.
