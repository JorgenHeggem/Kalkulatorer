import os
import sys
import customtkinter as ctk
from tkinter import messagebox

# Konfigurer CustomTkinter
ctk.set_appearance_mode("Dark")  # "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue", "green", "dark-blue"


class KalkulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DC Kalkulator")
        self.root.geometry("650x600")

        # Finner riktig ikonfil
        if hasattr(sys, '_MEIPASS'):
            ikon_sti = os.path.join(sys._MEIPASS, "Kalk ikon DC.ico")
        else:
            ikon_sti = os.path.join(os.path.dirname(__file__), "Kalk ikon DC.ico")

        # Bruk ikonet til applikasjonen
        self.root.iconbitmap(ikon_sti)

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
        hovedramme = ctk.CTkFrame(self.root)
        hovedramme.pack(fill="both", expand=True, padx=0, pady=0)
        hovedramme.configure(fg_color="transparent")

        # Venstre ramme for resten av grensesnittet
        venstre_ramme = ctk.CTkFrame(hovedramme)
        venstre_ramme.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        venstre_ramme.configure(fg_color="transparent")

        # Høyre ramme for notatene
        hoyre_ramme = ctk.CTkFrame(hovedramme)
        hoyre_ramme.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        hoyre_ramme.configure(fg_color="transparent")
        
        # Valg for beregningstype
        ctk.CTkLabel(venstre_ramme, text="Velg beregning:", font=("Arial", 14, "bold")).pack(pady=1)
        self.beregningsvalg = ctk.CTkComboBox(venstre_ramme, values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR"], command=self.oppdater_beregning)
        self.beregningsvalg.pack(pady=5)
        self.beregningsvalg.set("Ohms lov")

        # Frame for input-felt
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
        self.notater_boks.pack(fill="both", expand=True, padx=10, pady=10)  # Fyller tilgjengelig plass

        # Legg til tekst ved oppstart
        prefiks_tekst = "Støttede prefikser: T, G, M, k, m, µ, n\n\n"
        self.notater_boks.insert("0.0", prefiks_tekst)

        # Start med standard beregning
        self.oppdater_beregning("Ohms lov")
        
    def erstatt_komma_med_punktum(self, verdi):
        """Erstatt komma med punktum i input."""
        return verdi.replace(',', '.')

    def konverter_prefiks(self, verdi):
        """Støtte for prefikser som k, M, G etc., og desimaltall med komma."""
        verdi = self.erstatt_komma_med_punktum(verdi.strip())  # Erstatt komma med punktum
        try:
            if 'm' in verdi and 'M' not in verdi:  # Milli
                return float(verdi.replace('m', '')) * 1e-3
            elif 'k' in verdi:  # Kilo
                return float(verdi.replace('k', '')) * 1e3
            elif 'M' in verdi and 'm' not in verdi:
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
                return float(verdi)  # Ingen prefiks
        except ValueError:
            raise ValueError("Ugyldig verdi for prefiks!")


    def formater_resultat(self, verdi):
        """Formatere verdien med SI-prefikser og bruk komma som desimaltegn."""
        prefikser = [
            (1e12, 'T'),  # Giga
            (1e9, 'G'),  # Giga
            (1e6, 'M'),  # Mega
            (1e3, 'k'),  # Kilo
            (1, ''),     # Ingen prefiks
            (1e-3, 'm'), # Milli
            (1e-6, 'µ'), # Mikro
            (1e-9, 'n')  # Nano
        ]
        for faktor, prefiks in prefikser:
            if abs(verdi) >= faktor:
                # Formatere med punktum og så erstatte med komma for visning
                return f"{(verdi / faktor):.2f} {prefiks}".replace('.', ',')
        return f"{verdi:.2f}".replace('.', ',')


    def beregn_ohms_lov_dc(self):
        """Ohms lov med mulighet for å skrive inn spenning, strøm, motstand og effekt."""
        try:
            U = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
            I = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
            R = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
            P = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else None

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

            self.resultat_label.configure(
                text=f"U= {self.formater_resultat(U)}V\nI = {self.formater_resultat(I)}A\nR = {self.formater_resultat(R)}Ω\nP = {self.formater_resultat(P)}W"
            )
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_seriekobling_dc(self):
        """Beregner seriekobling av motstander."""
        try:
            R1 = self.konverter_prefiks(self.r_input1.get())
            R2 = self.konverter_prefiks(self.r_input2.get())
            R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0
            R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0
            R_total = R1 + R2 + R3 + R4
            self.resultat_label.configure(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_parallellkobling_dc(self):
        """Beregner parallellkobling av motstander."""
        try:
            R1 = self.konverter_prefiks(self.r_input1.get())
            R2 = self.konverter_prefiks(self.r_input2.get())
            R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else None
            R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else None

            if R3 and R4:
                R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3) + (1 / R4))
            elif R3:
                R_total = 1 / ((1 / R1) + (1 / R2) + (1 / R3))
            else:
                R_total = 1 / ((1 / R1) + (1 / R2))

            self.resultat_label.configure(text=f"Rtotal = {self.formater_resultat(R_total)} Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_vdr_dc(self):
        """Spenningsdeling med fire motstander (VDR)."""
        try:
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
                text=f"UR1 = {self.formater_resultat(V_R1)} V\nUR2 = {self.formater_resultat(V_R2)} V\nUR3 = {self.formater_resultat(V_R3)} V\nUR4 = {self.formater_resultat(V_R4)} V"
            )
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_cdr_dc(self):
        """Strømdeling med fire motstander (CDR)."""
        try:
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
                    text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A\nIR3 = {self.formater_resultat(I_R3)} A\nIR4 = {self.formater_resultat(I_R4)} A"
                )
            elif R3:
                I_R1 = I_in * ((R2 * R3) / (R1 * (R2 + R3) + R2 * R3))
                I_R2 = I_in * ((R1 * R3) / (R1 * (R2 + R3) + R2 * R3))
                I_R3 = I_in * ((R1 * R2) / (R1 * (R2 + R3) + R2 * R3))
                self.resultat_label.configure(
                    text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A\nIR3 = {self.formater_resultat(I_R3)} A"
                )
            else:
                I_R1 = I_in * R2 / (R1 + R2)
                I_R2 = I_in * R1 / (R1 + R2)
                self.resultat_label.configure(
                    text=f"IR1 = {self.formater_resultat(I_R1)} A\nIR2 = {self.formater_resultat(I_R2)} A"
                )
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))


    def kopier_resultat(self):
        """Kopierer resultatet til utklippstavlen."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.resultat_label.cget("text"))
        #messagebox.showinfo("Kopiert", "Resultatet er kopiert til utklippstavlen!")

    def oppdater_beregning(self, event=None):
        # Oppdater input-felt basert på valgt beregning
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        beregning = self.beregningsvalg.get()

        if beregning == "Ohms lov":
            ctk.CTkLabel(self.input_frame, text="Spenning (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.u_input = ctk.CTkEntry(self.input_frame)
            self.u_input.grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Strøm (A):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.i_input = ctk.CTkEntry(self.input_frame)
            self.i_input.grid(row=1, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input = ctk.CTkEntry(self.input_frame)
            self.r_input.grid(row=2, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Effekt (W):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.p_input = ctk.CTkEntry(self.input_frame)
            self.p_input.grid(row=3, column=1, padx=10, pady=5)

            beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_ohms_lov_dc)
            beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

        elif beregning == "Seriekobling":
            ctk.CTkLabel(self.input_frame, text="Motstand 1 (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = ctk.CTkEntry(self.input_frame)
            self.r_input1.grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 2 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = ctk.CTkEntry(self.input_frame)
            self.r_input2.grid(row=1, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 3 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = ctk.CTkEntry(self.input_frame)
            self.r_input3.grid(row=2, column=1, padx=10, pady=5)
            
            ctk.CTkLabel(self.input_frame, text="Motstand 4 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.r_input4 = ctk.CTkEntry(self.input_frame)
            self.r_input4.grid(row=3, column=1, padx=10, pady=5)

            beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_seriekobling_dc)
            beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

        elif beregning == "Parallellkobling":
            ctk.CTkLabel(self.input_frame, text="Motstand 1 (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = ctk.CTkEntry(self.input_frame)
            self.r_input1.grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 2 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = ctk.CTkEntry(self.input_frame)
            self.r_input2.grid(row=1, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 3 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = ctk.CTkEntry(self.input_frame)
            self.r_input3.grid(row=2, column=1, padx=10, pady=5)
            
            ctk.CTkLabel(self.input_frame, text="Motstand 4 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.r_input4 = ctk.CTkEntry(self.input_frame)
            self.r_input4.grid(row=3, column=1, padx=10, pady=5)

            beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_parallellkobling_dc)
            beregn_knapp.grid(row=4, column=0, columnspan=2, pady=20)

        elif beregning == "VDR":
            ctk.CTkLabel(self.input_frame, text="Inngangsspenning (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.vin_input = ctk.CTkEntry(self.input_frame)
            self.vin_input.grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 1 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = ctk.CTkEntry(self.input_frame)
            self.r_input1.grid(row=1, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 2 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = ctk.CTkEntry(self.input_frame)
            self.r_input2.grid(row=2, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 3 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = ctk.CTkEntry(self.input_frame)
            self.r_input3.grid(row=3, column=1, padx=10, pady=5)
            
            ctk.CTkLabel(self.input_frame, text="Motstand 4 (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.r_input4 = ctk.CTkEntry(self.input_frame)
            self.r_input4.grid(row=4, column=1, padx=10, pady=5)

            beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_vdr_dc)
            beregn_knapp.grid(row=5, column=0, columnspan=2, pady=20)

        elif beregning == "CDR":
            ctk.CTkLabel(self.input_frame, text="Inngangsstrøm (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
            self.iin_input = ctk.CTkEntry(self.input_frame)
            self.iin_input.grid(row=0, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 1 (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
            self.r_input1 = ctk.CTkEntry(self.input_frame)
            self.r_input1.grid(row=1, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 2 (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
            self.r_input2 = ctk.CTkEntry(self.input_frame)
            self.r_input2.grid(row=2, column=1, padx=10, pady=5)

            ctk.CTkLabel(self.input_frame, text="Motstand 3 (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
            self.r_input3 = ctk.CTkEntry(self.input_frame)
            self.r_input3.grid(row=3, column=1, padx=10, pady=5)
            
            ctk.CTkLabel(self.input_frame, text="Motstand 4 (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.r_input4 = ctk.CTkEntry(self.input_frame)
            self.r_input4.grid(row=4, column=1, padx=10, pady=5)

            beregn_knapp = ctk.CTkButton(self.input_frame, text="Beregn", command=self.beregn_cdr_dc)
            beregn_knapp.grid(row=5, column=0, columnspan=2, pady=20)


if __name__ == "__main__":
    root = ctk.CTk()  # Bruk CustomTkinter CTk for hovedvinduet
    app = KalkulatorApp(root)
    root.mainloop()