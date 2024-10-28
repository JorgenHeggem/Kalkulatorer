
# Jørgen Heggem sin DC Kalkulator
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes  # Legg til denne importen øverst i filen

class KalkulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DC Kalkulator")
        self.root.geometry("500x500")

        # Finner riktig ikonfil
        if hasattr(sys, '_MEIPASS'):
            # Bruker ikonet fra den midlertidige mappen der .exe kjøres
            ikon_sti = os.path.join(sys._MEIPASS, "Kalk ikon DC.ico")
        else:
            # Bruker ikonet direkte når det kjøres som et skript
            ikon_sti = os.path.join(os.path.dirname(__file__), "Kalk ikon DC.ico")

        self.root.iconbitmap(ikon_sti)

        # Fortsett med resten av GUI-initialisering...


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

        # Opprett GUI-elementer
        
        self.lag_gui()
    
    def lag_gui(self):
        # Hovedramme som inneholder både innholdet og notatene
        hovedramme = tk.Frame(self.root)
        hovedramme.pack(fill="both", expand=True)

        # Venstre ramme for resten av grensesnittet
        venstre_ramme = tk.Frame(hovedramme)
        venstre_ramme.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Høyre ramme for notatene
        hoyre_ramme = tk.Frame(hovedramme)
        hoyre_ramme.pack(side="right", fill="y", padx=10, pady=10)

        # Valg for beregningstype
        tk.Label(venstre_ramme, text="Velg beregning:", font=("Arial", 12, "bold")).pack(pady=10)
        self.beregningsvalg = ttk.Combobox(venstre_ramme, state="readonly", values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR"], font=("Arial", 10))
        self.beregningsvalg.current(0)
        self.beregningsvalg.pack(pady=10)
        self.beregningsvalg.bind("<<ComboboxSelected>>", self.oppdater_beregning)

        # Frame for input-felt
        self.input_frame = tk.Frame(venstre_ramme)
        self.input_frame.pack(pady=20)

        # Resultat-etikett
        self.resultat_label = tk.Label(venstre_ramme, text="Resultat:", font=("Arial", 12))
        self.resultat_label.pack(pady=10)

        # Kopier-knapp
        self.kopier_knapp = tk.Button(venstre_ramme, text="Kopier resultat", command=self.kopier_resultat)
        self.kopier_knapp.pack(pady=10)

        # Etikett for notater i høyre ramme
        tk.Label(hoyre_ramme, text="Notater:", font=("Arial", 12)).pack(pady=5)

        # Tekstboks for notater
        self.notater_boks = tk.Text(hoyre_ramme, height=20, width=30, font=("Arial", 10))
        self.notater_boks.pack(pady=10)
        
        # Legg til tekst ved oppstart
        Prefiks_tekst = "Støttede prefikser: G, M, k, m, µ, n\n\n"
        self.notater_boks.insert(tk.END, Prefiks_tekst)

        # Start med standard beregning
        self.oppdater_beregning()


    def konverter_prefiks(self, verdi):
        """Støtte for prefikser som k, M, G etc."""
        verdi = verdi.strip().lower()
        try:
            if 'm' in verdi: # Milli
                return float(verdi.replace('m', '')) * 1e-3            
            elif 'k' in verdi:  # Kilo
                return float(verdi.replace('k', '')) * 1e3
            elif 'm' in verdi and 'µ' not in verdi:
                return float(verdi.replace('M', '')) * 1e6
            elif 'µ' in verdi:  # Mikro
                return float(verdi.replace('µ', '')) * 1e-6
            elif 'G' in verdi:  # Giga
                return float(verdi.replace('G', '')) * 1e9
            elif 'n' in verdi:  # Nano
                return float(verdi.replace('n', '')) * 1e-9
            elif 'T' in verdi:  # Tera
                return float(verdi.replace('T', '')) * 1e12
            else:
                return float(verdi) # Ingen prefiks
        except ValueError:  # Hvis konvertering feiler  (f.eks. bokstaver i input)  
            raise ValueError("Ugyldig verdi for prefiks!")  # Gi beskjed til bruker

    def formater_resultat(self, verdi):
        # Definerer SI-prefikser og deres verdier
        prefikser = [
            (1e9, 'G'),  # Giga
            (1e6, 'M'),  # Mega
            (1e3, 'k'),  # Kilo
            (1, ''),     # Ingen prefiks
            (1e-3, 'm'), # Milli
            (1e-6, 'µ'), # Mikro
            (1e-9, 'n')  # Nano
        ]

        # Finn riktig prefiks
        for faktor, prefiks in prefikser:
            if abs(verdi) >= faktor:
                return f"{verdi / faktor:.2f} {prefiks}"
        
        # Hvis ingen prefiks passer, returner verdien som den er
        return f"{verdi:.2f}"

    def beregn_ohms_lov(self):
        """Ohms lov med mulighet for å skrive inn spenning, strøm, motstand og effekt."""
        try:
            U = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None  
            I = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
            R = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
            P = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else None

            if U and I: # Hvis spenning og strøm er gitt
                R = U / I
                P = U * I
            elif U and R:   # Hvis spenning og motstand er gitt
                I = U / R
                P = (U ** 2) / R    
            elif I and R:   # Hvis strøm og motstand er gitt
                U = I * R
                P = (I ** 2) * R
            elif P and I:   # Hvis effekt og strøm er gitt
                U = P / I
                R = U / I
            elif P and U:   # Hvis effekt og spenning er gitt
                I = P / U
                R = U / I

            if not any([U, I, R, P]):   # Hvis ingen verdier er gitt
                raise ValueError("Fyll inn minst to verdier for å beregne de andre.")   # Gi beskjed til bruker

            self.resultat_label.config(text=f"U = {self.formater_resultat(U)} V\nI = {self.formater_resultat(I)} A\nR = {self.formater_resultat(R)} Ω\nP = {self.formater_resultat(P)} W")
        except ValueError as e: # Hvis det oppstår en feil
            messagebox.showerror("Input Feil", str(e))  # Vis feilmelding til bruker    

    def beregn_seriekobling(self):  
        """Beregner seriekobling av motstander."""
        try:
            R1 = self.konverter_prefiks(self.r_input1.get())    # Konverterer input til tall
            R2 = self.konverter_prefiks(self.r_input2.get())    # Konverterer input til tall
            R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0      # Konverterer input til tall, eller 0 hvis input er tom

            R_total = R1 + R2 + R3      # Beregner total motstand
            self.resultat_label.config(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")    # Viser resultatet til bruker    
        except ValueError as e:    # Hvis det oppstår en feil
            messagebox.showerror("Input Feil", str(e))  # Vis feilmelding til bruker

    def beregn_parallellkobling(self):                              
        """Beregner parallellkobling av motstander."""
        try:    # Prøv å beregne parallellkobling
            R1 = self.konverter_prefiks(self.r_input1.get())    # Konverterer input til tall
            R2 = self.konverter_prefiks(self.r_input2.get())    # Konverterer input til tall
            R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None   # Konverterer input til tall, eller None hvis input er tom

            if R3:  # Hvis det er tre motstander
                R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3))  # Beregner total motstand
            else:   # Hvis det er to motstander
                R_total = 1 / ((1 / R1) + (1 / R2)) # Beregner total motstand

            self.resultat_label.config(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")    # Viser resultatet til bruker
        except ValueError as e:   # Hvis det oppstår en feil
            messagebox.showerror("Input Feil", str(e))  # Vis feilmelding til bruker

    def beregn_vdr(self):       
        """Spenningsdeling med tre motstander (VDR)."""
        try:    # Prøv å beregne spenningsdeling
            V_in = self.konverter_prefiks(self.vin_input.get())   # Konverterer input til tall
            R1 = self.konverter_prefiks(self.r_input1.get())    # Konverterer input til tall
            R2 = self.konverter_prefiks(self.r_input2.get())    # Konverterer input til tall
            R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0  # Konverterer input til tall, eller 0 hvis input er tom

            R_total = R1 + R2 + R3  # Beregner total motstand
            V_R1 = V_in * R1 / R_total  # Beregner spenning over R1
            V_R2 = V_in * R2 / R_total  # Beregner spenning over R2
            V_R3 = V_in * R3 / R_total  # Beregner spenning over R3

            self.resultat_label.config(text=f"UR1 = {self.formater_resultat(V_R1)} V\nUR2 = {self.formater_resultat(V_R2)} V\nUR3 = {self.formater_resultat(V_R3)} V")
        except ValueError as e:  # Hvis det oppstår en feil
            messagebox.showerror("Input Feil", str(e))  # Vis feilmelding til bruker

    def beregn_cdr(self):   
        """Strømdeling med tre motstander (CDR)."""
        try:    # Prøv å beregne strømdeling
            I_in = self.konverter_prefiks(self.iin_input.get())  # Konverterer input til tall
            R1 = self.konverter_prefiks(self.r_input1.get())    # Konverterer input til tall
            R2 = self.konverter_prefiks(self.r_input2.get())    # Konverterer input til tall
            R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None   # Konverterer input til tall, eller None hvis input er tom

            if R3:  # Hvis det er tre motstander
                I_R1 = I_in * ((R2 * R3) / (R1 * (R2 + R3) + R2 * R3))
                I_R2 = I_in * ((R1 * R3) / (R1 * (R2 + R3) + R2 * R3))
                I_R3 = I_in * ((R1 * R2) / (R1 * (R2 + R3) + R2 * R3))
                self.resultat_label.config(text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A\nIR3 = {self.formater_resultat(I_R3)} A")
            else:   # Hvis det er to motstander
                I_R1 = I_in * R2 / (R1 + R2)
                I_R2 = I_in * R1 / (R1 + R2)
                self.resultat_label.config(text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A")
        except ValueError as e: # Hvis det oppstår en feil
            messagebox.showerror("Input Feil", str(e))  # Vis feilmelding til bruker

    def kopier_resultat(self):  
        """Kopierer resultatet til utklippstavlen."""
        self.root.clipboard_clear() # Tømmer utklippstavlen
        self.root.clipboard_append(self.resultat_label.cget("text"))    # Kopierer resultatet til utklippstavlen
        messagebox.showinfo("Kopiert", "Resultatet er kopiert til utklippstavlen!")   # Viser melding til bruker

    def oppdater_beregning(self, event=None):   
        # Oppdater input-felt basert på valgt beregning
        for widget in self.input_frame.winfo_children():    # Fjerner alle input-felt
            widget.destroy()    # Fjerner input-felt

        beregning = self.beregningsvalg.get()   # Henter valgt beregning

        if beregning == "Ohms lov": # Hvis Ohms lov er valgt
            tk.Label(self.input_frame, text="Spenning (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e") # Opprett etikett for spenning
            self.u_input = tk.Entry(self.input_frame)   # Opprett input-felt for spenning
            self.u_input.grid(row=0, column=1, padx=10, pady=5) # Plasserer input-felt i rammen

            tk.Label(self.input_frame, text="Strøm (A):").grid(row=1, column=0, padx=10, pady=5, sticky="e")    # Opprett etikett for strøm
            self.i_input = tk.Entry(self.input_frame)   # Opprett input-felt for strøm
            self.i_input.grid(row=1, column=1, padx=10, pady=5)     # Plasserer input-felt i rammen 

            tk.Label(self.input_frame, text="Motstand (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e") # Opprett etikett for motstand
            self.r_input = tk.Entry(self.input_frame)   # Opprett input-felt for motstand
            self.r_input.grid(row=2, column=1, padx=10, pady=5) # Plasserer input-felt i rammen

            tk.Label(self.input_frame, text="Effekt (W):").grid(row=3, column=0, padx=10, pady=5, sticky="e")   # Opprett etikett for effekt
            self.p_input = tk.Entry(self.input_frame)   # Opprett input-felt for effekt
            self.p_input.grid(row=3, column=1, padx=10, pady=5) # Plasserer input-felt i rammen

            beregn_knapp = tk.Button(self.input_frame, text="Beregn", command=self.beregn_ohms_lov)   # Opprett beregningsknapp
            beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)   # Plasserer beregningsknapp i rammen

        elif beregning == "Seriekobling":
            tk.Label(self.input_frame, text="Motstand 1 (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = tk.Entry(self.input_frame)
            self.r_input1.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 2 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = tk.Entry(self.input_frame)
            self.r_input2.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 3 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = tk.Entry(self.input_frame)
            self.r_input3.grid(row=2, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_frame, text="Beregn", command=self.beregn_seriekobling)
            beregn_knapp.grid(row=3, column=0, columnspan=2, pady=20)

        elif beregning == "Parallellkobling":
            tk.Label(self.input_frame, text="Motstand 1 (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = tk.Entry(self.input_frame)
            self.r_input1.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 2 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = tk.Entry(self.input_frame)
            self.r_input2.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 3 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = tk.Entry(self.input_frame)
            self.r_input3.grid(row=2, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_frame, text="Beregn", command=self.beregn_parallellkobling)
            beregn_knapp.grid(row=3, column=0, columnspan=2, pady=20)

        elif beregning == "VDR":
            tk.Label(self.input_frame, text="Inngangsspenning (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.vin_input = tk.Entry(self.input_frame)
            self.vin_input.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 1 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = tk.Entry(self.input_frame)
            self.r_input1.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 2 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = tk.Entry(self.input_frame)
            self.r_input2.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 3 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = tk.Entry(self.input_frame)
            self.r_input3.grid(row=3, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_frame, text="Beregn", command=self.beregn_vdr)
            beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

        elif beregning == "CDR":
            tk.Label(self.input_frame, text="Inngangsstrøm (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.iin_input = tk.Entry(self.input_frame)
            self.iin_input.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 1 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = tk.Entry(self.input_frame)
            self.r_input1.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 2 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = tk.Entry(self.input_frame)
            self.r_input2.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(self.input_frame, text="Motstand 3 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = tk.Entry(self.input_frame)
            self.r_input3.grid(row=3, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_frame, text="Beregn", command=self.beregn_cdr)
            beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)
root = tk.Tk()  # Opprett hovedvinduet
app = KalkulatorApp(root)   # Opprett applikasjonen
root.mainloop() # Start applikasjonen