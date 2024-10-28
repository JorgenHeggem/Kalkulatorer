# Jørgen Heggem sin AC Kalkulator
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import cmath
import math

class KalkulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AC Kalkulator")
        self.root.geometry("700x700")

        # Håndter riktig ikonbane
        ikon_bane = self.finn_ikon_bane()
        if ikon_bane:
            try:
                self.root.iconbitmap(ikon_bane)
            except Exception as e:
                print(f"Kunne ikke sette ikonet: {e}")

        # GUI-tilstand (variabler for inputfeltene)
        self.u_input = None
        self.form_valg = "Polar"  # Standard er polar form

        # Opprett GUI-elementer
        self.lag_gui()

    def finn_ikon_bane(self):
        """Hjelpefunksjon for å finne riktig bane til ikonet."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, "AC Kalkulator ikon.ico")
        else:
            return os.path.join(os.path.dirname(__file__), "AC Kalkulator ikon.ico")

    def lag_gui(self):
        # Hovedramme som inneholder både "utregningsfeltet" og notatene
        hovedramme = tk.Frame(self.root)
        hovedramme.pack(fill="both", expand=True)

        # Venstre ramme for "utregningsfeltet"
        venstre_ramme = tk.Frame(hovedramme)
        venstre_ramme.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Høyre ramme for notatene
        hoyre_ramme = tk.Frame(hovedramme)
        hoyre_ramme.pack(side="right", fill="y", padx=10, pady=10)

        # Valg av beregningstype
        tk.Label(venstre_ramme, text="Velg beregning:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.beregningsvalg = ttk.Combobox(venstre_ramme, state="readonly", 
                                           values=["Ohms lov", "Seriekobling", "Parallellkobling", "VDR", "CDR", "Kap og Ind"], font=("Arial", 10))
        self.beregningsvalg.current(0)
        self.beregningsvalg.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.beregningsvalg.bind("<<ComboboxSelected>>", self.oppdater_beregning)

        # Valg av form (Polar eller Rektangulær)
        self.form_label = tk.Label(venstre_ramme, text="Velg form:", font=("Arial", 12, "bold"))
        self.form_valg = ttk.Combobox(venstre_ramme, values=["Polar", "Rektangulær"], state="readonly", font=("Arial", 10))
        self.form_valg.current(0)
        self.form_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.form_valg.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.form_valg.bind("<<ComboboxSelected>>", self.oppdater_beregning)

        # Valg for komponent (Kondensator eller Spole) - starter skjult
        self.komponent_label = tk.Label(venstre_ramme, text="Velg komponent:", font=("Arial", 12, "bold"))
        self.komponent_valg = ttk.Combobox(venstre_ramme, state="readonly", values=["Kondensator", "Spole"], font=("Arial", 10))
        self.komponent_valg.current(0)
        self.komponent_valg.bind("<<ComboboxSelected>>", self.oppdater_beregning)

        # Resten av GUI-komponentene
        self.input_ramme = tk.Frame(venstre_ramme)
        self.input_ramme.grid(row=2, column=0, columnspan=2, pady=20)

        self.resultat_label = tk.Label(venstre_ramme, text="Resultat:", font=("Arial", 12))
        self.resultat_label.grid(row=3, column=0, columnspan=2, pady=10)

        self.kopier_knapp = tk.Button(venstre_ramme, text="Kopier resultat", command=self.kopier_resultat)
        self.kopier_knapp.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Label(hoyre_ramme, text="Notater:", font=("Arial", 12)).pack(pady=5)
        self.notater_boks = tk.Text(hoyre_ramme, height=20, width=30)
        self.notater_boks.pack(pady=10)
        
            # Sett inn forhåndsdefinert tekst i tekstboksen på én linje
        self.notater_boks.insert(tk.END, "Støttede prefikser: T, G, M, k, m, µ, n")


        # Start med standard beregning
        self.oppdater_beregning()




    def konverter_prefiks(self, verdi):
        verdi = verdi.strip().lower()
        try:
            if 'k' in verdi:
                return float(verdi.replace('k', '')) * 1e3
            elif 'm' in verdi and 'µ' not in verdi:
                return float(verdi.replace('m', '')) * 1e-3
            elif 'µ' in verdi:
                return float(verdi.replace('µ', '')) * 1e-6
            elif 'g' in verdi:
                return float(verdi.replace('g', '')) * 1e9
            elif 'M' in verdi:
                return float(verdi.replace('M', '')) * 1e6
            else:
                return float(verdi)
        except ValueError:
            raise ValueError("Ugyldig verdi for prefiks!")

    def formater_resultat(self, verdi):
        enheter = [
            (1e-9, 'n'), (1e-6, 'µ'), (1e-3, 'm'), (1, ''),
            (1e3, 'k'), (1e6, 'M'), (1e9, 'G'), (1e12, 'T')
        ]
        for faktor, enhet in enheter:
            if abs(verdi) < faktor * 1000:
                return f"{verdi / faktor:.2f} {enhet}"
        return f"{verdi:.2f}"

    def beregn_ohms_lov_ac(self):
        """AC versjon av Ohms lov, med polar og rektangulær form, og separate fasevinkler for spenning, strøm og impedans."""
        try:
            U_mag = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
            U_fase = math.radians(float(self.u_fase_input.get())) if self.u_fase_input.get() else 0
            Z_mag = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
            Z_fase = math.radians(float(self.z_fase_input.get())) if self.z_fase_input.get() else 0
            I_mag = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
            I_fase = math.radians(float(self.i_fase_input.get())) if self.i_fase_input.get() else 0

            if self.form_valg.get() == "Polar":
                if U_mag and Z_mag:  # U og Z gitt
                    U = cmath.rect(U_mag, U_fase)
                    Z = cmath.rect(Z_mag, Z_fase)
                    I = U / Z
                elif U_mag and I_mag:  # U og I gitt
                    U = cmath.rect(U_mag, U_fase)
                    I = cmath.rect(I_mag, I_fase)
                    Z = U / I
                elif Z_mag and I_mag:  # Z og I gitt
                    Z = cmath.rect(Z_mag, Z_fase)
                    I = cmath.rect(I_mag, I_fase)
                    U = I * Z

            else:  # Rektangulær form
                U_re = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
                U_im = self.konverter_prefiks(self.u_fase_input.get()) if self.u_fase_input.get() else None
                Z_re = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
                Z_im = self.konverter_prefiks(self.z_fase_input.get()) if self.z_fase_input.get() else None
                I_re = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
                I_im = self.konverter_prefiks(self.i_fase_input.get()) if self.i_fase_input.get() else None

                if U_re and Z_re:  # U og Z gitt
                    U = complex(U_re, U_im)
                    Z = complex(Z_re, Z_im)
                    I = U / Z
                elif U_re and I_re:  # U og I gitt
                    U = complex(U_re, U_im)
                    I = complex(I_re, I_im)
                    Z = U / I
                elif Z_re and I_re:  # Z og I gitt
                    Z = complex(Z_re, Z_im)
                    I = complex(I_re, I_im)
                    U = I * Z

            if not any([U, I, Z]):
                raise ValueError("Fyll inn minst to verdier for å beregne de andre.")

            self.resultat_label.config(text=f"U = {self.formater_resultat(abs(U))} ∠ {math.degrees(cmath.phase(U)):.2f}° V\n"
                                            f"Z = {self.formater_resultat(abs(Z))} ∠ {math.degrees(cmath.phase(Z)):.2f}° Ω\n"
                                            f"I = {self.formater_resultat(abs(I))} ∠ {math.degrees(cmath.phase(I)):.2f}° A")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_seriekobling_ac(self):
        """AC seriekobling (polar og rektangulær form)."""
        try:
            Z_total = 0 + 0j  # Start med 0 + 0j

            for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                if impedans_input.get():
                    if self.form_valg.get() == "Polar":
                        Z_mag = self.konverter_prefiks(impedans_input.get())
                        Z_fase = math.radians(float(fase_input.get()))
                        Z = cmath.rect(Z_mag, Z_fase)
                    else:
                        Z_re = self.konverter_prefiks(impedans_input.get())
                        Z_im = self.konverter_prefiks(fase_input.get())
                        Z = complex(Z_re, Z_im)
                    Z_total += Z

            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_seriekobling_ac(self):
        """AC seriekobling (polar og rektangulær form)."""
        try:
            Z_total = 0 + 0j  # Start med 0 + 0j

            for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                if impedans_input.get():
                    if self.form_valg.get() == "Polar":
                        Z_mag = self.konverter_prefiks(impedans_input.get())
                        Z_fase = math.radians(float(fase_input.get()))
                        Z = cmath.rect(Z_mag, Z_fase)
                    else:
                        Z_re = self.konverter_prefiks(impedans_input.get())
                        Z_im = self.konverter_prefiks(fase_input.get())
                        Z = complex(Z_re, Z_im)
                    Z_total += Z

            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_seriekobling_ac(self):
        """AC seriekobling (polar og rektangulær form)."""
        try:
            Z_total = 0 + 0j  # Start med 0 + 0j

            for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                if impedans_input.get():
                    if self.form_valg.get() == "Polar":
                        Z_mag = self.konverter_prefiks(impedans_input.get())
                        Z_fase = math.radians(float(fase_input.get()))
                        Z = cmath.rect(Z_mag, Z_fase)
                    else:
                        Z_re = self.konverter_prefiks(impedans_input.get())
                        Z_im = self.konverter_prefiks(fase_input.get())
                        Z = complex(Z_re, Z_im)
                    Z_total += Z

            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_seriekobling_ac(self):
        """AC seriekobling (polar og rektangulær form)."""
        try:
            Z_total = 0 + 0j  # Start med 0 + 0j

            for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                if impedans_input.get():
                    if self.form_valg.get() == "Polar":
                        Z_mag = self.konverter_prefiks(impedans_input.get())
                        Z_fase = math.radians(float(fase_input.get()))
                        Z = cmath.rect(Z_mag, Z_fase)
                    else:
                        Z_re = self.konverter_prefiks(impedans_input.get())
                        Z_im = self.konverter_prefiks(fase_input.get())
                        Z = complex(Z_re, Z_im)
                    Z_total += Z

            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_parallellkobling_ac(self):
        """AC parallellkobling (polar og rektangulær form)."""
        try:
            Z_total_inv = 0 + 0j  # Start med 0 + 0j

            for impedans_input, fase_input in [(self.r_input1, self.p_input1), (self.r_input2, self.p_input2), (self.r_input3, self.p_input3), (self.r_input4, self.p_input4)]:
                if impedans_input.get():
                    if self.form_valg.get() == "Polar":
                        Z_mag = self.konverter_prefiks(impedans_input.get())
                        Z_fase = math.radians(float(fase_input.get()))
                        Z = cmath.rect(Z_mag, Z_fase)
                    else:
                        Z_re = self.konverter_prefiks(impedans_input.get())
                        Z_im = self.konverter_prefiks(fase_input.get())
                        Z = complex(Z_re, Z_im)
                    Z_total_inv += 1 / Z

            if Z_total_inv == 0:
                raise ValueError("Ingen gyldige impedanser oppgitt.")

            Z_total = 1 / Z_total_inv

            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))

    def beregn_vdr_ac(self):
        """AC spenningsdeling (polar og rektangulær form)."""
        try:
            if self.form_valg.get() == "Polar":
                Vin_mag = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else 0
                Vin_fase = math.radians(float(self.p_input.get())) if self.p_input.get() else 0
                Vin = cmath.rect(Vin_mag, Vin_fase)

                Z1_mag = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0
                Z1_fase = math.radians(float(self.p_input1.get())) if self.p_input1.get() else 0
                Z1 = cmath.rect(Z1_mag, Z1_fase)

                Z2_mag = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0
                Z2_fase = math.radians(float(self.p_input2.get())) if self.p_input2.get() else 0
                Z2 = cmath.rect(Z2_mag, Z2_fase)

                Z3_mag = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0
                Z3_fase = math.radians(float(self.p_input3.get())) if self.p_input3.get() else 0
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
            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω\n"
                                            f"V1 = {self.formater_resultat(abs(V1))} ∠ {math.degrees(cmath.phase(V1)):.2f}° V\n"
                                            f"V2 = {self.formater_resultat(abs(V2))} ∠ {math.degrees(cmath.phase(V2)):.2f}° V\n"
                                            f"V3 = {self.formater_resultat(abs(V3))} ∠ {math.degrees(cmath.phase(V3)):.2f}° V")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))


    def beregn_cdr_ac(self):
        """AC strømdeling (polar og rektangulær form)."""
        try:
            if self.form_valg.get() == "Polar":
                # Kontroller at verdiene ikke er tomme og sett en standardverdi hvis de er
                Iin_mag = self.konverter_prefiks(self.vin_input.get()) if self.vin_input.get() else 0.0
                Iin_fase = math.radians(float(self.p_input.get())) if self.p_input.get() else 0.0
                Iin = cmath.rect(Iin_mag, Iin_fase)

                Z1_mag = self.konverter_prefiks(self.r_input1.get()) if self.r_input1.get() else 0.0
                Z1_fase = math.radians(float(self.p_input1.get())) if self.p_input1.get() else 0.0
                Z1 = cmath.rect(Z1_mag, Z1_fase)

                Z2_mag = self.konverter_prefiks(self.r_input2.get()) if self.r_input2.get() else 0.0
                Z2_fase = math.radians(float(self.p_input2.get())) if self.p_input2.get() else 0.0
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

            self.resultat_label.config(text=f"Z_total = {self.formater_resultat(abs(Z_total))} ∠ {math.degrees(cmath.phase(Z_total)):.2f}° Ω\n"
                                            f"I1 = {self.formater_resultat(abs(I1))} ∠ {math.degrees(cmath.phase(I1)):.2f}° A\n"
                                            f"I2 = {self.formater_resultat(abs(I2))} ∠ {math.degrees(cmath.phase(I2)):.2f}° A")
        except ValueError as e:
            messagebox.showerror("Input Feil", str(e))
            
    def beregn_kap_og_ind_ac(self):
        try:
            if self.komponent_valg.get() == "Kondensator":
                C = self.konverter_prefiks(self.c_input.get())
                f = self.konverter_prefiks(self.f_input.get())
                Z = 1 / (2 * math.pi * f * C)
                self.resultat_label.config(text=f"Z = {self.formater_resultat(Z)} ∠-90° Ω")
            else:  # Spole
                L = self.konverter_prefiks(self.l_input.get())
                f = self.konverter_prefiks(self.f_input.get())
                Z = 2 * math.pi * f * L
                self.resultat_label.config(text=f"Z = {self.formater_resultat(Z)} ∠90° Ω")
        except ValueError as e:
            messagebox.showerror("Input Feil", f"Ugyldig input: {str(e)}")
            
                


    def kopier_resultat(self):
        """Kopierer resultatet til utklippstavlen."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.resultat_label.cget("text"))
        messagebox.showinfo("Kopiert", "Resultatet er kopiert til utklippstavlen!")

    def oppdater_beregning(self, *args):
        # Tømmer input-felt
        for widget in self.input_ramme.winfo_children():
            widget.destroy()

        beregning = self.beregningsvalg.get()
        form = self.form_valg.get()

        if beregning == "Ohms lov":
            if form == "Polar":
                tk.Label(self.input_ramme, text="Spenningens magnitude (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.u_input = tk.Entry(self.input_ramme)
                self.u_input.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Spenningens fasevinkel (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.u_fase_input = tk.Entry(self.input_ramme)
                self.u_fase_input.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Strømmens magnitude (A):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.i_input = tk.Entry(self.input_ramme)
                self.i_input.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Strømmens fasevinkel (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.i_fase_input = tk.Entry(self.input_ramme)
                self.i_fase_input.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedansens magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input = tk.Entry(self.input_ramme)
                self.r_input.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedansens fasevinkel (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.z_fase_input = tk.Entry(self.input_ramme)
                self.z_fase_input.grid(row=5, column=1, padx=10, pady=5)
            else:
                tk.Label(self.input_ramme, text="Spenningens reelle del (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.u_input = tk.Entry(self.input_ramme)
                self.u_input.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Spenningens imaginære del (V):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.u_fase_input = tk.Entry(self.input_ramme)
                self.u_fase_input.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Strømmens reelle del (A):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.i_input = tk.Entry(self.input_ramme)
                self.i_input.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Strømmens imaginære del (A):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.i_fase_input = tk.Entry(self.input_ramme)
                self.i_fase_input.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedansens reelle del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input = tk.Entry(self.input_ramme)
                self.r_input.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedansens imaginære del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.z_fase_input = tk.Entry(self.input_ramme)
                self.z_fase_input.grid(row=5, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_ramme, text="Beregn", command=self.beregn_ohms_lov_ac)
            beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)

        elif beregning == "Seriekobling" or beregning == "Parallellkobling":
            # Skjul komponent-valg og vis form-valg på samme sted
            
            self.komponent_label.grid_forget()  # Skjuler etiketten for komponent
            self.komponent_valg.grid_forget()   # Skjuler comboboxen for komponent
            
            self.form_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
            self.form_valg.grid(row=1, column=1, padx=10, pady=10, sticky="w")

            form = self.form_valg.get()
            beregn_knapp = None
            if form == "Polar":
                tk.Label(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = tk.Entry(self.input_ramme)
                self.r_input1.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.p_input1 = tk.Entry(self.input_ramme)
                self.p_input1.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = tk.Entry(self.input_ramme)
                self.r_input2.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input2 = tk.Entry(self.input_ramme)
                self.p_input2.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = tk.Entry(self.input_ramme)
                self.r_input3.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.p_input3 = tk.Entry(self.input_ramme)
                self.p_input3.grid(row=5, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 4 magnitude (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                self.r_input4 = tk.Entry(self.input_ramme)
                self.r_input4.grid(row=6, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 4 fase (grader):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                self.p_input4 = tk.Entry(self.input_ramme)
                self.p_input4.grid(row=7, column=1, padx=10, pady=5)
            else:
                tk.Label(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = tk.Entry(self.input_ramme)
                self.r_input1.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.p_input1 = tk.Entry(self.input_ramme)
                self.p_input1.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = tk.Entry(self.input_ramme)
                self.r_input2.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input2 = tk.Entry(self.input_ramme)
                self.p_input2.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 reell del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = tk.Entry(self.input_ramme)
                self.r_input3.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 imaginær del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.p_input3 = tk.Entry(self.input_ramme)
                self.p_input3.grid(row=5, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 4 reell del (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                self.r_input4 = tk.Entry(self.input_ramme)
                self.r_input4.grid(row=6, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 4 imaginær del (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                self.p_input4 = tk.Entry(self.input_ramme)
                self.p_input4.grid(row=7, column=1, padx=10, pady=5)

            if beregning == "Seriekobling":
                # Skjul komponent-valg og vis form-valg på samme sted
                
                self.komponent_label.grid_forget()  # Skjuler etiketten for komponent
                self.komponent_valg.grid_forget()   # Skjuler comboboxen for komponent
                
                self.form_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
                self.form_valg.grid(row=1, column=1, padx=10, pady=10, sticky="w")

                form = self.form_valg.get()
                beregn_knapp = tk.Button(self.input_ramme, text="Beregn Seriekobling", command=self.beregn_seriekobling_ac)
            else:
                beregn_knapp = tk.Button(self.input_ramme, text="Beregn Parallellkobling", command=self.beregn_parallellkobling_ac)

            beregn_knapp.grid(row=8, column=0, columnspan=2, pady=20)

        elif beregning == "VDR":
            # Skjul komponent-valg og vis form-valg på samme sted
            
            self.komponent_label.grid_forget()  # Skjuler etiketten for komponent
            self.komponent_valg.grid_forget()   # Skjuler comboboxen for komponent
            
            self.form_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
            self.form_valg.grid(row=1, column=1, padx=10, pady=10, sticky="w")

            form = self.form_valg.get()
            
            if form == "Polar":
                tk.Label(self.input_ramme, text="Inngangsspenning magnitude (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.vin_input = tk.Entry(self.input_ramme)
                self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Inngangsspenning fase (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.p_input = tk.Entry(self.input_ramme)
                self.p_input.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = tk.Entry(self.input_ramme)
                self.r_input1.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input1 = tk.Entry(self.input_ramme)
                self.p_input1.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = tk.Entry(self.input_ramme)
                self.r_input2.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.p_input2 = tk.Entry(self.input_ramme)
                self.p_input2.grid(row=5, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 magnitude (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = tk.Entry(self.input_ramme)
                self.r_input3.grid(row=6, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 fase (grader):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                self.p_input3 = tk.Entry(self.input_ramme)
                self.p_input3.grid(row=7, column=1, padx=10, pady=5)
            else:
                tk.Label(self.input_ramme, text="Inngangsspenning reell del (V):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.vin_input = tk.Entry(self.input_ramme)
                self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Inngangsspenning imaginær del (V):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.p_input = tk.Entry(self.input_ramme)
                self.p_input.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = tk.Entry(self.input_ramme)
                self.r_input1.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input1 = tk.Entry(self.input_ramme)
                self.p_input1.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = tk.Entry(self.input_ramme)
                self.r_input2.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.p_input2 = tk.Entry(self.input_ramme)
                self.p_input2.grid(row=5, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 reell del (Ω):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
                self.r_input3 = tk.Entry(self.input_ramme)
                self.r_input3.grid(row=6, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 3 imaginær del (Ω):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
                self.p_input3 = tk.Entry(self.input_ramme)
                self.p_input3.grid(row=7, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_ramme, text="Beregn VDR", command=self.beregn_vdr_ac)
            beregn_knapp.grid(row=8, column=0, columnspan=2, pady=20)

        elif beregning == "CDR":  # Beregning for CDR
            # Skjul komponent-valg og vis form-valg på samme sted
            
            self.komponent_label.grid_forget()  # Skjuler etiketten for komponent
            self.komponent_valg.grid_forget()   # Skjuler comboboxen for komponent
            
            self.form_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
            self.form_valg.grid(row=1, column=1, padx=10, pady=10, sticky="w")

            form = self.form_valg.get()

            
            if form == "Polar":
                tk.Label(self.input_ramme, text="Inngangsstrøm magnitude (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.vin_input = tk.Entry(self.input_ramme)
                self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Inngangsstrøm fase (grader):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.p_input = tk.Entry(self.input_ramme)
                self.p_input.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 magnitude (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = tk.Entry(self.input_ramme)
                self.r_input1.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 fase (grader):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input1 = tk.Entry(self.input_ramme)
                self.p_input1.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 magnitude (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = tk.Entry(self.input_ramme)
                self.r_input2.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 fase (grader):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.p_input2 = tk.Entry(self.input_ramme)
                self.p_input2.grid(row=5, column=1, padx=10, pady=5)

            else:  # For rektangulær form
                tk.Label(self.input_ramme, text="Inngangsstrøm reell del (A):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                self.vin_input = tk.Entry(self.input_ramme)
                self.vin_input.grid(row=0, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Inngangsstrøm imaginær del (A):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                self.p_input = tk.Entry(self.input_ramme)
                self.p_input.grid(row=1, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 reell del (Ω):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
                self.r_input1 = tk.Entry(self.input_ramme)
                self.r_input1.grid(row=2, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 1 imaginær del (Ω):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
                self.p_input1 = tk.Entry(self.input_ramme)
                self.p_input1.grid(row=3, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 reell del (Ω):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
                self.r_input2 = tk.Entry(self.input_ramme)
                self.r_input2.grid(row=4, column=1, padx=10, pady=5)

                tk.Label(self.input_ramme, text="Impedans 2 imaginær del (Ω):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
                self.p_input2 = tk.Entry(self.input_ramme)
                self.p_input2.grid(row=5, column=1, padx=10, pady=5)

            beregn_knapp = tk.Button(self.input_ramme, text="Beregn CDR", command=self.beregn_cdr_ac)
            beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)

        elif beregning == "Kap og Ind":
                    # Skjul form-valg og vis komponent-valgene på samme sted
                    self.form_label.grid_forget()
                    self.form_valg.grid_forget()

                    self.komponent_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
                    self.komponent_valg.grid(row=1, column=1, padx=10, pady=10, sticky="w")

                    komponent = self.komponent_valg.get()

                    if komponent == "Kondensator":
                        tk.Label(self.input_ramme, text="Kapasitanse (C):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                        self.c_input = tk.Entry(self.input_ramme)
                        self.c_input.grid(row=0, column=1, padx=10, pady=5)

                        tk.Label(self.input_ramme, text="Frekvens (f):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                        self.f_input = tk.Entry(self.input_ramme)
                        self.f_input.grid(row=1, column=1, padx=10, pady=5)
                        
                        beregn_knapp = tk.Button(self.input_ramme, text="Beregn Kondensator", command=self.beregn_kap_og_ind_ac)
                        beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)

                    elif komponent == "Spole":
                        tk.Label(self.input_ramme, text="Induktans (L):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
                        self.l_input = tk.Entry(self.input_ramme)
                        self.l_input.grid(row=0, column=1, padx=10, pady=5)

                        tk.Label(self.input_ramme, text="Frekvens (f):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
                        self.f_input = tk.Entry(self.input_ramme)
                        self.f_input.grid(row=1, column=1, padx=10, pady=5)
                        beregn_knapp = tk.Button(self.input_ramme, text="Beregn Spole", command=self.beregn_kap_og_ind_ac)
                        beregn_knapp.grid(row=6, column=0, columnspan=2, pady=20)
                

    def oppdater_kalkulator(self, *args):
        self.oppdater_beregning()


# Opprett hovedvinduet
root = tk.Tk()
app = KalkulatorApp(root)
root.mainloop()