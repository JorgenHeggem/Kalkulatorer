# Utviklet av: Jørgen Heggem
import os
import sys
import customtkinter as ctk
from tkinter import messagebox
import cmath
import math

# Konfigurer CustomTkinter
ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"


class KalkulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator")
        self.root.geometry("700x850")

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
        self.r_input4 = None
        self.u_fase_input = None
        self.i_fase_input = None    
        self.r_fase_input = None    
        self.z_fase_input = None
        self.r_input1 = None
        self.r_input2 = None
        self.r_input3 = None
        self.r_input4 = None    
        self.p_input1 = None
        self.p_input2 = None
        self.p_input3 = None
        self.p_input4 = None
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
        self.valg_ramme = ctk.CTkFrame(venstre_ramme)
        self.valg_ramme.pack(pady=5)
        self.valg_ramme.configure(fg_color="transparent")
        
        # Valg for strømtype
        ctk.CTkLabel(self.valg_ramme, text="Velg strømtype:", font=("Arial", 14, "bold")).pack(pady=1)  
        self.kalkvalg = ctk.CTkComboBox(self.valg_ramme, values=["DC", "AC"], command=self.oppdater_kalkulator)
        self.kalkvalg.pack(pady=5)
        self.kalkvalg.set("DC")

        # Valg av beregning
        ctk.CTkLabel(self.valg_ramme, text="Velg beregning:", font=("Arial", 14, "bold")).pack(pady=1)
        self.beregningsvalg = ctk.CTkComboBox(self.valg_ramme, values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR"], command=self.oppdater_beregning)
        self.beregningsvalg.pack(pady=5)
        self.beregningsvalg.set("Ohms lov")

        # Valg for form (kun for AC)
        self.form_label = ctk.CTkLabel(self.valg_ramme, text="Velg form:", font=("Arial", 14, "bold"))
        self.form_valg = ctk.CTkComboBox(self.valg_ramme, values=["Polar", "Rektangulær"], command=self.oppdater_beregning)
        self.form_label.pack_forget()  # Skjult som standard for DC
        self.form_valg.pack_forget()

        # Valg for komponent (kun for AC)
        self.komponent_label = ctk.CTkLabel(self.valg_ramme, text="Velg komponent:", font=("Arial", 14, "bold"))
        self.komponent_valg = ctk.CTkComboBox(self.valg_ramme, values=["Kondensator", "Spole"], command=self.oppdater_beregning)
        self.komponent_label.pack_forget()
        self.komponent_valg.pack_forget()

        # Ramme for input-felt
        self.input_frame = ctk.CTkFrame(venstre_ramme)
        self.input_frame.pack(pady=10)
        self.input_frame.configure(fg_color="transparent")

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
        kalk_type = self.kalkvalg.get()
        beregning = self.beregningsvalg.get()

        # Fjern eksisterende inputfelt
        for widget in self.input_frame.winfo_children():
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
        
    def setup_gui_fields(self, fields):
        """Setter opp GUI-felt basert på spesifiserte feltnavn og etiketter"""
        for row, (label_text, attr_name) in enumerate(fields, start=4):  # starter etter de første GUI-elementene
            # Opprett etikett og input-felt dynamisk
            label = ctk.CTkLabel(self.input_frame, text=label_text)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="e")
            
            # Opprett input-felt og lagre det som en attributt
            input_field = ctk.CTkEntry(self.input_frame)
            input_field.grid(row=row, column=1, padx=10, pady=5)
            
            # Bruk setattr for dynamisk å lagre input-feltet som attributt
            setattr(self, attr_name, input_field)

    def oppdater_beregning(self, event=None):
        """Setter opp GUI for valgte beregninger basert på type og beregningsvalg"""
        # Nullstiller input-feltene ved hver ny beregning
        for widget in self.input_frame.winfo_children():
            widget.grid_forget()  # Fjerner eksisterende widgets for oppsett

        kalk_type = self.kalkvalg.get()  # DC eller AC
        beregning = self.beregningsvalg.get()  # Ohms lov eller Seriekobling

        # Setter opp felter basert på type og beregning
        if kalk_type == "DC":
            if beregning == "Ohms lov":
                dc_fields = [
                    ("Spenning (V):", "u_input"),
                    ("Strøm (A):", "i_input"),
                    ("Motstand (Ω):", "r_input")
                ]
                self.setup_gui_fields(dc_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_ohms_lov)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
            elif beregning == "Seriekobling":
                dc_series_fields = [
                    ("Resistans 1 (Ω):", "r_input1"),
                    ("Resistans 2 (Ω):", "r_input2"),
                    ("Resistans 3 (Ω):", "r_input3"),
                    ("Resistans 4 (Ω):", "r_input4")
                ]
                self.setup_gui_fields(dc_series_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_seriekobling)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
            elif beregning == "Parallellkobling":
                dc_parallel_fields = [
                    ("Resistans 1 (Ω):", "r_input1"),
                    ("Resistans 2 (Ω):", "r_input2"),
                    ("Resistans 3 (Ω):", "r_input3"),
                    ("Resistans 4 (Ω):", "r_input4")
                ]
                self.setup_gui_fields(dc_parallel_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_parallellkobling)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
            elif beregning == "VDR":
                dc_vdr_fields = [
                    ("Inngangsspenning (V):", "vin_input"),
                    ("Resistans 1 (Ω):", "r_input1"),
                    ("Resistans 2 (Ω):", "r_input2"),
                    ("Resistans 3 (Ω):", "r_input3"),
                    ("Resistans 4 (Ω):", "r_input4")
                ]
                self.setup_gui_fields(dc_vdr_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_vdr)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
            elif beregning == "CDR":
                dc_cdr_fields = [
                    ("Inngangsstrøm (A):", "iin_input"),
                    ("Resistans 1 (Ω):", "r_input1"),
                    ("Resistans 2 (Ω):", "r_input2"),
                    ("Resistans 3 (Ω):", "r_input3"),
                    ("Resistans 4 (Ω):", "r_input4")
                ]
                self.setup_gui_fields(dc_cdr_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_cdr)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
        
        elif kalk_type == "AC":
            form = self.form_valg.get()  # Polar eller Rektangulær
            if beregning == "Ohms lov":
                self.skjul_komponent()
                if form == "Polar":
                    ac_fields = [
                        ("Spenning magnitude (U):", "u_input"),
                        ("Spenning fase (grader):", "u_fase_input"),
                        ("Strøm magnitude (I):", "i_input"),
                        ("Strøm fase (grader):", "i_fase_input"),
                        ("Motstand magnitude (Ω):", "r_input"),
                        ("Motstand fase (grader):", "r_fase_input")
                    ]
                else:  # Rektangulær form
                    ac_fields = [
                        ("Spenning reell del (U):", "u_input"),
                        ("Spenning imaginær del (j):", "u_fase_input"),
                        ("Strøm reell del (I):", "i_input"),
                        ("Strøm imaginær del (j):", "i_fase_input"),
                        ("Motstand reell del (Ω):", "r_input"),
                        ("Motstand imaginær del (j):", "z_fase_input")
                    ]
                self.setup_gui_fields(ac_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_ohms_lov)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)

            elif beregning == "Seriekobling":
                self.skjul_komponent()
                if form == "Polar":
                    ac_series_fields = [
                        ("Impedans 1 magnitude (Ω):", "r_input1"),
                        ("Impedans 1 fase (grader):", "p_input1"),
                        ("Impedans 2 magnitude (Ω):", "r_input2"),
                        ("Impedans 2 fase (grader):", "p_input2"),
                        ("Impedans 3 magnitude (Ω):", "r_input3"),
                        ("Impedans 3 fase (grader):", "p_input3"),
                        ("Impedans 4 magnitude (Ω):", "r_input4"),
                        ("Impedans 4 fase (grader):", "p_input4")
                    ]
                else:  # Rektangulær form
                    ac_series_fields = [
                        ("Impedans 1 reell del (Ω):", "r_input1"),
                        ("Impedans 1 imaginær del (Ω):", "p_input1"),
                        ("Impedans 2 reell del (Ω):", "r_input2"),
                        ("Impedans 2 imaginær del (Ω):", "p_input2"),
                        ("Impedans 3 reell del (Ω):", "r_input3"),
                        ("Impedans 3 imaginær del (Ω):", "p_input3"),
                        ("Impedans 4 reell del (Ω):", "r_input4"),
                        ("Impedans 4 imaginær del (Ω):", "p_input4")
                    ]
                self.setup_gui_fields(ac_series_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_seriekobling)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
                
            elif beregning == "Parallellkobling":
                self.skjul_komponent()
                if form == "Polar":
                    ac_parallel_fields = [
                        ("Impedans 1 magnitude (Ω):", "r_input1"),
                        ("Impedans 1 fase (grader):", "p_input1"),
                        ("Impedans 2 magnitude (Ω):", "r_input2"),
                        ("Impedans 2 fase (grader):", "p_input2"),
                        ("Impedans 3 magnitude (Ω):", "r_input3"),
                        ("Impedans 3 fase (grader):", "p_input3"),
                        ("Impedans 4 magnitude (Ω):", "r_input4"),
                        ("Impedans 4 fase (grader):", "p_input4")
                    ]
                else:  # Rektangulær form
                    ac_parallel_fields = [
                        ("Impedans 1 reell del (Ω):", "r_input1"),
                        ("Impedans 1 imaginær del (Ω):", "p_input1"),
                        ("Impedans 2 reell del (Ω):", "r_input2"),
                        ("Impedans 2 imaginær del (Ω):", "p_input2"),
                        ("Impedans 3 reell del (Ω):", "r_input3"),
                        ("Impedans 3 imaginær del (Ω):", "p_input3"),
                        ("Impedans 4 reell del (Ω):", "r_input4"),
                        ("Impedans 4 imaginær del (Ω):", "p_input4")
                    ]
                self.setup_gui_fields(ac_parallel_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_parallellkobling)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
                
            elif beregning == "VDR":
                self.skjul_komponent()
                if form == "Polar":
                    ac_vdr_fields = [
                        ("Inngangsspenning magnitude (V):", "vin_input"),
                        ("Inngangsspenning fase (grader):", "p_input"),
                        ("Impedans 1 magnitude (Ω):", "r_input1"),
                        ("Impedans 1 fase (grader):", "p_input1"),
                        ("Impedans 2 magnitude (Ω):", "r_input2"),
                        ("Impedans 2 fase (grader):", "p_input2"),
                        ("Impedans 3 magnitude (Ω):", "r_input3"),
                        ("Impedans 3 fase (grader):", "p_input3"),
                        ("Impedans 4 magnitude (Ω):", "r_input4"),
                        ("Impedans 4 fase (grader):", "p_input4")
                    ]
                else:  # Rektangulær form
                    ac_vdr_fields = [
                        ("Inngangsspenning reell del (V):", "vin_input"),
                        ("Inngangsspenning imaginær del (V):", "p_input"),
                        ("Impedans 1 reell del (Ω):", "r_input1"),
                        ("Impedans 1 imaginær del (Ω):", "p_input1"),
                        ("Impedans 2 reell del (Ω):", "r_input2"),
                        ("Impedans 2 imaginær del (Ω):", "p_input2"),
                        ("Impedans 3 reell del (Ω):", "r_input3"),
                        ("Impedans 3 imaginær del (Ω):", "p_input3"),
                        ("Impedans 4 reell del (Ω):", "r_input4"),
                        ("Impedans 4 imaginær del (Ω):", "p_input4")
                    ]
                self.setup_gui_fields(ac_vdr_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_vdr)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
            
            elif beregning == "CDR":
                self.skjul_komponent()
                if form == "Polar":
                    ac_cdr_fields = [
                        ("Inngangsstrøm magnitude (A):", "vin_input"),
                        ("Inngangsstrøm fase (grader):", "p_input"),
                        ("Impedans 1 magnitude (Ω):", "r_input1"),
                        ("Impedans 1 fase (grader):", "p_input1"),
                        ("Impedans 2 magnitude (Ω):", "r_input2"),
                        ("Impedans 2 fase (grader):", "p_input2"),
                        ("Impedans 3 magnitude (Ω):", "r_input3"),
                        ("Impedans 3 fase (grader):", "p_input3"),
                        ("Impedans 4 magnitude (Ω):", "r_input4"),
                        ("Impedans 4 fase (grader):", "p_input4")
                    ]
                else:  # Rektangulær form
                    ac_cdr_fields = [
                        ("Inngangsstrøm reell del (A):", "vin_input"),
                        ("Inngangsstrøm imaginær del (A):", "p_input"),
                        ("Impedans 1 reell del (Ω):", "r_input1"),
                        ("Impedans 1 imaginær del (Ω):", "p_input1"),
                        ("Impedans 2 reell del (Ω):", "r_input2"),
                        ("Impedans 2 imaginær del (Ω):", "p_input2"),
                        ("Impedans 3 reell del (Ω):", "r_input3"),
                        ("Impedans 3 imaginær del (Ω):", "p_input3"),
                        ("Impedans 4 reell del (Ω):", "r_input4"),
                        ("Impedans 4 imaginær del (Ω):", "p_input4")
                    ]
                self.setup_gui_fields(ac_cdr_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_cdr)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
                
            elif beregning == "Kap og Ind":
                self.skjul_form()
                if self.komponent_valg.get() == "Kondensator":
                    ac_komponent_fields = [
                        ("Kapasitans (F):", "c_input"),
                        ("Frekvens (Hz):", "f_input")
                    ]
                else:  # Spole
                    ac_komponent_fields = [
                        ("Induktans (L):", "l_input"),
                        ("Frekvens (Hz):", "f_input")
                    ]
                self.setup_gui_fields(ac_komponent_fields)
                beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_kap_og_ind)
                beregn_knapp.grid(sticky="n", row=50, column=1, pady=10)
        
    def skjul_komponent(self):
        # Skjuler kompnentvalg
        self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
        self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
        self.form_label.pack_forget()  # Skjuler etiketten for komponent
        self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
        self.form_label.pack(pady=5)  # Vis formetiketten for AC
        self.form_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC
                
    def skjul_form(self):
        # Skjuler formvalg
        self.komponent_label.pack_forget()  # Skjuler etiketten for komponent
        self.komponent_valg.pack_forget()   # Skjuler comboboxen for komponent
        self.form_label.pack_forget()  # Skjuler etiketten for komponent
        self.form_valg.pack_forget()   # Skjuler comboboxen for komponent
        self.komponent_label.pack(pady=5)  # Vis formetiketten for AC
        self.komponent_valg.pack(pady=5)  # Vis komboboksen for formvalg for AC
                    
    def beregn_ohms_lov(self):
        kalk_type = self.kalkvalg.get()  # Hent valgt kalkulatortype

        try:
            # Hvis kalkulatoren er satt til DC
            if kalk_type == "DC":
                U = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
                I = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
                R = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
                

                # Utfør beregninger basert på hvilke verdier som er oppgitt
                if U and I:  # Hvis spenning og strøm er gitt
                    R = U / I
                    P = U * I
                elif U and R:  # Hvis spenning og motstand er gitt
                    I = U / R
                    P = U * U / R
                elif I and R:  # Hvis strøm og motstand er gitt
                    U = I * R
                    P = I * I * R

                if not any([U, I, R]):  # Hvis ingen verdier er gitt
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
                U_mag = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
                U_fase = math.radians(float(self.u_fase_input.get().replace(',', '.'))) if self.u_fase_input.get() else None
                Z_mag = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
                Z_fase = math.radians(float(self.z_fase_input.get().replace(',', '.'))) if self.z_fase_input.get() else None
                I_mag = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
                I_fase = math.radians(float(self.i_fase_input.get().replace(',', '.'))) if self.i_fase_input.get() else None

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
                    U_re = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
                    U_im = self.konverter_prefiks(self.u_fase_input.get()) if self.u_fase_input.get() else None
                    Z_re = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
                    Z_im = self.konverter_prefiks(self.z_fase_input.get()) if self.z_fase_input.get() else None
                    I_re = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
                    I_im = self.konverter_prefiks(self.i_fase_input.get()) if self.i_fase_input.get() else None

                    if U_re and Z_re:  # Hvis spenning (U) og impedans (Z) er gitt
                        U = complex(U_re, U_im)
                        Z = complex(Z_re, Z_im)
                        I = U / Z  # Beregn strøm
                    elif U_re and I_re:  # Hvis spenning (U) og strøm (I) er gitt
                        U = complex(U_re, U_im)
                        I = complex(I_re, I_im)
                        Z = U / I  # Beregn impedans
                    elif Z_re and I_re:  # Hvis impedans (Z) og strøm (I) er gitt
                        Z = complex(Z_re, Z_im)
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
        kalk_type = self.kalkvalg.get()
        try:
            if kalk_type == "DC":
                R1 = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0.0
                R2 = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0.0
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0.0
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0.0
                R_total = R1 + R2 + R3 + R4
                self.resultat_label.configure(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")
            
            elif kalk_type == "AC":    
                Z_total = 0 + 0j  # Start med 0 + 0j

                for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                    if impedans_input.get():
                        if self.form_valg.get() == "Polar":
                            Z_mag = self.konverter_prefiks(impedans_input.get())
                            Z_fase = math.radians(float(fase_input.get().replace(',', '.')))
                            Z = cmath.rect(Z_mag, Z_fase)
                        else:
                            Z_re = self.konverter_prefiks(impedans_input.get())
                            Z_im = self.konverter_prefiks(fase_input.get())
                            Z = complex(Z_re, Z_im)
                        Z_total += Z

                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
        
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_parallellkobling(self):
        kalk_type = self.kalkvalg.get()
        try:
            if kalk_type == "DC":
                R1 = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else None
                R2 = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else None
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else None

                if R3 and R4:
                    R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3) + (1 / R4))
                elif R3:
                    R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3))
                else:
                    R_total = 1 / ((1 / R1) + (1 / R2))

                self.resultat_label.configure(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")   
            
            elif kalk_type == "AC":
                Z_total_inv = 0 + 0j  # Start med 0 + 0j

                for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                    if impedans_input.get():
                        if self.form_valg.get() == "Polar":
                            Z_mag = self.konverter_prefiks(impedans_input.get())
                            Z_fase = math.radians(float(fase_input.get().replace(',', '.')))
                            Z = cmath.rect(Z_mag, Z_fase)
                        else:
                            Z_re = self.konverter_prefiks(impedans_input.get())
                            Z_im = self.konverter_prefiks(fase_input.get())
                            Z = complex(Z_re, Z_im)
                        Z_total_inv += 1 / Z

                if Z_total_inv == 0:
                    raise ValueError("Ingen gyldige impedanser oppgitt.")

                Z_total = 1 / Z_total_inv

                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
      
        
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_vdr(self):
        kalk_type = self.kalkvalg.get()
        try:
            if kalk_type == "DC":
                V_in = self.konverter_prefiks(self.vin_input.get())
                R1 = self.konverter_prefiks(self.r_input1.get())
                R2 = self.konverter_prefiks(self.r_input2.get())
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0.0
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0.0

                R_total = R1 + R2 + R3 + R4
                V_R1 = V_in * R1 / R_total
                V_R2 = V_in * R2 / R_total
                V_R3 = V_in * R3 / R_total
                V_R4 = V_in * R4 / R_total

                self.resultat_label.configure(
                    text=f"UR1 = {self.formater_resultat(V_R1)} V\nUR2 = {self.formater_resultat(V_R2)} V\nUR3 = {self.formater_resultat(V_R3)} V\nUR4 = {self.formater_resultat(V_R4)} V")
            elif kalk_type == "AC":
                if self.form_valg.get() == "Polar":
                    Vin_mag = self.konverter_prefiks(self.vin_input.get())
                    Vin_fase = math.radians(float(self.p_input.get().replace(',', '.')))
                    Vin = cmath.rect(Vin_mag, Vin_fase)

                    Z1_mag = self.konverter_prefiks(self.r_input1.get())
                    Z1_fase = math.radians(float(self.p_input1.get().replace(',', '.')))
                    Z1 = cmath.rect(Z1_mag, Z1_fase)

                    Z2_mag = self.konverter_prefiks(self.r_input2.get())
                    Z2_fase = math.radians(float(self.p_input2.get().replace(',', '.')))
                    Z2 = cmath.rect(Z2_mag, Z2_fase)

                    Z3_mag = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0.0
                    Z3_fase = math.radians(float(self.p_input3.get().replace(',', '.'))) if self.p_input3.get() else 0.0
                    Z3 = cmath.rect(Z3_mag, Z3_fase)
                    
                    Z4_mag = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0.0
                    Z4_fase = math.radians(float(self.p_input4.get().replace(',', '.'))) if self.p_input4.get() else 0.0
                    Z4 = cmath.rect(Z4_mag, Z4_fase)
                else:  # Rektangulær form
                    Vin_re = self.konverter_prefiks(self.vin_input.get())
                    Vin_im = self.konverter_prefiks(self.p_input.get())
                    Vin = complex(Vin_re, Vin_im)

                    Z1_re = self.konverter_prefiks(self.r_input1.get())
                    Z1_im = self.konverter_prefiks(self.p_input1.get())
                    Z1 = complex(Z1_re, Z1_im)

                    Z2_re = self.konverter_prefiks(self.r_input2.get())
                    Z2_im = self.konverter_prefiks(self.p_input2.get())
                    Z2 = complex(Z2_re, Z2_im)

                    Z3_re = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0.0
                    Z3_im = self.konverter_prefiks(self.p_input3.get()) if self.p_input3.get() else 0.0
                    Z3 = complex(Z3_re, Z3_im)
                    
                    Z4_re = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0.0
                    Z4_im = self.konverter_prefiks(self.p_input4.get()) if self.p_input4.get() else 0.0
                    Z4 = complex(Z4_re, Z4_im)

                Z_total = Z1 + Z2 + Z3
                if Z_total == 0:
                    raise ValueError("Impedansene kan ikke alle være null.")
                V1 = Vin * Z1 / Z_total
                V2 = Vin * Z2 / Z_total
                V3 = Vin * Z3 / Z_total
                V4 = Vin * Z4 / Z_total
                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω\n"
                                                f"V1 = {self.formater_resultat(abs(V1))} ∠ {math.degrees(cmath.phase(V1)):.2f}° V\n"
                                                f"V2 = {self.formater_resultat(abs(V2))} ∠ {math.degrees(cmath.phase(V2)):.2f}° V\n"
                                                f"V3 = {self.formater_resultat(abs(V3))} ∠ {math.degrees(cmath.phase(V3)):.2f}° V\n"
                                                f"V4 = {self.formater_resultat(abs(V4))} ∠ {math.degrees(cmath.phase(V4)):.2f}° V")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_cdr(self):
        kalk_type = self.kalkvalg.get()
        try:
            if kalk_type == "DC":
                I_in = self.konverter_prefiks(self.iin_input.get()) if self.iin_input.get() else None
                R1 = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else None
                R2 = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else None
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
                    Iin_mag = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else None
                    Iin_fase = math.radians(float(self.p_input.get().replace(',', '.'))) if self.p_input.get() else None
                    Iin = cmath.rect(Iin_mag, Iin_fase)

                    Z1_mag = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else None
                    Z1_fase = math.radians(float(self.p_input1.get().replace(',', '.'))) if self.p_input1.get() else None
                    Z1 = cmath.rect(Z1_mag, Z1_fase)

                    Z2_mag = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else None
                    Z2_fase = math.radians(float(self.p_input2.get().replace(',', '.'))) if self.p_input2.get() else None
                    Z2 = cmath.rect(Z2_mag, Z2_fase)
                    
                    Z3_mag = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None
                    Z3_fase = math.radians(float(self.p_input3.get().replace(',', '.'))) if self.p_input3.get() else None
                    Z3 = cmath.rect(Z3_mag, Z3_fase)
                    
                    Z4_mag = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else None
                    Z4_fase = math.radians(float(self.p_input4.get().replace(',', '.'))) if self.p_input4.get() else None
                    Z4 = cmath.rect(Z4_mag, Z4_fase)
                else:  # Rektangulær form
                    Iin_re = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else None
                    Iin_im = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else None
                    Iin = complex(Iin_re, Iin_im)

                    Z1_re = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else None
                    Z1_im = self.konverter_prefiks(self.p_input1.get()) if self.p_input1.get() else None
                    Z1 = complex(Z1_re, Z1_im)

                    Z2_re = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else None
                    Z2_im = self.konverter_prefiks(self.p_input2.get()) if self.p_input2.get() else None
                    Z2 = complex(Z2_re, Z2_im)
                    
                    Z3_re = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None
                    Z3_im = self.konverter_prefiks(self.p_input3.get()) if self.p_input3.get() else None
                    Z3 = complex(Z3_re, Z3_im)
                    
                    Z4_re = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else None
                    Z4_im = self.konverter_prefiks(self.p_input4.get()) if self.p_input4.get() else None
                    Z4 = complex(Z4_re, Z4_im)

                Z_total_inv = 1 / Z1 + 1 / Z2 + 1 / Z3 + 1 / Z4
                if Z_total_inv == 0:
                    raise ValueError("Impedansene kan ikke alle være null.")
                Z_total = 1 / Z_total_inv

                I1 = Iin * (Z_total / Z1)
                I2 = Iin * (Z_total / Z2)
                I3 = Iin * (Z_total / Z3)
                I4 = Iin * (Z_total / Z4)

                self.resultat_label.configure(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω\n"
                                                   f"I1 = {self.formater_resultat(abs(I1))} ∠ {math.degrees(cmath.phase(I1)):.2f}° A\n"
                                                   f"I2 = {self.formater_resultat(abs(I2))} ∠ {math.degrees(cmath.phase(I2)):.2f}° A\n"
                                                   f"I3 = {self.formater_resultat(abs(I3))} ∠ {math.degrees(cmath.phase(I3)):.2f}° A\n"
                                                   f"I4 = {self.formater_resultat(abs(I4))} ∠ {math.degrees(cmath.phase(I4)):.2f}° A")
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