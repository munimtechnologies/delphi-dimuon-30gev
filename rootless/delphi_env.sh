# delphi_env 0.1.1 -- sourced INSIDE the DELPHI image after the login profile (amendment 0.42).
# Only puts the image's own DELPHI tools on PATH when the login profile did not; it changes no
# analysis code, switch, threshold or blinding rule. Prints nothing when sourced quietly.
# Part of the open DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
_dt_ok(){ command -v dellib >/dev/null 2>&1 && command -v cernlib >/dev/null 2>&1; }
DELPHI_ENV_SOURCE=login
if ! _dt_ok && [ -r /etc/profile.d/delphi.sh ]; then
  . /etc/profile.d/delphi.sh
  DELPHI_ENV_SOURCE=profile.d/delphi.sh
fi
if ! _dt_ok; then
  for _s in /delphi/setup.sh /delphi/*/setup.sh /delphi/*/*/setup.sh /delphi/*/*/*/setup.sh; do
    [ -r "$_s" ] || continue
    . "$_s"
    if _dt_ok; then DELPHI_ENV_SOURCE=$_s; break; fi
  done
fi
if ! _dt_ok; then DELPHI_ENV_SOURCE=none; fi
export DELPHI_ENV_SOURCE
export DELPHI_DATA_ROOT=${DELPHI_DATA_ROOT:-/eos/opendata/delphi}
unset _s
unset -f _dt_ok
