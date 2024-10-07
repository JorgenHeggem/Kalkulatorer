import os
import sys
import customtkinter as ctk     # CustomTkinter for å style GUI
from tkinter import messagebox  # For å vise feilmeldinger
import cmath    # For komplekse tall
import math     # For matematiske funksjoner

# Konfigurer CustomTkinter
ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"


class KalkulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator")
        self.root.geometry("700x800")

        # GUI-tilstand (variabler for inputfeltene)
        self.u_input = None
        self.i_input = None
        self.r_input = None
        self.p_input = None
        self.vin_input = None
        self.iin_input = None
        self.r_input1 = None
        self.r_input2 = None
        self.r_input3 = None
        self.form_valg = "Polar"  # Standard for AC form er polar

        # Opprett GUI-elementer
        self.lag_gui()

    def lag_gui(self):
        # Hovedramme som inneholder både innholdet og notatene
        hovedramme = ctk.CTkFrame(self.root)
        hovedramme.pack(fill="both", expand=True)
        hovedramme.configure(fg_color="transparent")

        # Venstre ramme for resten av grensesnittet
        venstre_ramme = ctk.CTkFrame(hovedramme)
        venstre_ramme.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        venstre_ramme.configure(fg_color="transparent")

        # Høyre ramme for notater
        hoyre_ramme = ctk.CTkFrame(hovedramme)  
        hoyre_ramme.pack(side="right", fill="both", expand=True, padx=0, pady=0)    
        hoyre_ramme.configure(fg_color="transparent")   

        # Ramme for valg av strømtype og beregning
        valg_ramme = ctk.CTkFrame(venstre_ramme)
        valg_ramme.pack(pady=5)
        valg_ramme.configure(fg_color="transparent")
        
        # Valg for strømtype
        ctk.CTkLabel(valg_ramme, text="Velg strømtype:", font=("Arial", 14, "bold")).pack(pady=1)  
        self.kalk_valg = ctk.CTkComboBox(valg_ramme, values=["DC", "AC"], command=self.oppdater_kalkulator)
        self.kalk_valg.pack(pady=5)
        self.kalk_valg.set("DC")

        # Valg av beregning
        ctk.CTkLabel(valg_ramme, text="Velg beregning:", font=("Arial", 14, "bold")).pack(pady=1)
        self.beregningsvalg = ctk.CTkComboBox(valg_ramme, values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR"], command=self.oppdater_beregning)
        self.beregningsvalg.pack(pady=5)
        self.beregningsvalg.set("Ohms lov")

        # Valg for form (kun for AC)
        self.form_label = ctk.CTkLabel(valg_ramme, text="Velg form:", font=("Arial", 14, "bold"))
        self.form_valg = ctk.CTkComboBox(valg_ramme, values=["Polar", "Rektangulær"], command=self.oppdater_beregning)
        self.form_label.pack_forget()  # Skjult som standard for DC
        self.form_valg.pack_forget()

        # Valg for komponent (kun for AC)
        self.komponent_label = ctk.CTkLabel(valg_ramme, text="Velg komponent:", font=("Arial", 14, "bold"))
        self.komponent_valg = ctk.CTkComboBox(valg_ramme, values=["Kondensator", "Spole"], command=self.oppdater_beregning)
        self.komponent_label.pack_forget()
        self.komponent_valg.pack_forget()

        # Ramme for input-felt
        self.input_ramme = ctk.CTkFrame(venstre_ramme)
        self.input_ramme.pack(pady=10)
        self.input_ramme.configure(fg_color="transparent")

        # Resultat-etikett
        self.resultat_label = ctk.CTkLabel(venstre_ramme, text="Resultat:", font=("Arial", 12))
        self.resultat_label.pack(pady=10)

        # Kopier-knapp
        self.kopier_knapp = ctk.CTkButton(venstre_ramme, text="Kopier resultat", command=self.kopier_resultat)
        self.kopier_knapp.pack(pady=10)

        # Etikett for notater i høyre ramme
        ctk.CTkLabel(hoyre_ramme, text="Notater:", font=("Arial", 14, "bold")).pack(pady=0)

        # Tekstboks for notater
        self.notater_boks = ctk.CTkTextbox(hoyre_ramme, font=("Arial", 14))
        self.notater_boks.pack(fill="both", expand=True, padx=10, pady=10)

        # Legg til tekst ved oppstart
        prefiks_tekst = "Støttede prefikser: T, G, M, k, m, µ, n\n\n"
        self.notater_boks.insert("0.0", prefiks_tekst)

        # Start med standard beregning for DC
        self.oppdater_kalkulator()

    def konverter_prefiks(self, verdi):
        verdi = verdi.strip().replace(',', '.')
        try:
            if 'k' in verdi:
                return float(verdi.replace('k', '')) * 1e3 # k = kilo
            elif 'm' in verdi and 'µ' not in verdi:
                return float(verdi.replace('m', '')) * 1e-3 # m = milli
            elif 'µ' in verdi:
                return float(verdi.replace('µ', '')) * 1e-6 # µ = mikro
            elif 'g' in verdi: 
                return float(verdi.replace('g', '')) * 1e9 # g = giga
            elif 'M' in verdi:
                return float(verdi.replace('M', '')) * 1e6 # M = mega
            else:
                return float(verdi) # Ingen prefiks
        except ValueError:
            raise ValueError("Ugyldig verdi for prefiks!")

    def formater_resultat(self, verdi):
        enheter = [
            (1e-9, 'n'), (1e-6, 'µ'), (1e-3, 'm'), (1, ''), 
            (1e3, 'k'), (1e6, 'M'), (1e9, 'G'), (1e12, 'T') 
        ]
        for faktor, enhet in enheter:
            if abs(verdi) < faktor * 1000:
                return f"{verdi / faktor:.2f}".replace('.', ',') + f" {enhet}" # Returner formatert verdi med prefiks
        return f"{verdi:.2f}".replace('.', ',')

    def oppdater_kalkulator(self, event=None): 
        """Oppdater kalkulatortype og beregning basert på valgt strømtype."""
        kalk_type = self.kalk_valg.get()
        beregning = self.beregningsvalg.get()

        # Fjern eksisterende inputfelt
        for widget in self.input_ramme.winfo_children():
            widget.destroy()

        if kalk_type == "DC":
            self.root.title("DC Kalkulator")
            self.form_label.pack_forget()   # Skjuler form-valget for DC
            self.form_valg.pack_forget()
            self.komponent_label.pack_forget()  # Skjuler komponent-valget for DC
            self.komponent_valg.pack_forget()
            self.beregningsvalg.configure(values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR"])    # Fjern beregning for kapasitans og induktans
            self.beregningsvalg.set(beregning or "Ohms lov")
        elif kalk_type == "AC":
            self.root.title("AC Kalkulator")
            self.form_label.pack(pady=5)    # Vis form-valget for AC
            self.form_valg.pack(pady=5)
            self.beregningsvalg.configure(values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR", "Kap og Ind"])  # Legg til beregning for kapasitans og induktans
            self.beregningsvalg.set(beregning or "Ohms lov")

        # Oppdater basert på den nye kalkulatortypen og beregningen
        self.oppdater_beregning()

    def oppdater_beregning(self, event=None):
        """Oppdater input-felt basert på valgt beregning og strømtype."""
        for widget in self.input_ramme.winfo_children():
            widget.destroy()
            
        if hasattr(self, 'form_valg'):  # Sjekk om form-valgboksen allerede finnes og skjul den om nødvendig
            self.form_valg.pack_forget()  # Skjul den eksisterende komboboksen for formvalg hvis den finnes
            
        kalk_type = self.kalk_valg.get()
        beregning = self.beregningsvalg.get()
        self.resultat_label.configure(text="")
                    
        if kalk_type == "DC":
            self.root.title("DC Kalkulator")
            self.form_label.pack_forget()  # Skjuler form-valget for DC
            self.form_valg.pack_forget()
            self.komponent_label.pack_forget()  # Skjuler komponent-valget for DC
            self.komponent_label.pack_forget()
            self.beregningsvalg.configure(values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR"])

            if beregning == "Ohms lov":
                # Ohms lov input-felt for DC
                ctk.CTkLabel(self.input_ramme, text="Spenning (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.u_input = ctk.CTkEntry(self.input_ramme)
                self.u_input.grid(row=0, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Strøm (A):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.i_input = ctk.CTkEntry(self.input_ramme)
                self.i_input.grid(row=1, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input = ctk.CTkEntry(self.input_ramme)
                self.r_input.grid(row=2, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Effekt (W):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input = ctk.CTkEntry(self.input_ramme)
                self.p_input.grid(row=3, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_ohms_lov)
                beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

            elif beregning == "Seriekobling":
                ctk.CTkLabel(self.input_ramme, text="Motstand 1 (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = ctk.CTkEntry(self.input_ramme)
                self.r_input1.grid(row=0, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 2 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = ctk.CTkEntry(self.input_ramme)
                self.r_input2.grid(row=1, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 3 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = ctk.CTkEntry(self.input_ramme)
                self.r_input3.grid(row=2, column=1, padx=10, pady=5)
                
                ctk.CTkLabel(self.input_ramme, text="Motstand 4 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.r_input4 = ctk.CTkEntry(self.input_ramme)
                self.r_input4.grid(row=3, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_seriekobling)
                beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

            elif beregning == "Parallellkobling":
                ctk.CTkLabel(self.input_ramme, text="Motstand 1 (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = ctk.CTkEntry(self.input_ramme)
                self.r_input1.grid(row=0, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 2 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = ctk.CTkEntry(self.input_ramme)
                self.r_input2.grid(row=1, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 3 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = ctk.CTkEntry(self.input_ramme)
                self.r_input3.grid(row=2, column=1, padx=10, pady=5)
                
                ctk.CTkLabel(self.input_ramme, text="Motstand 4 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.r_input4 = ctk.CTkEntry(self.input_ramme)
                self.r_input4.grid(row=3, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_parallellkobling)
                beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

            elif beregning == "VDR":
                ctk.CTkLabel(self.input_ramme, text="Inngangsspenning (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.vin_input = ctk.CTkEntry(self.input_ramme)
                self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 1 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = ctk.CTkEntry(self.input_ramme)
                self.r_input1.grid(row=1, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 2 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = ctk.CTkEntry(self.input_ramme)
                self.r_input2.grid(row=2, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 3 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = ctk.CTkEntry(self.input_ramme)
                self.r_input3.grid(row=3, column=1, padx=10, pady=5)
                
                ctk.CTkLabel(self.input_ramme, text="Motstand 4 (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input4 = ctk.CTkEntry(self.input_ramme)
                self.r_input4.grid(row=4, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_vdr)
                beregn_knapp.grid(row=5, column=0, columnspan=2, pady=20)

            elif beregning == "CDR":
                ctk.CTkLabel(self.input_ramme, text="Inngangsstrøm (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.iin_input = ctk.CTkEntry(self.input_ramme)
                self.iin_input.grid(row=0, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 1 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = ctk.CTkEntry(self.input_ramme)
                self.r_input1.grid(row=1, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 2 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = ctk.CTkEntry(self.input_ramme)
                self.r_input2.grid(row=2, column=1, padx=10, pady=5)

                ctk.CTkLabel(self.input_ramme, text="Motstand 3 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = ctk.CTkEntry(self.input_ramme)
                self.r_input3.grid(row=3, column=1, padx=10, pady=5)
                
                ctk.CTkLabel(self.input_ramme, text="Motstand 4 (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input4 = ctk.CTkEntry(self.input_ramme)
                self.r_input4.grid(row=4, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_cdr)
                beregn_knapp.grid(row=5, column=0, columnspan=2, pady=20)


        elif kalk_type == "AC":
            self.root.title("AC Kalkulator")
            self.beregningsvalg.configure(values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR", "Kap og Ind"])

            if beregning == "Ohms lov":
                # Skjul komponent-valg og vis form-valg på samme sted
                self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack_forget()  # Skjuler etiketten for komponent
                self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack(pady=5)  # Vis formetiketten for AC
                self.form_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC
                if self.form_valg.get() == "Polar":
                    ctk.CTkLabel(self.input_ramme, text="Spenningens magnitude (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.u_input = ctk.CTkEntry(self.input_ramme)
                    self.u_input.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Spenningens fase (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.u_fase_input = ctk.CTkEntry(self.input_ramme)
                    self.u_fase_input.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Strømmens magnitude (A):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.i_input = ctk.CTkEntry(self.input_ramme)
                    self.i_input.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Strømmens fase (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.i_fase_input = ctk.CTkEntry(self.input_ramme)
                    self.i_fase_input.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedansens magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.r_input = ctk.CTkEntry(self.input_ramme)
                    self.r_input.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedansens fase (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.z_fase_input = ctk.CTkEntry(self.input_ramme)
                    self.z_fase_input.grid(row=5, column=1, padx=10, pady=5)
                else:
                    ctk.CTkLabel(self.input_ramme, text="Spenningens reelle del (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.u_input = ctk.CTkEntry(self.input_ramme)
                    self.u_input.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Spenningens imaginære del (V):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.u_fase_input = ctk.CTkEntry(self.input_ramme)
                    self.u_fase_input.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Strømmens reelle del (A):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.i_input = ctk.CTkEntry(self.input_ramme)
                    self.i_input.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Strømmens imaginære del (A):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.i_fase_input = ctk.CTkEntry(self.input_ramme)
                    self.i_fase_input.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedansens reelle del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.r_input = ctk.CTkEntry(self.input_ramme)
                    self.r_input.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedansens imaginære del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.z_fase_input = ctk.CTkEntry(self.input_ramme)
                    self.z_fase_input.grid(row=5, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_ohms_lov)
                beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)
                
            elif beregning == "Seriekobling":
                # Skjul komponent-valg og vis form-valg på samme sted
                self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack_forget()  # Skjuler etiketten for komponent
                self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack(pady=5)  # Vis formetiketten for AC
                self.form_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC
                if self.form_valg.get() == "Polar":
                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.r_input3 = ctk.CTkEntry(self.input_ramme)
                    self.r_input3.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.p_input3 = ctk.CTkEntry(self.input_ramme)
                    self.p_input3.grid(row=5, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 magnitude (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.r_input4 = ctk.CTkEntry(self.input_ramme)
                    self.r_input4.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 fase (grader):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.p_input4 = ctk.CTkEntry(self.input_ramme)
                    self.p_input4.grid(row=7, column=1, padx=10, pady=5)
                else:
                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 reell del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.r_input3 = ctk.CTkEntry(self.input_ramme)
                    self.r_input3.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 imaginær del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.p_input3 = ctk.CTkEntry(self.input_ramme)
                    self.p_input3.grid(row=5, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 reell del (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.r_input4 = ctk.CTkEntry(self.input_ramme)
                    self.r_input4.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 imaginær del (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.p_input4 = ctk.CTkEntry(self.input_ramme)
                    self.p_input4.grid(row=7, column=1, padx=10, pady=5)
                    
                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_seriekobling)
                beregn_knapp.grid(row=8, column=0, columnspan=2, pady=20)
                
            elif beregning == "Parallellkobling":
                # Skjul komponent-valg og vis form-valg på samme sted
                self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack_forget()  # Skjuler etiketten for komponent
                self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack(pady=5)  # Vis formetiketten for AC
                self.form_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC
                
                if self.form_valg.get() == "Polar":
                    # Bruk grid til å plassere input-felt for polar form
                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.r_input3 = ctk.CTkEntry(self.input_ramme)
                    self.r_input3.grid(row=5, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.p_input3 = ctk.CTkEntry(self.input_ramme)
                    self.p_input3.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 magnitude (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.r_input4 = ctk.CTkEntry(self.input_ramme)
                    self.r_input4.grid(row=7, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 fase (grader):").grid(row=8, column=0, padx=10, pady=5, sticky="e")
                    self.p_input4 = ctk.CTkEntry(self.input_ramme)
                    self.p_input4.grid(row=8, column=1, padx=10, pady=5)
                    
                else:
                    # Bruk grid til å plassere input-felt for rektangulær form
                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 reell del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.r_input3 = ctk.CTkEntry(self.input_ramme)
                    self.r_input3.grid(row=5, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 imaginær del (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.p_input3 = ctk.CTkEntry(self.input_ramme)
                    self.p_input3.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 reell del (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.r_input4 = ctk.CTkEntry(self.input_ramme)
                    self.r_input4.grid(row=7, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 4 imaginær del (Ω):").grid(row=8, column=0, padx=10, pady=5, sticky="e")
                    self.p_input4 = ctk.CTkEntry(self.input_ramme)
                    self.p_input4.grid(row=8, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn", command=self.beregn_parallellkobling)
                beregn_knapp.grid(row=9, column=0, columnspan=2, pady=20)

            elif beregning == "VDR":
                # Skjul komponent-valg og vis form-valg på samme sted
                self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack_forget()       # Skjuler etiketten for form
                self.form_valg.pack_forget()        # Skjuler comboboxen for form
                self.form_label.pack(pady=5)  # Vis formetiketten for AC
                self.form_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC
                
                if self.form_valg.get() == "Polar":
                    # Input for Polar form
                    ctk.CTkLabel(self.input_ramme, text="Inngangsspenning magnitude (V):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.vin_input = ctk.CTkEntry(self.input_ramme)
                    self.vin_input.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Inngangsspenning fase (grader):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.p_input = ctk.CTkEntry(self.input_ramme)
                    self.p_input.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=5, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.r_input3 = ctk.CTkEntry(self.input_ramme)
                    self.r_input3.grid(row=7, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=8, column=0, padx=10, pady=5, sticky="e")
                    self.p_input3 = ctk.CTkEntry(self.input_ramme)
                    self.p_input3.grid(row=8, column=1, padx=10, pady=5)

                else:
                    # Input for Rektangulær form
                    ctk.CTkLabel(self.input_ramme, text="Inngangsspenning reell del (V):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.vin_input = ctk.CTkEntry(self.input_ramme)
                    self.vin_input.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Inngangsspenning imaginær del (V):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.p_input = ctk.CTkEntry(self.input_ramme)
                    self.p_input.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=5, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 reell del (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.r_input3 = ctk.CTkEntry(self.input_ramme)
                    self.r_input3.grid(row=7, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 imaginær del (Ω):").grid(row=8, column=0, padx=10, pady=5, sticky="e")
                    self.p_input3 = ctk.CTkEntry(self.input_ramme)
                    self.p_input3.grid(row=8, column=1, padx=10, pady=5)

                # Beregn-knapp plassert med grid()
                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn VDR", command=self.beregn_vdr)
                beregn_knapp.grid(row=9, column=0, columnspan=2, pady=20)


            elif beregning == "CDR":  # Beregning for CDR
                # Skjul komponent-valg og vis form-valg på samme sted
                self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack_forget()  # Skjuler etiketten for komponent
                self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack(pady=5)  # Vis formetiketten for AC
                self.form_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC

                if self.form_valg.get() == "Polar":
                    ctk.CTkLabel(self.input_ramme, text="Inngangsstrøm magnitude (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.vin_input = ctk.CTkEntry(self.input_ramme)
                    self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Inngangsstrøm fase (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.p_input = ctk.CTkEntry(self.input_ramme)
                    self.p_input.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=5, column=1, padx=10, pady=5)
                    
                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=7, column=1, padx=10, pady=5)
                
                else:  # For rektangulær form
                    ctk.CTkLabel(self.input_ramme, text="Inngangsstrøm reell del (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.vin_input = ctk.CTkEntry(self.input_ramme)
                    self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Inngangsstrøm imaginær del (A):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.p_input = ctk.CTkEntry(self.input_ramme)
                    self.p_input.grid(row=1, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                    self.r_input1 = ctk.CTkEntry(self.input_ramme)
                    self.r_input1.grid(row=2, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                    self.p_input1 = ctk.CTkEntry(self.input_ramme)
                    self.p_input1.grid(row=3, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=4, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=5, column=1, padx=10, pady=5)
                    
                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                    self.r_input2 = ctk.CTkEntry(self.input_ramme)
                    self.r_input2.grid(row=6, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                    self.p_input2 = ctk.CTkEntry(self.input_ramme)
                    self.p_input2.grid(row=7, column=1, padx=10, pady=5)

                beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn CDR", command=self.beregn_cdr)
                beregn_knapp.grid(row=8, column=0, columnspan=2, pady=20)

            elif beregning == "Kap og Ind":
                # Skjul komponent-valg og vis form-valg på samme sted
                self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.form_label.pack_forget()  # Skjuler etiketten for komponent
                self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
                self.komponent_label.pack(pady=5)  # Vis formetiketten for AC
                self.komponent_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC

                if self.komponent_valg.get() == "Kondensator":
                    ctk.CTkLabel(self.input_ramme, text="Kapasitanse (F):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.c_input = ctk.CTkEntry(self.input_ramme)
                    self.c_input.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Frekvens (f):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.f_input = ctk.CTkEntry(self.input_ramme)
                    self.f_input.grid(row=1, column=1, padx=10, pady=5)
                    
                    beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn Kondensator", command=self.beregn_kap_og_ind)
                    beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)

                elif self.komponent_valg.get() == "Spole":
                    ctk.CTkLabel(self.input_ramme, text="Induktans (H):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                    self.l_input = ctk.CTkEntry(self.input_ramme)
                    self.l_input.grid(row=0, column=1, padx=10, pady=5)

                    ctk.CTkLabel(self.input_ramme, text="Frekvens (f):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                    self.f_input = ctk.CTkEntry(self.input_ramme)
                    self.f_input.grid(row=1, column=1, padx=10, pady=5)
                    beregn_knapp = ctk.CTkButton(self.input_ramme, text="Beregn Spole", command=self.beregn_kap_og_ind)
                    beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)
            
    
    def beregn_ohms_lov(self):
        kalk_type = self.kalk_valg.get()  # Hent valgt kalkulatortype

        try:
            # Hvis kalkulatoren er satt til DC
            if kalk_type == "DC":
                U = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None # Hent spenning
                I = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None # Hent strøm
                R = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None # Hent motstand
                P = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else None # Hent effekt

                # Utfør beregninger basert på hvilke verdier som er oppgitt
                if U and I:  # Hvis spenning og strøm er gitt
                    R = U / I
                    P = U * I
                elif U and R:  # Hvis spenning og motstand er gitt
                    I = U / R
                    P = (U ** 2) / R
                elif I and R:  # Hvis strøm og motstand er gitt
                    U = I * R
                    P = (I ** 2) * R
                elif P and I:  # Hvis effekt og strøm er gitt
                    U = P / I
                    R = U / I
                elif P and U:  # Hvis effekt og spenning er gitt
                    I = P / U
                    R = U / I

                if not any([U, I, R, P]):  # Hvis ingen verdier er gitt
                    raise ValueError("Fyll inn minst to verdier for å beregne de andre.")

                # Formater resultatet og vis det i GUI
                self.resultat_label.configure(
                    text=f"U = {self.formater_resultat(U)} V\n"
                        f"I = {self.formater_resultat(I)} A\n"
                        f"R = {self.formater_resultat(R)} Ω\n"
                        f"P = {self.formater_resultat(P)} W"
                )

            # Hvis kalkulatoren er satt til AC
            elif kalk_type == "AC":
                U_mag = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None # Hent spenningens magnitude
                U_fase = math.radians(float(self.u_fase_input.get().replace(',', '.'))) if self.u_fase_input.get() else 0 # Konverter til radianer
                Z_mag = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None # Hent impedansens magnitude
                Z_fase = math.radians(float(self.z_fase_input.get().replace(',', '.'))) if self.z_fase_input.get() else 0 # Konverter til radianer
                I_mag = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None # Hent strømmens magnitude
                I_fase = math.radians(float(self.i_fase_input.get().replace(',', '.'))) if self.i_fase_input.get() else 0 # Konverter til radianer

                # Polar form
                if self.form_valg.get() == "Polar":
                    if U_mag and Z_mag:  # Hvis spenning (U) og impedans (Z) er gitt
                        U = cmath.rect(U_mag, U_fase)  # Konverter fra polar til rektangulær form
                        Z = cmath.rect(Z_mag, Z_fase)
                        I = U / Z  # Beregn strøm
                    elif U_mag and I_mag:  # Hvis spenning (U) og strøm (I) er gitt
                        U = cmath.rect(U_mag, U_fase)
                        I = cmath.rect(I_mag, I_fase)
                        Z = U / I  # Beregn impedans
                    elif Z_mag and I_mag:  # Hvis impedans (Z) og strøm (I) er gitt
                        Z = cmath.rect(Z_mag, Z_fase)
                        I = cmath.rect(I_mag, I_fase)
                        U = I * Z  # Beregn spenning

                # Rektangulær form
                else:
                    U_re = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None # Hent spenningens reelle del
                    U_im = self.konverter_prefiks(self.u_fase_input.get()) if self.u_fase_input.get() else None # Hent spenningens imaginære del
                    Z_re = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None # Hent impedansens reelle del
                    Z_im = self.konverter_prefiks(self.z_fase_input.get()) if self.z_fase_input.get() else None # Hent impedansens imaginære del
                    I_re = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None # Hent strømmens reelle del
                    I_im = self.konverter_prefiks(self.i_fase_input.get()) if self.i_fase_input.get() else None # Hent strømmens imaginære del

                    if U_re and Z_re:  # Hvis spenning (U) og impedans (Z) er gitt
                        U = complex(U_re, U_im) # Konverter til komplekst tall
                        Z = complex(Z_re, Z_im) 
                        I = U / Z  # Beregn strøm
                    elif U_re and I_re:  # Hvis spenning (U) og strøm (I) er gitt
                        U = complex(U_re, U_im) # Konverter til komplekst tall
                        I = complex(I_re, I_im)
                        Z = U / I  # Beregn impedans
                    elif Z_re and I_re:  # Hvis impedans (Z) og strøm (I) er gitt
                        Z = complex(Z_re, Z_im) # Konverter til komplekst tall
                        I = complex(I_re, I_im)
                        U = I * Z  # Beregn spenning

                # Hvis ingen av verdiene er gitt
                if not any([U, I, Z]):
                    raise ValueError("Fyll inn minst to verdier for å beregne de andre.")

                # Formater resultatene og vis dem i GUI
                self.resultat_label.configure(
                    text=f"U = {self.formater_resultat(abs(U))} ∠ {math.degrees(cmath.phase(U)):.2f}° V\n"
                        f"Z = {self.formater_resultat(abs(Z))} ∠ {math.degrees(cmath.phase(Z)):.2f}° Ω\n"
                        f"I = {self.formater_resultat(abs(I))} ∠ {math.degrees(cmath.phase(I)):.2f}° A"
                )
        
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_seriekobling(self):
        kalk_type = self.kalk_valg.get()
        try:
            if kalk_type == "DC": # Hvis kalkulatoren er satt til DC
                R1 = self.konverter_prefiks(self.r_input1.get()) # Hent motstand 1
                R2 = self.konverter_prefiks(self.r_input2.get()) # Hent motstand 2
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0 # Hent motstand 3
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0 # Hent motstand 4
                R_total = R1 + R2 + R3 + R4 # Beregn total motstand
                self.resultat_label.configure(text=f"Rtotal = {self.formater_resultat(R_total)} Ω") # Vis total motstand
            
            elif kalk_type == "AC":    
                Z_total = 0 + 0j # Start med 0 + 0j

                for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]: # Gå gjennom inputfeltene for impedans og fase
                    if impedans_input.get(): # Hvis inputfeltet for impedans ikke er tomt
                        if self.form_valg.get() == "Polar": # Hvis formvalget er satt til Polar
                            Z_mag = self.konverter_prefiks(impedans_input.get()) # Hent impedansens magnitude
                            Z_fase = math.radians(float(fase_input.get().replace(',', '.'))) # Hent impedansens fase og konverter til radianer
                            Z = cmath.rect(Z_mag, Z_fase) # Konverter fra polar til rektangulær form
                        else:
                            Z_re = self.konverter_prefiks(impedans_input.get()) # Hent impedansens reelle del
                            Z_im = self.konverter_prefiks(fase_input.get()) # Hent impedansens imaginære del
                            Z = complex(Z_re, Z_im) # Konverter til komplekst tall
                        Z_total += Z

                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω") # Vis total impedans
        
        except ValueError as e: # Hvis det oppstår en ValueError
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_parallellkobling(self): # Beregning for parallellkobling
        kalk_type = self.kalk_valg.get() 
        try:
            if kalk_type == "DC": # Hvis kalkulatoren er satt til DC
                R1 = self.konverter_prefiks(self.r_input1.get())    # Hent motstand 1
                R2 = self.konverter_prefiks(self.r_input2.get())    # Hent motstand 2
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None   # Hent motstand 3
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else None   # Hent motstand 4

                if R3 and R4:   # Hvis motstand 3 og 4 er gitt
                    R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3) + (1 / R4))   # Beregn total motstand
                elif R3:    # Hvis bare motstand 3 er gitt
                    R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3))  # Beregn total motstand
                else:  # Hvis bare motstand 1 og 2 er gitt
                    R_total = 1 / ((1 / R1) + (1 / R2))   # Beregn total motstand

                self.resultat_label.configure(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")     # Vis total motstand
            
            elif kalk_type == "AC":   # Hvis kalkulatoren er satt til AC
                Z_total_inv = 0 + 0j  # Start med 0 + 0j    

                for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:   # Gå gjennom inputfeltene for impedans og fase
                    if impedans_input.get():   # Hvis inputfeltet for impedans ikke er tomt
                        if self.form_valg.get() == "Polar":  # Hvis formvalget er satt til Polar
                            Z_mag = self.konverter_prefiks(impedans_input.get())    # Hent impedansens magnitude
                            Z_fase = math.radians(float(fase_input.get().replace(',', '.')))    # Hent impedansens fase og konverter til radianer
                            Z = cmath.rect(Z_mag, Z_fase)   # Konverter fra polar til rektangulær form
                        else:
                            Z_re = self.konverter_prefiks(impedans_input.get())   # Hent impedansens reelle del
                            Z_im = self.konverter_prefiks(fase_input.get())  # Hent impedansens imaginære del
                            Z = complex(Z_re, Z_im)   # Konverter til komplekst tall
                        Z_total_inv += 1 / Z        # Beregn den inverse av total impedans

                if Z_total_inv == 0:    
                    raise ValueError("Ingen gyldige impedanser oppgitt.")   # Gi en feilmelding hvis total impedans er null

                Z_total = 1 / Z_total_inv   # Beregn total impedans

                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")   # Vis total impedans
      
        
        except ValueError as e: # Hvis det oppstår en ValueError
            messagebox.showerror("Input Feil", str(e))  # Vis feilmelding i en messagebox
            
    def beregn_vdr(self):
        kalk_type = self.kalk_valg.get()
        try:
            if kalk_type == "DC":
                V_in = self.konverter_prefiks(self.vin_input.get())
                R1 = self.konverter_prefiks(self.r_input1.get())
                R2 = self.konverter_prefiks(self.r_input2.get())
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0

                R_total = R1 + R2 + R3 + R4
                V_R1 = V_in * R1 / R_total
                V_R2 = V_in * R2 / R_total
                V_R3 = V_in * R3 / R_total
                V_R4 = V_in * R4 / R_total

                self.resultat_label.configure(
                    text=f"UR1 = {self.formater_resultat(V_R1)} V\nUR2 = {self.formater_resultat(V_R2)} V\nUR3 = {self.formater_resultat(V_R3)} V\nUR4 = {self.formater_resultat(V_R4)} V")
            elif kalk_type == "AC":
                if self.form_valg.get() == "Polar":
                    Vin_mag = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else 0
                    Vin_fase = math.radians(float(self.p_input.get().replace(',', '.'))) if self.p_input.get() else 0
                    Vin = cmath.rect(Vin_mag, Vin_fase)

                    Z1_mag = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0
                    Z1_fase = math.radians(float(self.p_input1.get().replace(',', '.'))) if self.p_input1.get() else 0
                    Z1 = cmath.rect(Z1_mag, Z1_fase)

                    Z2_mag = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0
                    Z2_fase = math.radians(float(self.p_input2.get().replace(',', '.'))) if self.p_input2.get() else 0
                    Z2 = cmath.rect(Z2_mag, Z2_fase)

                    Z3_mag = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0
                    Z3_fase = math.radians(float(self.p_input3.get().replace(',', '.'))) if self.p_input3.get() else 0
                    Z3 = cmath.rect(Z3_mag, Z3_fase)
                else:  # Rektangulær form
                    Vin_re = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else 0
                    Vin_im = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else 0
                    Vin = complex(Vin_re, Vin_im)

                    Z1_re = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0
                    Z1_im = self.konverter_prefiks(self.p_input1.get()) if self.p_input1.get() else 0
                    Z1 = complex(Z1_re, Z1_im)

                    Z2_re = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0
                    Z2_im = self.konverter_prefiks(self.p_input2.get()) if self.p_input2.get() else 0
                    Z2 = complex(Z2_re, Z2_im)

                    Z3_re = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0
                    Z3_im = self.konverter_prefiks(self.p_input3.get()) if self.p_input3.get() else 0
                    Z3 = complex(Z3_re, Z3_im)

                Z_total = Z1 + Z2 + Z3
                if Z_total == 0:
                    raise ValueError("Impedansene kan ikke alle være null.")
                V1 = Vin * Z1 / Z_total
                V2 = Vin * Z2 / Z_total
                V3 = Vin * Z3 / Z_total
                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω\n"
                                                f"V1 = {self.formater_resultat(abs(V1))} ∠ {math.degrees(cmath.phase(V1)):.2f}° V\n"
                                                f"V2 = {self.formater_resultat(abs(V2))} ∠ {math.degrees(cmath.phase(V2)):.2f}° V\n"
                                                f"V3 = {self.formater_resultat(abs(V3))} ∠ {math.degrees(cmath.phase(V3)):.2f}° V")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_cdr(self):
        kalk_type = self.kalk_valg.get()
        try:
            if kalk_type == "DC":
                I_in = self.konverter_prefiks(self.iin_input.get())
                R1 = self.konverter_prefiks(self.r_input1.get())
                R2 = self.konverter_prefiks(self.r_input2.get())
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else None

                if R3 and R4:
                    I_R1 = I_in * ((R2 * R3 * R4) / (R1 * (R2 * R3 + R2 * R4 + R3 * R4) + R2 * R3 * R4))
                    I_R2 = I_in * ((R1 * R3 * R4) / (R1 * (R2 * R3 + R2 * R4 + R3 * R4) + R2 * R3 * R4))
                    I_R3 = I_in * ((R1 * R2 * R4) / (R1 * (R2 * R3 + R2 * R4 + R3 * R4) + R2 * R3 * R4))
                    I_R4 = I_in * ((R1 * R2 * R3) / (R1 * (R2 * R3 + R2 * R4 + R3 * R4) + R2 * R3 * R4))
                    self.resultat_label.configure(
                        text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A\nIR3 = {self.formater_resultat(I_R3)} A\nIR4 = {self.formater_resultat(I_R4)} A")
                elif R3:
                    I_R1 = I_in * ((R2 * R3) / (R1 * (R2 + R3) + R2 * R3))
                    I_R2 = I_in * ((R1 * R3) / (R1 * (R2 + R3) + R2 * R3))
                    I_R3 = I_in * ((R1 * R2) / (R1 * (R2 + R3) + R2 * R3))
                    self.resultat_label.configure(
                        text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A\nIR3 = {self.formater_resultat(I_R3)} A")
                else:
                    I_R1 = I_in * R2 / (R1 + R2)
                    I_R2 = I_in * R1 / (R1 + R2)
                    self.resultat_label.configure(
                        text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A")
            
            elif kalk_type == "AC":
                if self.form_valg.get() == "Polar":
                    # Kontroller at verdiene ikke er tomme og sett en standardverdi hvis de er
                    Iin_mag = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else 0.0
                    Iin_fase = math.radians(float(self.p_input.get().replace(',', '.'))) if self.p_input.get() else 0.0
                    Iin = cmath.rect(Iin_mag, Iin_fase)

                    Z1_mag = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0.0
                    Z1_fase = math.radians(float(self.p_input1.get().replace(',', '.'))) if self.p_input1.get() else 0.0
                    Z1 = cmath.rect(Z1_mag, Z1_fase)

                    Z2_mag = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0.0
                    Z2_fase = math.radians(float(self.p_input2.get().replace(',', '.'))) if self.p_input2.get() else 0.0
                    Z2 = cmath.rect(Z2_mag, Z2_fase)
                else:  # Rektangulær form
                    Iin_re = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else 0.0
                    Iin_im = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else 0.0
                    Iin = complex(Iin_re, Iin_im)

                    Z1_re = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0.0
                    Z1_im = self.konverter_prefiks(self.p_input1.get()) if self.p_input1.get() else 0.0
                    Z1 = complex(Z1_re, Z1_im)

                    Z2_re = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0.0
                    Z2_im = self.konverter_prefiks(self.p_input2.get()) if self.p_input2.get() else 0.0
                    Z2 = complex(Z2_re, Z2_im)

                Z_total_inv = 1 / Z1 + 1 / Z2
                if Z_total_inv == 0:
                    raise ValueError("Impedansene kan ikke alle være null.")
                Z_total = 1 / Z_total_inv

                I1 = Iin * (Z_total / Z1)
                I2 = Iin * (Z_total / Z2)

                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω\n"
                                                f"I1 = {self.formater_resultat(abs(I1))} ∠ {math.degrees(cmath.phase(I1)):.2f}° A\n"
                                                f"I2 = {self.formater_resultat(abs(I2))} ∠ {math.degrees(cmath.phase(I2)):.2f}° A")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_kap_og_ind(self):
        try:
            if self.komponent_valg.get() == "Kondensator":
                C = self.konverter_prefiks(self.c_input.get())
                f = self.konverter_prefiks(self.f_input.get())
                Z = 1 / (2 * math.pi * f * C)
                self.resultat_label.configure(text=f"Z = {self.formater_resultat(Z)} ∠-90° Ω")
            else:  # Spole
                L = self.konverter_prefiks(self.l_input.get())
                f = self.konverter_prefiks(self.f_input.get())
                Z = 2 * math.pi * f * L
                self.resultat_label.configure(text=f"Z = {self.formater_resultat(Z)} ∠90° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", f"Ugyldig input: {str(e)}")

    def kopier_resultat(self):
        """Kopierer resultatet til utklippstavlen."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.resultat_label.cget("text"))

if __name__ == "__main__":
    root = ctk.CTk()  # Bruk CustomTkinter CTk for hovedvinduet
    app = KalkulatorApp(root)
    root.mainloop()