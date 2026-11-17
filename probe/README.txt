delphi-probe 0.1.0 (MV2 of Munim, Inc.; made with AI agents; Apache-2.0)

Question this serves: does the 30 GeV opposite-sign dimuon excess that a re-analysis of
archived ALEPH data found in Z -> b bbar events (A. Heister, arXiv:1610.06536: 32 +- 11
events at 30.40 +- 0.46 GeV, width 1.78 +- 1.14 GeV, ~5 sigma local, ~3 sigma global)
also appear in DELPHI's data from the same LEP1 Z-pole running? DELPHI released its full
data and software in 2024 (CERN Open Data, CC0). As far as a prior-art search on
2026-11-17 found, no DELPHI or OPAL test of this excess exists; L3 (arXiv:1905.01111)
is the only other LEP experiment that has looked.

This job only checks feasibility: the DELPHI container (AlmaLinux 9), xrootd access to
the 1994 short DST (nickname short94_c2, ~429 files, ~90 MB each), the skelana example
build, the nickname catalogue, and the skelana manual / data policy as text. It reads
public data only and does not look at any dimuon mass.

Run: sed 's/\r$//' /work/probe.sh > /tmp/probe.sh && bash /tmp/probe.sh
Outputs: /out/probe/
