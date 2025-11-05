# Real-Time Photon Animation Demo 🦎

**Watch photons move through the atmosphere in real-time!**

An intuitive, visual demonstration of atmospheric radiative transfer where students can see individual photons scatter, absorb, and propagate through a simple atmospheric layer.

---

## 🎯 What This Demo Shows

This is a **simplified, highly visual** version of the Monte Carlo 2-stream simulation. Perfect for:

- **First-time learners** - See the physics happen step-by-step
- **Lecture demonstrations** - Real-time animation keeps students engaged
- **Building intuition** - Watch how optical depth and scattering affect photon paths

### Key Features

✅ **Real-time animation** - Photons move vertically through atmosphere
✅ **Scattering events** - See magenta flashes when photons scatter
✅ **Absorption visualization** - Red fading effect when photons are absorbed
✅ **Live statistics** - Reflectance, transmittance, absorptance update in real-time
✅ **Absorption profile** - Histogram shows WHERE in atmosphere photons get absorbed
✅ **Interactive controls** - Adjust optical depth, scattering probability, photon count

---

## 🚀 Quick Start

### Run in 3 Commands

```bash
cd photon_demo_app
./setup.sh
source .venv/bin/activate && python src/photon_demo.py
```

---

## 📖 How to Use

### 1. Set Parameters

Use the sliders on the right panel:

- **Optical Depth (τ)**: 0.5 to 10.0
  - Low τ (< 1): Thin atmosphere, most photons transmitted
  - High τ (> 5): Thick atmosphere, many absorptions/reflections

- **Scattering Probability (ω₀)**: 0.0 to 1.0
  - ω₀ = 0: Pure absorption (photons disappear quickly)
  - ω₀ = 1: Pure scattering (photons bounce forever)
  - ω₀ = 0.9: Typical cloud (mostly scattering, some absorption)

- **Number of Photons**: 1 to 100
  - Start with ~20 for clear visualization
  - Use 50-100 for better statistics

- **Animation Speed**: 0.5x to 10x
  - Slow down to see individual scatter events
  - Speed up for quick statistical results

### 2. Click "Start Animation"

Watch as photons:
1. 🟡 **Launch** from top (yellow/orange, moving down)
2. 🔵 **Scatter** (blue if moving up, with magenta flash at scatter point)
3. 🔴 **Absorb** (fade to red and disappear)
4. ⬆️ **Reflect** (reach top of atmosphere)
5. ⬇️ **Transmit** (reach surface)

### 3. Watch the Statistics Panel

Updates in real-time showing:
- How many photons launched, completed, currently moving
- **Reflectance** - Fraction that exited at top
- **Transmittance** - Fraction that reached bottom
- **Absorptance** - Fraction absorbed in atmosphere
- **Total should = 100%** (energy conservation!)

### 4. Observe Absorption Profile

The red histogram on the right side of the animation shows **WHERE** in the atmosphere photons get absorbed:
- Top bins = absorption near TOA
- Bottom bins = absorption near surface
- Useful for understanding atmospheric heating patterns!

---

## 🎓 Educational Demos

### Demo 1: Effect of Optical Depth

**Goal**: Show how atmosphere thickness affects transmission

1. Set ω₀ = 0.9, τ = 0.5, 20 photons
2. Click Start - observe **high transmittance** (most reach bottom)
3. Reset, change τ = 5.0
4. Click Start - observe **lower transmittance** (more scatter/absorb)

**Question for students**: "At what τ does reflectance = transmittance?"

### Demo 2: Pure Absorption vs Pure Scattering

**Goal**: Understand role of scattering albedo

1. Set τ = 2.0, ω₀ = 0.0 (pure absorption), 20 photons
2. Start - watch photons **quickly fade** (all absorbed, no scattering)
3. Reset, change ω₀ = 1.0 (pure scattering)
4. Start - watch photons **bounce up and down** (no absorption!)

**Question**: "Why does ω₀ = 1 give non-zero reflectance?"

### Demo 3: Where Does Absorption Happen?

**Goal**: Visualize atmospheric heating profile

1. Set τ = 3.0, ω₀ = 0.7, 50 photons (for better statistics)
2. Start animation
3. Watch **absorption histogram** build up
4. Notice where most absorption occurs

**Question**: "Does absorption happen more at top or bottom? Why?"

---

## 🔬 The Physics

### Two-Stream Approximation

Photons only move **vertically** (up or down), not horizontally. This simplifies the full 3D problem while capturing essential physics.

### Photon States

- **Yellow (⬇)**: Moving downward through atmosphere
- **Blue (⬆)**: Moving upward (after scattering)
- **Magenta flash**: Scattering event occurring
- **Red fade**: Absorption happening

### What's Happening

1. **Sampling path length**: Distance to next interaction ~ exponential distribution
2. **Scatter or absorb?**: Random draw against ω₀
3. **Scatter direction**: In 2-stream, 50% up / 50% down (isotropic)
4. **Repeat** until photon exits atmosphere or is fully absorbed

---

## 🎨 Visual Guide

### Color Coding

| Color | Meaning |
|-------|---------|
| 🟡 Yellow | Photon moving DOWN |
| 🔵 Blue | Photon moving UP |
| 💜 Magenta flash | Scattering event! |
| 🔴 Red fade | Being absorbed |

### Arrow Indicators

Each moving photon shows a small white arrow:
- ⬇️ Downward arrow = moving toward surface
- ⬆️ Upward arrow = moving toward space

---

## 🧪 Experiment Ideas

### For Students

1. **Find the critical optical depth**
   - At what τ does reflectance = 50%?
   - Hint: Try ω₀ = 0.99 to minimize absorption

2. **Energy conservation check**
   - Run with 50 photons
   - Verify R + T + A ≈ 100%
   - Why might it not be exactly 100%?

3. **Absorption profile analysis**
   - Run with different τ values
   - Sketch how absorption profile changes
   - Explain physical reason

---

## ⚙️ Technical Details

### What's Different from Full Simulation?

This demo is **simplified** for visualization:

✅ **Simpler**: Only isotropic scattering (no asymmetry parameter)
✅ **Slower**: Intentionally animated for visual learning
✅ **Fewer photons**: 1-100 instead of thousands
✅ **Real-time**: Updates every frame (60 FPS)

### Performance

- Handles up to 100 photons smoothly
- Adjust animation speed if needed
- For statistical accuracy, use the full `mc2s_app` instead

---

## 🐛 Troubleshooting

**Photons move too fast**
→ Reduce "Animation Speed" slider

**Can't see individual photons**
→ Reduce number of photons to 10-20

**Statistics don't add to 100%**
→ This is normal! Small photon counts have statistical uncertainty

**Want more photons**
→ Use the full `mc2s_app` for serious simulations

---

## 🦊 Comparison with Other Tools

### This Demo (photon_demo_app)
- ✅ **Best for**: Visual learning, first exposure
- ✅ **Strength**: Real-time animation, intuitive
- ❌ **Limitation**: Simplified physics, small photon counts

### Full GUI (mc2s_app)
- ✅ **Best for**: Quantitative analysis, research
- ✅ **Strength**: Full physics, 50,000 photons, presets
- ❌ **Limitation**: Less visual (shows paths, not animation)

### Recommendation
- Start students with **this demo** (photon_demo_app)
- Then progress to **full GUI** (mc2s_app) for deeper study

---

## 📁 File Structure

```
photon_demo_app/
├── src/
│   ├── photon_demo.py       # Main GUI application
│   ├── photon_animation.py  # Animation engine
│   └── config.py            # Constants and settings
├── setup.sh                 # One-command setup
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 🎉 Tips for Teaching

### Before Class
- Run through demo yourself
- Test on classroom projector
- Prepare 2-3 parameter sets to show

### During Class
- Start with τ=1, ω₀=0.9, 10 photons
- Narrate what's happening as photons move
- Pause between runs to discuss results
- Let students suggest parameters to try

### After Class
- Share setup instructions for homework
- Assign parameter exploration exercises
- Connect to textbook two-stream equations

---

## 🚀 Next Steps

1. **Run this demo** - Get familiar with controls
2. **Try all demos** - See different atmospheric scenarios
3. **Explore on your own** - Find interesting parameter combinations
4. **Move to full GUI** - Use `mc2s_app` for research-grade simulations

---

**Enjoy watching photons dance through the atmosphere!** 🦎🔬☀️
