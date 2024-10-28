    def beregn_ohms_lov(self):
        kalk_type = self.kalkvalg.get()  # Hent valgt kalkulatortype

        try:
            # Hvis kalkulatoren er satt til DC
            if kalk_type == "DC":
                U = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
                I = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
                R = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
                P = self.konverter_prefiks(self.p_input.get()) if self.p_input.get() else None

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
                U_mag = self.konverter_prefiks(self.u_input.get()) if self.u_input.get() else None
                U_fase = math.radians(float(self.u_fase_input.get().replace(',', '.'))) if self.u_fase_input.get() else 0
                Z_mag = self.konverter_prefiks(self.r_input.get()) if self.r_input.get() else None
                Z_fase = math.radians(float(self.z_fase_input.get().replace(',', '.'))) if self.z_fase_input.get() else 0
                I_mag = self.konverter_prefiks(self.i_input.get()) if self.i_input.get() else None
                I_fase = math.radians(float(self.i_fase_input.get().replace(',', '.'))) if self.i_fase_input.get() else 0

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
                R1 = self.konverter_prefiks(self.r_input1.get())
                R2 = self.konverter_prefiks(self.r_input2.get()) 
                R3 = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0
                R4 = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0
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
        kalk_type = self.kalkvalg.get()
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
                    
                    Z3_re = self.konverter_prefiks(self.r_input3.get()) if self.r_input3.get() else 0.0
                    Z3_im = self.konverter_prefiks(self.p_input3.get()) if self.p_input3.get() else 0.0
                    Z3 = complex(Z3_re, Z3_im)
                    
                    Z4_re = self.konverter_prefiks(self.r_input4.get()) if self.r_input4.get() else 0.0
                    Z4_im = self.konverter_prefiks(self.p_input4.get()) if self.p_input4.get() else 0.0
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