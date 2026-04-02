"""
Particle Physics Event Generator

Generates realistic particle collision events based on Standard Model physics.
Simulates pp collisions at LHC energies (13 TeV) with proper kinematics,
particle decay channels, and detector geometry.
"""

import numpy as np
from typing import Any

# Particle properties: mass (GeV/c^2), charge, color, symbol
PARTICLES = {
    "electron": {"mass": 0.000511, "charge": -1, "color": "#00c8ff", "symbol": "e-"},
    "positron": {"mass": 0.000511, "charge": 1, "color": "#ff6644", "symbol": "e+"},
    "muon": {"mass": 0.10566, "charge": -1, "color": "#00ff88", "symbol": "mu-"},
    "antimuon": {"mass": 0.10566, "charge": 1, "color": "#ffaa00", "symbol": "mu+"},
    "photon": {"mass": 0.0, "charge": 0, "color": "#ffff44", "symbol": "gamma"},
    "pion+": {"mass": 0.13957, "charge": 1, "color": "#ff44aa", "symbol": "pi+"},
    "pion-": {"mass": 0.13957, "charge": -1, "color": "#aa44ff", "symbol": "pi-"},
    "pion0": {"mass": 0.13498, "charge": 0, "color": "#888888", "symbol": "pi0"},
    "kaon+": {"mass": 0.49368, "charge": 1, "color": "#ff8844", "symbol": "K+"},
    "kaon-": {"mass": 0.49368, "charge": -1, "color": "#44aaff", "symbol": "K-"},
    "proton": {"mass": 0.93827, "charge": 1, "color": "#ff4444", "symbol": "p"},
    "antiproton": {"mass": 0.93827, "charge": -1, "color": "#4444ff", "symbol": "p-bar"},
    "jet": {"mass": 0.0, "charge": 0, "color": "#666666", "symbol": "jet"},
    "neutrino": {"mass": 0.0, "charge": 0, "color": "#333333", "symbol": "nu"},
}

# CMS detector geometry (simplified, in meters)
DETECTOR = {
    "tracker_radius": 1.1,      # Silicon tracker
    "ecal_inner": 1.29,         # Electromagnetic calorimeter inner
    "ecal_outer": 1.8,
    "hcal_inner": 1.81,         # Hadronic calorimeter inner
    "hcal_outer": 2.95,
    "solenoid_radius": 2.95,    # Superconducting solenoid
    "muon_inner": 4.0,          # Muon chambers
    "muon_outer": 7.4,
    "half_length": 5.5,         # Half-length along beam axis
    "b_field": 3.8,             # Magnetic field in Tesla
}


def generate_track_points(
    px: float, py: float, pz: float, charge: int, mass: float, particle_type: str
) -> list[list[float]]:
    """Generate 3D track points for a particle through the CMS detector.

    Charged particles curve in the magnetic field (helix trajectory).
    Neutral particles travel in straight lines.
    Electrons/photons stop at ECAL, hadrons at HCAL, muons go through everything.

    Args:
        px, py, pz: Momentum components in GeV/c.
        charge: Particle charge.
        mass: Particle mass in GeV/c^2.
        particle_type: Type name for determining detector interaction.

    Returns:
        List of [x, y, z] points in meters tracing the particle path.
    """
    pt = np.sqrt(px**2 + py**2)
    p = np.sqrt(px**2 + py**2 + pz**2)
    if p < 0.01:
        return [[0, 0, 0]]

    energy = np.sqrt(p**2 + mass**2)

    # Determine how far the particle travels
    if particle_type in ("electron", "positron", "photon", "pion0"):
        max_r = DETECTOR["ecal_outer"]  # Stops in ECAL
    elif particle_type in ("muon", "antimuon"):
        max_r = DETECTOR["muon_outer"]  # Passes through everything
    elif particle_type == "neutrino":
        max_r = DETECTOR["muon_outer"]  # Invisible but goes through
    else:
        max_r = DETECTOR["hcal_outer"]  # Hadrons stop in HCAL

    points = [[0.0, 0.0, 0.0]]
    n_points = 60

    if charge == 0:
        # Straight line for neutral particles
        phi = np.arctan2(py, px)
        theta = np.arctan2(pt, pz)
        for i in range(1, n_points + 1):
            t = (i / n_points) * max_r / np.sin(theta) if np.sin(theta) > 0.01 else (i / n_points) * max_r
            r = t * np.sin(theta)
            if r > max_r:
                break
            x = t * np.sin(theta) * np.cos(phi)
            y = t * np.sin(theta) * np.sin(phi)
            z = t * np.cos(theta)
            if abs(z) > DETECTOR["half_length"]:
                break
            points.append([float(x), float(y), float(z)])
    else:
        # Helix for charged particles in magnetic field
        # Radius of curvature: r = pt / (0.3 * B * |q|) in meters, pt in GeV
        B = DETECTOR["b_field"]
        r_curv = pt / (0.3 * B * abs(charge)) if pt > 0.01 else 100.0
        r_curv = min(r_curv, 50.0)  # Cap for very high pt

        phi0 = np.arctan2(py, px)
        omega = charge * 0.3 * B / (pt + 0.001)  # Angular velocity
        vz = pz / (energy + 0.001)  # z velocity (natural units approx)

        for i in range(1, n_points + 1):
            t = i * 0.15  # Time steps
            # Helix equations
            x = (np.sin(phi0 + omega * t) - np.sin(phi0)) / (omega + 1e-10)
            y = -(np.cos(phi0 + omega * t) - np.cos(phi0)) / (omega + 1e-10)
            z = vz * t * 2.0

            r = np.sqrt(x**2 + y**2)
            if r > max_r or abs(z) > DETECTOR["half_length"]:
                break
            points.append([float(x), float(y), float(z)])

    return points


def generate_event(event_type: str | None = None) -> dict[str, Any]:
    """Generate a single collision event with particles and tracks.

    Args:
        event_type: Optional type: 'dimuon', 'dielectron', 'zpeak', 'higgs_4l',
                    'ttbar', 'qcd_jets', or None for random.

    Returns:
        Event dict with metadata and particle list.
    """
    if event_type is None:
        event_type = np.random.choice(
            ["dimuon", "dielectron", "zpeak", "higgs_4l", "ttbar", "qcd_jets"],
            p=[0.2, 0.15, 0.25, 0.05, 0.15, 0.2],
        )

    particles = []
    run = int(np.random.randint(160000, 180000))
    event_num = int(np.random.randint(1, 10000000))

    if event_type == "dimuon":
        particles = _gen_dimuon()
        label = "Di-muon event"
        description = "Two muons from Z boson or virtual photon decay"
    elif event_type == "dielectron":
        particles = _gen_dielectron()
        label = "Di-electron event"
        description = "Two electrons from Z boson or Drell-Yan process"
    elif event_type == "zpeak":
        particles = _gen_zpeak()
        label = "Z boson decay"
        description = "Z boson decaying to lepton pair at ~91 GeV invariant mass"
    elif event_type == "higgs_4l":
        particles = _gen_higgs_4l()
        label = "Higgs candidate (4-lepton)"
        description = "Higgs boson decaying to ZZ* to 4 leptons (~125 GeV)"
    elif event_type == "ttbar":
        particles = _gen_ttbar()
        label = "Top quark pair"
        description = "Top-antitop pair production with leptonic decay"
    elif event_type == "qcd_jets":
        particles = _gen_qcd_jets()
        label = "QCD multijet event"
        description = "High-energy QCD jet production"
    else:
        particles = _gen_dimuon()
        label = "Di-muon event"
        description = "Two muons from Z boson decay"

    # Add soft underlying event particles
    n_ue = np.random.randint(5, 20)
    for _ in range(n_ue):
        particles.append(_gen_soft_particle())

    # Compute event-level quantities
    total_e = sum(p["energy"] for p in particles)
    met_x = -sum(p["px"] for p in particles if p["type"] != "neutrino")
    met_y = -sum(p["py"] for p in particles if p["type"] != "neutrino")
    met = float(np.sqrt(met_x**2 + met_y**2))

    # Generate tracks for all particles
    for p in particles:
        p["track"] = generate_track_points(
            p["px"], p["py"], p["pz"], p["charge"], p["mass"], p["type"]
        )

    return {
        "run": run,
        "event": event_num,
        "type": event_type,
        "label": label,
        "description": description,
        "sqrt_s": 13000.0,  # 13 TeV
        "num_particles": len(particles),
        "total_energy": round(float(total_e), 2),
        "met": round(met, 2),
        "particles": particles,
    }


def _make_particle(ptype: str, px: float, py: float, pz: float) -> dict[str, Any]:
    """Create a particle dict with computed kinematics."""
    info = PARTICLES[ptype]
    mass = info["mass"]
    p = np.sqrt(px**2 + py**2 + pz**2)
    energy = np.sqrt(p**2 + mass**2)
    pt = np.sqrt(px**2 + py**2)
    eta = np.arctanh(pz / (p + 1e-10)) if p > 0.01 else 0.0
    phi = np.arctan2(py, px)

    return {
        "type": ptype,
        "symbol": info["symbol"],
        "color": info["color"],
        "mass": float(mass),
        "charge": int(info["charge"]),
        "px": round(float(px), 4),
        "py": round(float(py), 4),
        "pz": round(float(pz), 4),
        "pt": round(float(pt), 4),
        "energy": round(float(energy), 4),
        "eta": round(float(eta), 4),
        "phi": round(float(phi), 4),
    }


def _gen_dimuon() -> list[dict[str, Any]]:
    """Generate a di-muon event (Z/gamma* -> mu+ mu-)."""
    m_inv = np.random.choice([
        np.random.normal(91.2, 2.5),   # Z peak
        np.random.exponential(20) + 10,  # Continuum
    ])
    m_inv = max(m_inv, 1.0)
    return _gen_lepton_pair("muon", "antimuon", m_inv)


def _gen_dielectron() -> list[dict[str, Any]]:
    """Generate a di-electron event."""
    m_inv = np.random.normal(91.2, 2.5)
    return _gen_lepton_pair("electron", "positron", max(m_inv, 1.0))


def _gen_zpeak() -> list[dict[str, Any]]:
    """Generate a Z boson event at the Z mass peak."""
    m_inv = np.random.normal(91.1876, 2.4952)
    if np.random.random() < 0.5:
        return _gen_lepton_pair("muon", "antimuon", m_inv)
    else:
        return _gen_lepton_pair("electron", "positron", m_inv)


def _gen_higgs_4l() -> list[dict[str, Any]]:
    """Generate a Higgs -> ZZ* -> 4 lepton event."""
    m_h = np.random.normal(125.1, 0.5)
    # First Z (on-shell)
    m_z1 = np.random.normal(91.2, 2.5)
    m_z1 = min(m_z1, m_h - 12)
    # Second Z (off-shell)
    m_z2 = np.random.uniform(12, m_h - m_z1)

    particles = []
    if np.random.random() < 0.5:
        particles.extend(_gen_lepton_pair("muon", "antimuon", m_z1))
        particles.extend(_gen_lepton_pair("electron", "positron", m_z2))
    else:
        particles.extend(_gen_lepton_pair("electron", "positron", m_z1))
        particles.extend(_gen_lepton_pair("muon", "antimuon", m_z2))
    return particles


def _gen_ttbar() -> list[dict[str, Any]]:
    """Generate a ttbar event with semi-leptonic decay."""
    particles = []
    # Leptonic top: t -> W b -> l nu b
    pt_l = np.random.exponential(40) + 20
    phi_l = np.random.uniform(-np.pi, np.pi)
    eta_l = np.random.normal(0, 1.5)
    px_l = pt_l * np.cos(phi_l)
    py_l = pt_l * np.sin(phi_l)
    pz_l = pt_l * np.sinh(eta_l)

    if np.random.random() < 0.5:
        particles.append(_make_particle("muon", px_l, py_l, pz_l))
    else:
        particles.append(_make_particle("electron", px_l, py_l, pz_l))

    # Neutrino
    particles.append(_make_particle("neutrino", -px_l * 0.8, -py_l * 0.6, pz_l * 0.5))

    # b-jets (2)
    for _ in range(2):
        pt_j = np.random.exponential(50) + 30
        phi_j = np.random.uniform(-np.pi, np.pi)
        eta_j = np.random.normal(0, 1.2)
        particles.extend(_gen_jet(pt_j, phi_j, eta_j, n_particles=np.random.randint(4, 8)))

    # Hadronic W: 2 more jets
    for _ in range(2):
        pt_j = np.random.exponential(35) + 20
        phi_j = np.random.uniform(-np.pi, np.pi)
        eta_j = np.random.normal(0, 1.5)
        particles.extend(_gen_jet(pt_j, phi_j, eta_j, n_particles=np.random.randint(3, 6)))

    return particles


def _gen_qcd_jets() -> list[dict[str, Any]]:
    """Generate a QCD multijet event."""
    particles = []
    n_jets = np.random.randint(2, 5)
    for _ in range(n_jets):
        pt_j = np.random.exponential(60) + 30
        phi_j = np.random.uniform(-np.pi, np.pi)
        eta_j = np.random.normal(0, 1.5)
        particles.extend(_gen_jet(pt_j, phi_j, eta_j, n_particles=np.random.randint(5, 12)))
    return particles


def _gen_lepton_pair(lep1: str, lep2: str, m_inv: float) -> list[dict[str, Any]]:
    """Generate a lepton pair from a resonance with given invariant mass."""
    # Decay in rest frame
    m1 = PARTICLES[lep1]["mass"]
    m2 = PARTICLES[lep2]["mass"]
    if m_inv < m1 + m2:
        m_inv = m1 + m2 + 0.1

    p_star = np.sqrt(max((m_inv**2 - (m1 + m2)**2) * (m_inv**2 - (m1 - m2)**2), 0)) / (2 * m_inv)

    # Random direction in rest frame
    cos_theta = np.random.uniform(-1, 1)
    sin_theta = np.sqrt(1 - cos_theta**2)
    phi_decay = np.random.uniform(-np.pi, np.pi)

    px1 = p_star * sin_theta * np.cos(phi_decay)
    py1 = p_star * sin_theta * np.sin(phi_decay)
    pz1 = p_star * cos_theta

    # Boost along z (simulate longitudinal boost from pp collision)
    rapidity = np.random.normal(0, 2.0)
    pt_boost = np.random.exponential(15)
    phi_boost = np.random.uniform(-np.pi, np.pi)

    # Apply longitudinal boost
    e1 = np.sqrt(px1**2 + py1**2 + pz1**2 + m1**2)
    e2 = np.sqrt(px1**2 + py1**2 + pz1**2 + m2**2)

    beta = np.tanh(rapidity)
    gamma = 1.0 / np.sqrt(max(1 - beta**2, 1e-10))

    pz1_lab = gamma * (pz1 + beta * e1)
    pz2_lab = gamma * (-pz1 + beta * e2)

    # Add transverse boost
    px1_lab = px1 + pt_boost * np.cos(phi_boost) * 0.5
    py1_lab = py1 + pt_boost * np.sin(phi_boost) * 0.5
    px2_lab = -px1 + pt_boost * np.cos(phi_boost) * 0.5
    py2_lab = -py1 + pt_boost * np.sin(phi_boost) * 0.5

    return [
        _make_particle(lep1, px1_lab, py1_lab, pz1_lab),
        _make_particle(lep2, px2_lab, py2_lab, pz2_lab),
    ]


def _gen_jet(pt: float, phi: float, eta: float, n_particles: int = 6) -> list[dict[str, Any]]:
    """Generate jet particles clustered around a direction."""
    particles = []
    for _ in range(n_particles):
        # Smear around jet axis
        d_eta = np.random.normal(0, 0.15)
        d_phi = np.random.normal(0, 0.15)
        frac = np.random.exponential(0.3)
        frac = min(frac, 1.0)

        p_pt = pt * frac
        p_eta = eta + d_eta
        p_phi = phi + d_phi

        px = p_pt * np.cos(p_phi)
        py = p_pt * np.sin(p_phi)
        pz = p_pt * np.sinh(p_eta)

        ptype = np.random.choice(
            ["pion+", "pion-", "pion0", "kaon+", "kaon-", "proton"],
            p=[0.30, 0.30, 0.15, 0.08, 0.08, 0.09],
        )
        particles.append(_make_particle(ptype, px, py, pz))
    return particles


def _gen_soft_particle() -> dict[str, Any]:
    """Generate a soft underlying event particle."""
    pt = np.random.exponential(0.8) + 0.2
    phi = np.random.uniform(-np.pi, np.pi)
    eta = np.random.normal(0, 2.5)
    px = pt * np.cos(phi)
    py = pt * np.sin(phi)
    pz = pt * np.sinh(eta)
    ptype = np.random.choice(
        ["pion+", "pion-", "pion0", "kaon+", "kaon-"],
        p=[0.35, 0.35, 0.15, 0.075, 0.075],
    )
    return _make_particle(ptype, px, py, pz)


def generate_batch(n: int = 20) -> list[dict[str, Any]]:
    """Generate a batch of random collision events.

    Args:
        n: Number of events to generate.

    Returns:
        List of event dicts.
    """
    return [generate_event() for _ in range(n)]
