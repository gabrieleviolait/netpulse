import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import time
import subprocess
import json
import os
import webbrowser
from fpdf import FPDF
# Nota: Scapy richiede privilegi di amministratore su Windows/Mac
try:
    from scapy.all import sr1, IP, ICMP
except ImportError:
    print("Installa scapy con: pip install scapy")

class TargetSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, options):
        super().__init__(parent)
        self.title("Target Nmap")
        self.geometry("400x200")
        self.result = None
        
        self.lbl = ctk.CTkLabel(self, text="Seleziona o inserisci l'IP/Dominio da scansionare:")
        self.lbl.pack(pady=(20, 10))
        
        self.combo = ctk.CTkComboBox(self, values=options, width=300)
        if options:
            self.combo.set(options[-1]) # Suggerisce l'ultimo IP trovato o il default
        self.combo.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="Inizia Scansione", command=self.on_ok)
        self.btn.pack(pady=20)
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
        
    def on_ok(self):
        self.result = self.combo.get()
        self.destroy()

class NetPulseGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurazione Finestra
        self.title("NetPulse - Super Scanner")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Stile Avanzato
        self.configure(fg_color="#1e1e2e") # Tema Dracula-like base

        # Layout Principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Titolo con stile
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=20, pady=(40, 10))
        lbl_title = ctk.CTkLabel(self.title_frame, text="NetPulse", font=("Outfit", 42, "bold"), text_color="#89b4fa")
        lbl_title.pack(side="left")

        # Descrizione Semplice
        lbl_desc = ctk.CTkLabel(self, text="Seleziona un'operazione per iniziare l'analisi", font=("Inter", 16), text_color="#bac2de")
        lbl_desc.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Pulsanti di Scelta con stile migliorato
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10)

        self.btn_wifi = ctk.CTkButton(btn_frame, text="📡 Trova Dispositivi WiFi", 
                                      command=self.start_ping_scan, 
                                      width=220, height=50,
                                      font=("Inter", 14, "bold"),
                                      fg_color="#cba6f7", hover_color="#b4befe", text_color="#11111b",
                                      corner_radius=12)
        self.btn_wifi.grid(row=0, column=0, padx=15, pady=10)

        self.btn_server = ctk.CTkButton(btn_frame, text="⚡ Analisi Sicurezza (Nmap)", 
                                        command=self.start_port_scan, 
                                        width=220, height=50,
                                        font=("Inter", 14, "bold"),
                                        fg_color="#89b4fa", hover_color="#74c7ec", text_color="#11111b",
                                        corner_radius=12)
        self.btn_server.grid(row=0, column=1, padx=15, pady=10)
        
        self.btn_pdf = ctk.CTkButton(btn_frame, text="📄 Salva Report PDF", 
                                        command=self.export_pdf, 
                                        width=220, height=50,
                                        font=("Inter", 14, "bold"),
                                        fg_color="#a6e3a1", hover_color="#94e2d5", text_color="#11111b",
                                        corner_radius=12,
                                        state="disabled") # Disabilitato fino a prima scansione
        self.btn_pdf.grid(row=0, column=2, padx=15, pady=10)

        # Area Risultati con effetto terminale
        self.result_area = ctk.CTkTextbox(self, font=("Consolas", 14), 
                                          fg_color="#181825", text_color="#a6adc8",
                                          border_color="#313244", border_width=2,
                                          corner_radius=15)
        self.result_area.grid(row=3, column=0, sticky="nsew", padx=40, pady=(20, 10))
        
        # Credits Footer
        self.lbl_credits = ctk.CTkLabel(self, text="Credits: www.gabrieleviola.it", font=("Inter", 12, "underline"), text_color="#89b4fa", cursor="hand2")
        self.lbl_credits.grid(row=4, column=0, pady=(0, 10))
        self.lbl_credits.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.gabrieleviola.it/"))
        
        # Input target (nascosto di default, potremmo espanderlo in futuro)
        self.target_ip = "127.0.0.1" 
        
        # Caricamento Firme
        self.signatures = self.load_signatures()
        self.scan_results = [] # Per il PDF
        self.discovered_ips = ["127.0.0.1", "google.com"]

    def load_signatures(self):
        try:
            with open("signatures.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.log("⚠️ Database firme (signatures.json) non trovato. Verranno mostrati risultati grezzi.")
            return {}

    def log(self, message):
        """Aggiunge testo all'area risultati con timestamp e lo salva per il PDF"""
        time_str = time.strftime("%H:%M:%S")
        log_msg = f"[{time_str}] {message}\n"
        self.result_area.insert("end", log_msg)
        self.result_area.see("end")
        self.scan_results.append(log_msg.strip())
        # Abilita il pulsante PDF se ci sono risultati
        if len(self.scan_results) > 0 and self.btn_pdf.cget("state") == "disabled":
            self.btn_pdf.configure(state="normal")

    def start_ping_scan(self):
        """Esegue una scansione dei dispositivi locali via ARP"""
        self.log("🚀 Avvio rilevamento dispositivi sulla rete locale...")
        
        # Disabilita bottoni durante la scansione
        self.btn_wifi.configure(state="disabled")
        self.btn_server.configure(state="disabled")
        
        threading.Thread(target=self.run_ping_scan_logic, daemon=True).start()

    def run_ping_scan_logic(self):
        self.log("🔎 Lettura della cache ARP di sistema in corso...")
        time.sleep(1)
        try:
            # Usa arp -a per leggere i dispositivi noti sulla rete locale
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=False)
            output = result.stdout
            
            dispositivi_trovati = 0
            for line in output.split('\n'):
                line = line.strip()
                # Cerchiamo le righe che contengono IP, MAC e il tipo (es. "dinamico" o "dynamic")
                if line and len(line.split()) >= 3 and ("dynamic" in line.lower() or "dinamico" in line.lower()):
                    parts = line.split()
                    ip = parts[0]
                    mac = parts[1]
                    # Filtra indirizzi di broadcast tipici
                    if not ip.startswith("224.") and not ip.startswith("239.") and ip != "255.255.255.255":
                        self.log(f"💻 Dispositivo: IP {ip} (MAC: {mac})")
                        if ip not in self.discovered_ips:
                            self.discovered_ips.append(ip)
                        dispositivi_trovati += 1
            
            if dispositivi_trovati == 0:
                self.log("⚠️ Nessun dispositivo trovato nella cache. (Assicurati di essere connesso)")
            else:
                self.log(f"✅ Trovati {dispositivi_trovati} dispositivi sulla rete locale.")
                
        except Exception as e:
            self.log(f"❌ Errore durante la ricerca dispositivi: {e}")
            
        self.log("✅ Scansione WiFi completata.")
        
        # Riabilita bottoni
        self.btn_wifi.configure(state="normal")
        self.btn_server.configure(state="normal")

    def start_port_scan(self):
        """Avvia una scansione delle porte con Nmap"""
        dialog = TargetSelectionDialog(self, self.discovered_ips)
        target = dialog.result
        if not target:
            return
            
        self.log(f"🔍 Analisi sicurezza Nmap per: {target}")
        self.btn_wifi.configure(state="disabled")
        self.btn_server.configure(state="disabled")
        
        threading.Thread(target=self.run_nmap_logic, args=(target,), daemon=True).start()

    def run_nmap_logic(self, target):
        self.log("🔎 Avvio Nmap in background... (potrebbe richiedere qualche secondo)")
        try:
            # Esegui nmap -F (Fast scan)
            result = subprocess.run(['nmap', '-F', target], capture_output=True, text=True, check=False)
            
            output = result.stdout
            
            if "Nmap done" not in output:
                self.log(f"❌ Errore Nmap o target non raggiungibile.")
                self.log(output)
            else:
                self.log("📊 Risultati Nmap tradotti:")
                lines = output.split('\n')
                port_found = False
                for line in lines:
                    if '/tcp' in line or '/udp' in line:
                        port_found = True
                        parts = line.split()
                        if len(parts) >= 3:
                            port_info = parts[0]
                            state = parts[1]
                            service = parts[2]
                            
                            # Traduzione usando le firme
                            if service in self.signatures:
                                sig = self.signatures[service]
                                self.log(f"  • {port_info} [{state}] - {sig['desc']} -> {sig['status']}")
                            else:
                                self.log(f"  • {port_info} [{state}] - Servizio: {service} (Sconosciuto al DB locale)")
                
                if not port_found:
                    self.log("  Nessuna porta aperta trovata.")
                    
        except FileNotFoundError:
            self.log("❌ ERRORE: Nmap non è installato o non è nel PATH di sistema.")
            self.log("Scaricalo da https://nmap.org/download.html")
        except Exception as e:
            self.log(f"❌ ERrore imprevisto: {e}")
            
        self.log("✅ Analisi Server completata.")
        self.btn_wifi.configure(state="normal")
        self.btn_server.configure(state="normal")
        
    def export_pdf(self):
        """Genera un PDF con i risultati della scansione"""
        if not self.scan_results:
            messagebox.showwarning("Attenzione", "Nessun risultato da esportare.")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Salva Report PDF",
            initialfile="NetPulse_Report.pdf"
        )
        
        if not filepath:
            return
            
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Titolo
            pdf.set_font("Arial", 'B', 24)
            pdf.set_text_color(41, 128, 185) # Blu
            pdf.cell(200, 20, txt="NetPulse - Report di Sicurezza", ln=True, align='C')
            
            # Data
            pdf.set_font("Arial", 'I', 12)
            pdf.set_text_color(100, 100, 100)
            date_str = time.strftime("%Y-%m-%d %H:%M:%S")
            pdf.cell(200, 10, txt=f"Generato il: {date_str}", ln=True, align='C')
            pdf.ln(10)
            
            # Contenuto
            pdf.set_font("Courier", size=10)
            pdf.set_text_color(0, 0, 0)
            
            for line in self.scan_results:
                # Gestione dei caratteri unicode semplici
                clean_line = line.replace('✅', '[OK]').replace('❌', '[ERR]').replace('🚀', '[START]').replace('📱', '[MOB]').replace('💻', '[PC]').replace('🔍', '[SCAN]').replace('🔎', '[...]').replace('📊', '[RES]').replace('•', '-')
                # Codifica in latin-1 per fpdf base, ignora i non compatibili
                clean_line = clean_line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 8, txt=clean_line)
            
            # Credits Footer nel PDF
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(41, 128, 185) # Blu link
            pdf.cell(0, 10, txt="Credits: www.gabrieleviola.it", ln=True, align='C', link="https://www.gabrieleviola.it/")
                
            pdf.output(filepath)
            messagebox.showinfo("Successo", f"Report salvato con successo in:\n{filepath}")
            self.log(f"📄 Report PDF generato: {filepath}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile generare il PDF:\n{e}")
            self.log(f"❌ Errore generazione PDF: {e}")

if __name__ == "__main__":
    app = NetPulseGUI()
    app.mainloop()
