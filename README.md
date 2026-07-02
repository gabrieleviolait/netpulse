# NetPulse

NetPulse is a desktop network utility with a simple GUI built in Python.

Main goals:
- discover local devices from ARP cache
- run fast port scan checks through Nmap
- translate common service names through a local signatures database
- export scan output to PDF

Important: this project is for authorized defensive use only.
Read the full policy in DISCLAIMER.md.

## Features

- Local network device discovery (ARP cache based)
- Target selection dialog for server checks
- Fast Nmap scan execution from GUI
- Signature mapping from signatures.json
- PDF report export
- One-click Windows launcher via start_netpulse.bat

## Project Structure

- netpulse.py: main GUI application
- start_netpulse.bat: Windows launcher (dependency checks + app start)
- signatures.json: local service signature metadata
- DISCLAIMER.md: legal and responsible-use notice

## Requirements

- Windows 10/11 (tested target)
- Python 3.10+
- Nmap installed and available in PATH (required for server scan feature)
- Internet access on first run for Python package installation via launcher

Python packages used by the app:
- customtkinter
- fpdf
- scapy

## Quick Start (Windows)

1. Install Python 3 and enable Add Python to PATH.
2. Install Nmap from https://nmap.org/download.html and ensure nmap command works in terminal.
3. Run start_netpulse.bat.

The launcher will:
- find a usable Python interpreter
- verify pip
- install missing Python dependencies
- warn if Nmap is missing
- start the GUI

## Manual Start (optional)

Install dependencies:

pip install customtkinter fpdf scapy

Run app:

python netpulse.py

## Security and Legal Notes

- Use NetPulse only on systems and networks you own or where you have explicit written authorization.
- Unauthorized network scanning may violate laws, contracts, or acceptable use policies.
- The author and contributors are not liable for misuse.
- If you are unsure whether you are authorized, do not run scans.

See DISCLAIMER.md for full details.

## Known Limitations

- Nmap-based checks require Nmap in PATH.
- ARP cache discovery visibility depends on host/network activity.
- Some scan operations may require elevated privileges depending on system policy.

## Publishing Checklist (GitHub)

Before publishing publicly, review:
- Disclaimer text and local legal requirements
- License file (recommended: MIT or Apache-2.0)
- Repository visibility and intended audience
- Issues and contribution policy

## Credits

Project credits and website are visible in the GUI footer.
