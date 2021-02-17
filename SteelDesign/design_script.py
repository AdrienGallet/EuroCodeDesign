import SteelSectionClass

# Section properties (in mm)
bf_top = 314
tf_top = 64
tw = 36
dw = 868.1
r = 30
bf_bot = 314
tf_bot = 64

# Action effects information
L_zeroM = 18000 # max span in mm between zero bending moments


#xs = SteelSectionClass.OpenCrossSection(bf_top, tf_top, tw, dw, bf_bot, tf_bot, r)
xs = SteelSectionClass.ISection(b=bf_top, tf=tf_top, tw=tw, dw=dw, r=r)

print("Cross-section type: {}".format(xs.type))
print("Cross-section area: {} mm\u00b2".format(xs.A))
print("Total depth: {} mm".format(xs.h))
print("Mass per meter: {} kg/m".format(xs.mpm))
print("Elastic NA yy: {} mm".format(xs.eNAyy))
print("Plastic NA yy: {} mm".format(xs.pNAyy))
print("Second moment of area yy: {} mm\u2074".format(xs.Iyy))
print("Second moment of area yy: {} cm\u2074".format(xs.Iyy/10**4))
print("Radius of gyration yy: {} mm".format(xs.ryy))
print("Elastic modulus top yy: {} mm\u00b3".format(xs.Wel_yy_top))
print("Elastic modulus bottomyy: {} mm\u00b3".format(xs.Wel_yy_bot))
print("Plastic modulus yy: {} mm\u00b3".format(xs.Wpl_yy))
print("Plastic modulus yy: {} cm\u00b3".format(xs.Wpl_yy/10**3))
print("")
print("Elastic NA zz: {} mm".format(xs.eNAzz))
print("Plastic NA zz: {} mm".format(xs.pNAzz))
print("Second moment of area zz: {} mm\u2074".format(xs.Izz))
print("Second moment of area zz: {} cm\u2074".format(xs.Izz/10**4))
print("Radius of gyration zz: {} mm".format(xs.rzz))
print("Elastic modulus top zz: {} mm\u00b3".format(xs.Wel_zz_top))
print("Elastic modulus bottom zz: {} mm\u00b3".format(xs.Wel_zz_bot))
print("Plastic modulus zz: {} mm\u00b3".format(xs.Wpl_zz))
print("Plastic modulus zz: {} cm\u00b3".format(xs.Wpl_zz/10**3))

print("Section class: {}".format(xs.sclass))

xs.local_plate_checks(L_zeroM)


