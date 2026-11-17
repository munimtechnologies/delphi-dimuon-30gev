"""fadgen: write Pythia 8 events as DELSIM external-generator input ("FADGEN", fort.26).

Format (as implemented by hepmc2fadgen.cpp in delphi-fullDST-edm4hep/delphi-sim-pipeline):
little-endian Fortran-unformatted sequential records; per event
  int32 reclen (= 4 + 60 N), int32 N, then per particle K(1..5) int32, P(1..5) float32,
  V(1..5) float32, then int32 reclen again; the file ends with the triple 4, 0, 4.
K(1): 1 final, 4 V0 left for DELSIM to decay, 11 decayed hadron or tau, 21 documentation.
K(2) PDG id, K(3) mother, K(4)/K(5) first/last daughter (1-based, 0 if none).
P: px, py, pz, E, m (GeV). V: production vertex x, y, z (mm), t (mm/c), 0.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import struct

import numpy as np

V0_IDS = {310, 3122, 3112, 3222, 3312, 3322}
REC = np.dtype([('k', '<i4', (5,)), ('p', '<f4', (5,)), ('v', '<f4', (5,))])


def lujets_from_pythia(ev):
    """Pythia 8 event record (entries 1..size-1 keep their numbering) -> K, P, V arrays."""
    n = ev.size() - 1
    K = np.zeros((n, 5), np.int32)
    P = np.zeros((n, 5), np.float32)
    V = np.zeros((n, 5), np.float32)
    for i in range(1, ev.size()):
        p = ev[i]
        a = p.idAbs()
        dl = list(p.daughterList())
        if p.isFinal():
            k1 = 4 if a in V0_IDS else 1
        elif (p.isHadron() or a == 15) and len(dl) > 0:
            k1 = 11
        else:
            k1 = 21
        r = i - 1
        K[r] = (k1, p.id(), max(p.mother1(), 0), min(dl) if dl else 0, max(dl) if dl else 0)
        P[r] = (p.px(), p.py(), p.pz(), p.e(), p.m())
        V[r] = (p.xProd(), p.yProd(), p.zProd(), p.tProd(), 0.0)
    return K, P, V


def write_event(f, K, P, V):
    n = len(K)
    if n > 4000:
        raise ValueError('more than 4000 entries')
    buf = np.zeros(n, REC)
    buf['k'] = K
    buf['p'] = P
    buf['v'] = V
    rec = 4 + 60 * n
    f.write(struct.pack('<ii', rec, n))
    f.write(buf.tobytes())
    f.write(struct.pack('<i', rec))


def write_end(f):
    f.write(struct.pack('<iii', 4, 0, 4))


def read_fadgen(path):
    """Yield (K, P, V) per event; stops at the N = 0 end marker. Raises on corruption."""
    with open(path, 'rb') as f:
        while True:
            head = f.read(8)
            if len(head) < 8:
                raise ValueError('file ended without end marker')
            rec, n = struct.unpack('<ii', head)
            if rec != 4 + 60 * n:
                raise ValueError('bad record length %d for N=%d' % (rec, n))
            body = f.read(60 * n)
            (tail,) = struct.unpack('<i', f.read(4))
            if tail != rec:
                raise ValueError('trailing length mismatch')
            if n == 0:
                return
            arr = np.frombuffer(body, REC)
            yield arr['k'].copy(), arr['p'].copy(), arr['v'].copy()
