# Quick Start Guide 🦎

## Get Running in 3 Commands

```bash
cd mc2s_app
./setup.sh
source .venv/bin/activate && python src/mc2s_gui.py
```

That's it! The app should launch.

## First Time Using the App?

### Try These Steps:

1. **Click "Run Simulation"** - See the default atmosphere (τ=2.0, ω₀=0.9)

2. **Try a preset** - Select "Thick Cloud" from the dropdown
   - Watch reflectance increase dramatically!

3. **Adjust optical depth** - Slide τ from 0.1 to 30
   - See how clouds block sunlight

4. **Change scattering** - Try different asymmetry values
   - g=0.85 (forward) vs g=0 (isotropic)

5. **Surface effects** - Increase surface albedo to 0.8
   - Simulate snow/ice impact

### Understanding the Display

**Left side**: 
- Blue horizontal line = Top of atmosphere
- Brown horizontal line = Surface
- Colored squiggly lines = Individual photon paths
- Bar on right = Energy budget

**Photon colors**:
- 🔵 Blue = Reflected to space
- 🟠 Orange = Transmitted to surface
- ⚫ Gray = Absorbed in atmosphere

**Right side**:
- Sliders to adjust parameters
- Results show percentages
- Should always add to ~100%

## Common Student Questions

**Q: Why do some photons take crazy paths?**
A: Multiple scattering! Photons can bounce up and down many times before escaping.

**Q: What's a "good" number of photons?**
A: 5,000 for quick tests, 20,000+ for accurate statistics.

**Q: The results don't add to exactly 100%, why?**
A: Statistical uncertainty. More photons = closer to 100%.

**Q: What's the weight threshold?**
A: Photons with weight < 0.01 are terminated to save computation time.

## Classroom Demo Ideas

### Demo 1: Cloud Thickness
1. Start with Clear Sky preset
2. Switch to Thin Cloud
3. Switch to Thick Cloud
4. **Question**: How does reflectance change?

### Demo 2: Greenhouse Effect
1. Set τ=1.0, ω₀=0.5 (absorbing atmosphere)
2. Compare to ω₀=1.0 (non-absorbing)
3. **Question**: Where does absorbed energy go?

### Demo 3: Snow-Albedo Feedback
1. Start with surface_albedo=0.1 (dark soil)
2. Change to 0.8 (snow)
3. **Question**: How does this affect climate?

## Troubleshooting

**"No module named pygame"**
→ Run `./setup.sh` again

**App is slow**
→ Reduce number of photons to 1000-2000

**Window doesn't fit screen**
→ Edit `WINDOW_WIDTH` and `WINDOW_HEIGHT` in `src/config.py`

**Build failed**
→ Check that you're in activated venv: `which python` should show `.venv`

## Next Steps

- Read full `README.md` for detailed usage
- Check `2stream_monte_carlo_guide.md` in parent directory for theory
- Modify `config.py` to add custom presets
- Build standalone app with `./build.sh` for distribution

---

**Happy photon tracing!** 🦊
