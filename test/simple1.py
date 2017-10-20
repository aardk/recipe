
infits="/home/user/temp/casa/inputs/zen.2457546.48011.xx.HH.uvcU.fits"
ingc="/home/user/temp/casa/inputs/GC.cl"

invis=importuvfits(infits)

f1=ft(invis, complist=ingc, usescratch=True)

f1= flagdata(f1, flagbackup=True,        mode='manual', antenna="82")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:0~65")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:377~387")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:850~854")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:930~1024")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:831")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:769")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:511")
f1= flagdata(f1, flagbackup=True,        mode='manual', spw="0:913")                
f1= flagdata(f1, autocorr=True)

K=gaincal(f1,
          gaintype='K', refant="11")
        
G=gaincal(f1,
          gaintable=[K],
          gaintype='G',
          calmode='ap',
          refant="11")

f2=applycal(f1, gaintable=[K, G])        

f3=split(f2)
