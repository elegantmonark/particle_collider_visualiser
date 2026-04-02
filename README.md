# Collider Viz - Particle Collision Event Display

A 3D interactive visualizer for particle physics collision events with realistic Standard Model physics, CMS detector geometry, and detailed particle information. Built with FastAPI, NumPy, Three.js, and vanilla JavaScript.

## Features

- **3D Event Display** - Interactive Three.js visualization of particle tracks through the CMS detector
- **6 Event Types** - Z boson decay, Higgs to 4 leptons (golden channel), di-muon, di-electron, top quark pair, QCD jets
- **Realistic Physics** - Helical tracks for charged particles in 3.8T magnetic field, straight lines for neutrals
- **CMS Detector Geometry** - Transparent cylindrical layers: tracker, ECAL, HCAL, solenoid, muon system
- **Particle Detail Panel** - Click any track to see full kinematics (pT, energy, eta, phi, Lorentz factor) and a physics explanation
- **Event Narratives** - Each event type comes with an accessible explanation of what happened in the collision
- **Particle Filtering** - Filter by type (leptons, hadrons, photons, charged, neutral) and minimum pT threshold
- **Click to Highlight** - Click a track to isolate it, dims all others
- **Color-Coded Particles** - Electrons (cyan), muons (green), pions (pink/purple), kaons (orange), photons (yellow)
- **Auto-Rotate** - Smooth orbital camera with toggle control

## Event Types

| Event | Description |
|-------|-------------|
| Z Boson Decay | Clean lepton pair at ~91 GeV invariant mass |
| Higgs to 4 Leptons | The "golden channel" discovery signature - 4 leptons at ~125 GeV |
| Di-muon | Muon-antimuon pair from Z/gamma* decay |
| Di-electron | Electron-positron pair from Drell-Yan process |
| Top Quark Pair | Complex event with jets, lepton, and missing energy |
| QCD Jets | High-multiplicity hadronic events from quark/gluon scattering |

## Installation

```bash
git clone https://github.com/yourusername/collider_viz.git
cd collider_viz
pip install -r requirements.txt
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

> Requires Python 3.10+. If using Python 3.15 alpha, use `py -3.12 -m uvicorn main:app --reload` instead.

## Usage

1. **Generate Events** - Click "New Event" or select a specific type from the dropdown
2. **Navigate** - Drag to orbit, scroll to zoom, right-drag to pan
3. **Inspect Particles** - Click any track or particle in the list to see its physics details
4. **Filter** - Use the pT slider and particle type chips to isolate what you want
5. **Toggle Detector** - Show/hide the detector layers
6. **Auto-Rotate** - Toggle the orbital camera animation

## Technical Approach

### Event Generation
Events are generated using Monte Carlo sampling based on Standard Model physics:
- Resonance decays (Z, Higgs) use proper two-body kinematics with Lorentz boosts
- Jets are modeled as collimated sprays of hadrons with realistic fragmentation
- Underlying event adds soft particles from proton remnants
- All momenta conserve energy-momentum (within numerical precision)

### Track Simulation
Particle trajectories through the CMS detector are computed using:
- **Charged particles**: Helical motion in the 3.8T solenoid magnetic field, with radius of curvature r = pT / (0.3 * B * |q|)
- **Neutral particles**: Straight-line propagation
- **Detector interactions**: Electrons/photons stop at ECAL, hadrons at HCAL, muons traverse everything

### Detector Geometry
Simplified CMS detector with correct radial dimensions:
- Silicon Tracker (r = 1.1m)
- Electromagnetic Calorimeter (r = 1.8m)
- Hadronic Calorimeter (r = 2.95m)
- Superconducting Solenoid (r = 3.0m)
- Muon Chambers (r = 7.4m)

## API Endpoints

- `GET /api/event?type=zpeak` - Generate a single collision event
- `GET /api/batch?n=20` - Generate multiple events
- `GET /api/particles` - Particle type catalogue
- `GET /api/detector` - Detector geometry
- `GET /health` - Health check

## Project Structure

```
collider_viz/
├── main.py          # FastAPI app and routes
├── physics.py       # Event generator with Standard Model physics
├── requirements.txt # fastapi, uvicorn, numpy, jinja2
├── README.md
├── LICENSE          # MIT
├── .gitignore
├── static/
│   └── style.css    # Dark theme styling
└── templates/
    └── index.html   # Three.js 3D frontend
```

## Author

**Trishan Biswas**

## License

[MIT License](LICENSE)
