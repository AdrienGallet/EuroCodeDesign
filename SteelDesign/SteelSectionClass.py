import math

"""
------ Assumptions
- Sections are symmetrical over their zz-axis (will require reviewing all zz based section properties if I change this conditions)
- Currently only applies to S355 steel
"""

"""
------ Conservatism
- Section classes are evaluated assuming full compression only
- Outstanding flange for the shear lag check does not take into account the radius
"""

"""
------ Incorrectness
- Root radius are not correctly considered in the evaluation of the plastic NA
- For welded sections, c/t should exclude the sizes of the welds (currently it would include them)
"""

"""
------ Out of scope
- Shear lag, plate buckling, shear buckling checks are simply limited, not carried out. 
- Flange induced buckling and transverse load check not carried out
"""

class OpenCrossSection():
	def __init__(self,bf_top=0, tf_top=0, tw=0, dw=0, bf_bot=0, tf_bot=0, r=0, type='custom'):
		# Assign section properties to self
		self.type='custom'
		self.bf_top = bf_top #Bottom flange width
		self.tf_top = tf_top #Top flange thickness
		self.tw = tw #Web thickness
		self.dw = dw #Web fillet depth
		self.bf_bot = bf_bot #Bottom flange width
		self.tf_bot = tf_bot #Bottom flange thickness
		self.r = r #Root radius

		# --- Calulate section properties
		# Total depth
		self.h = self.dw + 2*self.r + self.tf_top + self.tf_bot

		# Cross-section area
		self.A = self.bf_top * self.tf_top + \
				(self.dw + 2*self.r) * self.tw + \
				self.bf_bot * self.tf_bot + \
				4 * self.r**2*(1 - 0.25*math.pi)

		# Mass per metre (p=7850kg/m^3)
		self.mpm = self.A * 7850 * 10**-6

		# Elastic neutral axis - Major axis (yy) (based on first moment of area)
		self.eNAyy = ( (self.tf_top * self.bf_top) * (self.h - 0.5*self.tf_top) + \
					 (self.tw * (self.dw + 2*self.r)) * (self.tf_bot + 0.5*(self.dw + 2*self.r)) + \
					 (self.tf_bot * self.bf_bot) * (0.5*self.tf_bot) + \
					 (2 * (self.r**2*(1 - 0.25*math.pi)) * (self.tf_bot+0.223367*self.r)) + \
					 (2 * (self.r**2*(1 - 0.25*math.pi)) * (self.h - self.tf_top - 0.223367*self.r)) ) / self.A

		# Elastic neutral axis - Minor axis (zz) (based on first moment of area)
		self.eNAzz = 0.5*max(bf_top, bf_bot, tw) #This is because cross-sections considered here are symmetrical accross the zz-axis

		# Plastic neutral axis - Major axis (yy) (based on equal areas)
		A_f_top = self.bf_top * self.tf_top
		A_w = self.tw * (self.dw + 2*self.r) + 4*(self.r**2*(1 - 0.25*math.pi))
		A_f_bot = self.bf_bot * self.tf_bot

		# Evaluate location of pNA
		if A_f_top + A_w < A_f_bot:
			# NA within bottom flange
			self.pNA_location = 'flange_top'
			self.pNAyy = (A_f_top + A_w) / self.bf_bot
		elif A_f_bot + A_w < A_f_top:
			# NA within top flange
			self.pNA_location = 'flange_bot'
			self.pNAyy = self.h - ((A_f_bot + A_w) / self.bf_top)
		else:
			# NA within web
			self.pNA_location = 'web'
			delta_y = (A_f_top - A_f_bot) / self.tw
			self.pNAyy = (self.tf_bot + self.r + 0.5*self.dw) - delta_y

			# Note: if pNAyy is within radius range, then delta y will be slightly incorrect.
			if self.r != 0 and (self.pNAyy < self.tf_bot+self.r or self.pNAyy > self.h - self.tf_top - self.r):
				print("WARNING: Plastic NA within root fillet, yet root fillet area is not accounted for.")
				if(self.pNAyy < self.tf_bot+self.r):
					self.pNAyy = max(self.tf_bot,self.pNAyy) #Forces pNA to stay within bottom of web
				elif(self.pNAyy > self.h - self.tf_top - self.r):
					self.pNAyy = min(self.h - self.tf_top,self.pNAyy) #Forces pNA to stay within top of web
			
		# Plastic neural axis - Minor axis (zz) (based on equal area)
		self.pNAzz = 0.5*max(bf_top, bf_bot, tw) #This is because cross-sections considered here are symmetrical accross the zz-axis

		# Second moment of area - Major axis (yy)
		Iyy_web = (self.eNAyy - (self.tf_bot+self.r+0.5*self.dw))**2 * ((self.dw+2*self.r)*self.tw) + (self.tw*(self.dw+2*self.r)**3/12)
		Iyy_flange_top = (self.eNAyy - (self.h - 0.5*self.tf_top))**2 * (self.tf_top*self.bf_top) + (self.bf_top*self.tf_top**3/12)
		Iyy_flange_bot = (self.eNAyy - (0.5*self.tf_bot))**2 * (self.tf_bot*self.bf_bot) + (self.bf_bot*self.tf_bot**3/12)
		Iyy_root_fillet_bot = 2* ((self.eNAyy - self.tf_bot - 0.223367*self.r)**2 * (self.r**2*(1 - 0.25*math.pi)) + \
							  (self.r**4 * 0.0732137) )
		Iyy_root_fillet_top = 2* (((self.h - self.tf_top - 0.223367*self.r) - self.eNAyy)**2 * (self.r**2*(1 - 0.25*math.pi)) + \
							  (self.r**4 * 0.0732137) )
		self.Iyy = Iyy_web + Iyy_flange_top + Iyy_flange_bot + Iyy_root_fillet_bot + Iyy_root_fillet_top

		# Second moment of area - Minor axis (zz)
		Izz_web = (self.dw + 2*self.r) * self.tw**3 / 12
		Izz_flange_bot =  self.tf_bot*self.bf_bot**3 / 12
		Izz_flange_top = self.tf_top*self.bf_top**3 / 12
		Izz_root_fillet_bot = 2 * (self.r**4 * 0.0732137 + self.r**2*(1 - 0.25*math.pi)* (0.5*self.tw + 0.223367*self.r))
		Izz_root_fillet_top = 2 * (self.r**4 * 0.0732137 + self.r**2*(1 - 0.25*math.pi)* (0.5*self.tw + 0.223367*self.r))
		self.Izz = Izz_web + Izz_flange_top + Izz_flange_bot + Izz_root_fillet_bot + Izz_root_fillet_top


		# Radius of gyration - Major axis (yy)
		self.ryy = math.sqrt(self.Iyy/self.A)

		# Radius of gyration - Minor axis (zz)
		self.rzz = math.sqrt(self.Izz/self.A)

		# Elastic modulus to top flange - Major axis (yy)
		self.Wel_yy_top = self.Iyy / (self.h - self.eNAyy)

		# Elastic modulus to bottom flange - Major axis (yy)
		self.Wel_yy_bot = self.Iyy / (-self.eNAyy)

		# Plastic modulus - Major axis (yy)
		if self.pNA_location == 'web':
			area_above_NA_in_web = (self.dw + 2*self.r + self.tf_bot - self.pNAyy) * self.tw
			centroid_to_area_above_NA_in_web = 0.5*(self.dw + 2*self.r + self.tf_bot - self.pNAyy)
			area_above_NA_in_root_fillet = 2*(self.r**2*(1 - 0.25*math.pi))
			centroid_to_area_above_NA_in_root_fillet = ((self.h - self.tf_top - 0.223367*self.r) - self.pNAyy)
			area_flange_top = self.tf_top * self.bf_top
			centroid_to_area_flange_top = (self.dw + 2*self.r + self.tf_bot - self.pNAyy) + 0.5*self.tf_top

			area_below_NA_in_web = (self.pNAyy - self.tf_bot) * self.tw
			centroid_to_area_below_NA_in_web = 0.5*(self.pNAyy - self.tf_bot)
			area_below_NA_in_root_fillet = 2*(self.r**2*(1 - 0.25*math.pi))
			centroid_to_area_above_NA_in_root_fillet = (self.eNAyy - self.tf_bot - 0.223367*self.r)
			area_flange_bottom = self.tf_bot * self.bf_bot
			centroid_to_area_flange_bottom = self.pNAyy - 0.5*self.tf_bot

			self.Wpl_yy = area_above_NA_in_web * centroid_to_area_above_NA_in_web + \
						  area_above_NA_in_root_fillet * centroid_to_area_above_NA_in_root_fillet + \
						  area_flange_top * centroid_to_area_flange_top + \
						  area_below_NA_in_web * centroid_to_area_below_NA_in_web + \
						  area_below_NA_in_root_fillet * centroid_to_area_above_NA_in_root_fillet + \
						  area_flange_bottom * centroid_to_area_flange_bottom

		# Elastic modulus to top flange - Minor axis (zz)
		self.Wel_zz_bot = self.Izz / (0.5*self.bf_bot)

		# Elastic modulus to bottom flange - Minor axis (zz)
		self.Wel_zz_top = self.Izz / (0.5*self.bf_top)

		# Plastic modulus - Minor axis (zz)
		areas_in_root_fillet = 4*(self.r**2*(1 - 0.25*math.pi))
		centroid_to_areas_in_root_fillet = (self.tw + 0.223367*self.r)

		self.Wpl_zz = self.tf_bot * self.bf_bot**2 / 4 + \
					  self.tf_top * self.bf_top**2 / 4 + \
					  (self.dw + 2*self.r) * self.tw**2 / 4 + \
					  areas_in_root_fillet * centroid_to_areas_in_root_fillet

		# Shear area - Major Axis (z)
		if(self.type == 'I_rolled'):
			self.Av_z = self.A - self.bf_bot*self.tf_bot - self.bf_top*self.tf_top + \
						(self.tw+self.r)*0.5*self.tf_bot + (self.tw+self.r)*0.5*self.tf_top
		else:
			self.Av_z = self.A - self.bf_bot*self.tf_bot - self.bf_top*self.tf_top

		# Shear area - Minor Axis (y)
		self.Av_y = self.bf_bot*self.tf_bot - self.bf_top*self.tf_top

		# Define section class 
		# Check internal compression part (web)
		if(self.dw/self.tw < 33 * 0.81): sclass_web = 1
		elif(self.dw/self.tw < 38 * 0.81): sclass_web = 2
		elif(self.dw/self.tw < 42 * 0.81): sclass_web = 3
		else: sclass_web = 4

		# Check external compression part (flange)
		# Top flange
		if(0.5*(self.bf_top-self.tw-2*self.r) /self.tf_top < 9 * 0.81): sclass_flange_top = 1
		elif(0.5*(self.bf_top-self.tw-2*self.r) /self.tf_top < 10 * 0.81): sclass_flange_top = 2
		elif(0.5*(self.bf_top-self.tw-2*self.r) /self.tf_top < 14 * 0.81): sclass_flange_top = 3
		else: sclass_flange_top = 4

		# Bottom flange
		if(0.5*(self.bf_bot-self.tw-2*self.r) / self.tf_bot < 9 * 0.81): sclass_flange_bot = 1
		elif(0.5*(self.bf_bot-self.tw-2*self.r) / self.tf_bot < 10 * 0.81): sclass_flange_bot = 2
		elif(0.5*(self.bf_bot-self.tw-2*self.r) / self.tf_bot < 14 * 0.81): sclass_flange_bot = 3
		else: sclass_flange_bot = 4

		self.sclass = max(sclass_web, sclass_flange_top, sclass_flange_bot)


	def local_plate_checks(self, L_zeroM=0):
		print("Local plate checks conducted now.")

		#--- Shear lag check, BS EN 1993-1-5 3.
		# Check top flange 
		if (L_zeroM/50.0 < (self.bf_top - self.tw)/2): #BS EN 1993-1-5 3.1(1)
			print('Out of scope: shear lag in top flange needs to be considered.')
			return False
		# Check bottom flange
		if(L_zeroM/50.0 < (self.bf_bot - self.tw)/2): #BS EN 1993-1-5 3.1(1)
			print('Out of scope: shear lag in bottom flange needs to be considered.')
			return False

		#--- Plate buckling checks, BS EN 1993-1-5 4.
		if(self.sclass > 3):
			print('Out of scope: section is class 4.')
			return False

		#--- Shear buckling checks, BS EN 1993-1-5 5.
		if( (self.dw+self.r*2) < 72*0.81 ):
			print('Out of scope: shear buckling needs to be considered.')
			return False

		print('Local plate checks: OK!')
		return True




class ISection(OpenCrossSection):
	def __init__(self, b=0, tf=0, tw=0, dw=0, r=0):
		super().__init__(bf_top=b, tf_top=tf, tw=tw, dw=dw, bf_bot=b, tf_bot=tf, r=r)
		self.type = 'I_rolled' #Cross section (xs) type




"""
# Evaluate the following properties
- Warping constant
- Torsional constant
- Surface area per meter and per tonne
- Ratios for local buckling (to avoid plate buckling)

- Look into buckling parameters and torsional index

- Update yml file, and leave instructions for others to collaborate with/work on the code

"""

	


