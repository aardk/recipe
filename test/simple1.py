GCCleanMask='ellipse[[17h45m00.0s,-29d00m00.00s ], [ 11deg, 4deg ] , 30deg]'
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

f1= fixvis(f1, phasecenter="J2000 17h45m40s -29d00m28s")

K=gaincal(f1,
          gaintype='K', refant="11")
        
G=gaincal(f1,
          gaintable=[K],
          gaintype='G',
          calmode='ap',
          refant="11")

f2=applycal(f1, gaintable=[K, G])        

f3=split(f2)

oo=clean(vis=f3,
         niter=500,
         weighting='briggs',
         robust=0,
         imsize=[1024,1024],
         cell=['250arcsec'],
         mode='mfs',
         nterms=1,
         spw='0:150~900',
         reffreq='120MHz',
         #spw='0:150~700',
         mask=GCCleanMask)
