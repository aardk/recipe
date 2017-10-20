
infits="/home/user/temp/casa/inputs/zen.2457546.48011.xx.HH.uvcU.fits"
ingc="/home/user/temp/casa/inputs/GC.cl"

invis=importuvfits(infits)

f1=ft(invis, complist=ingc, usescratch=True)

K=gaincal(f1,
          gaintype='K', refant="11")
        
G=gaincal(f1,
          gaintable=[K],
          gaintype='G',
          calmode='ap',
          refant="11")

f2=applycal(f1, gaintable=[K, G])        

f3=split(f2)
