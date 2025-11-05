# Quick Start - Real-Time Photon Animation 🦎

## Get Running NOW (3 commands)

```bash
cd photon_demo_app
./setup.sh
source .venv/bin/activate && python src/photon_demo.py
```

---

## First Time? Try This! 🎬

### 1. **Basic Demo** (30 seconds)
- Leave all sliders at default
- Click **"Start Animation"**
- Watch photons rain down from top
- See some scatter upward (blue)
- See some get absorbed (red fade)
- Check statistics panel - energies should add to ~100%!

### 2. **Thin vs Thick Atmosphere** (1 minute)
- Set **Optical Depth = 0.5** (thin)
- Set **Photons = 20**
- Click Start
- → Notice: Most photons reach bottom! (high transmittance)

- Click **Reset**
- Set **Optical Depth = 8.0** (thick)
- Click Start
- → Notice: Many reflect back! (high reflectance)

### 3. **Pure Scattering** (30 seconds)
- Set **Scattering Prob = 1.0** (no absorption)
- Set **Optical Depth = 2.0**
- Set **Photons = 15**
- Click Start
- → Watch photons bounce up and down forever!
- → Eventually all exit (either top or bottom)
- → Absorptance = 0%!

### 4. **Pure Absorption** (30 seconds)
- Set **Scattering Prob = 0.0** (no scattering)
- Set **Optical Depth = 2.0**
- Set **Photons = 20**
- Click Start
- → All photons fade quickly!
- → All go straight down (no scatter)
- → All absorbed! Reflectance = 0%!

---

## Understanding the Display

### Main Animation Area

```
━━━━━━━━━━━━━━━━━━━━━━━━━  ← Top of Atmosphere (τ=0)
                           ↓ Photons rain down (yellow)
    🟡 ↓                   ↓
        🔵 ↑              ↓ Some scatter up (blue)
    🟡 ↓    💜            ↓ Magenta = scatter event!
        🟡 ↓              ↓
            🔴            ↓ Red fade = absorption
━━━━━━━━━━━━━━━━━━━━━━━━━  ← Surface (τ=τ_max)
```

### Right Side

- **Red histogram**: Shows WHERE photons absorbed
  - Top = absorption near TOA
  - Bottom = absorption near surface

### Statistics Panel

- **Reflectance**: % that exited at top
- **Transmittance**: % that reached bottom
- **Absorptance**: % absorbed in atmosphere
- **Total should ≈ 100%** (energy conservation)

---

## Pro Tips 🦊

### For Visual Clarity
- Use **10-20 photons** for easy viewing
- Slow down **Animation Speed** to 1.0x or less
- Watch individual photons scatter

### For Statistics
- Use **50-100 photons** for accurate percentages
- Speed up **Animation Speed** to 5-10x
- Focus on statistics panel, not individual photons

### For Demos
- Start **simple** (τ=1, ω₀=0.9, 15 photons)
- Change **one parameter** at a time
- Click **Reset** between demos
- Narrate what's happening!

---

## Common Questions

**Q: Photons are moving too fast!**
A: Reduce "Animation Speed" slider

**Q: Can't see individual photons**
A: Reduce "Number of Photons" to 10-15

**Q: Statistics don't add to exactly 100%**
A: Normal! With small photon counts, expect ±5% uncertainty

**Q: What's the magenta flash?**
A: Scattering event! Photon changed direction.

**Q: Why do some photons go up?**
A: After scattering, 50% chance to reverse direction

---

## Keyboard Shortcuts

None! This is a simple click-and-watch demo 🦎

---

## Next Steps

1. **Experiment** with different parameters
2. **Read full README.md** for physics explanation
3. **Try educational demos** in README
4. **Move to mc2s_app/** for advanced simulations

---

**Have fun watching photons!** ☀️🔬
