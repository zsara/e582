      SUBROUTINE COEF(SST,KL19,KL37,KV19,KV37,TOX19,TOX37)
C     $Id: coef.f,v 1.2 2002/10/03 19:56:26 phil Exp $
C*    This subroutine calculates the absorption coefficients and
c     the oxygen transmission at 19 and 37 GHz given the SST and
c     parameterizing the effective cloud emission temperature.
c
c     INPUT:
C                SST   -  Sea surface temperature in Kelvin (for a
c                         particular grid box)
c     OUTPUT:
C                KL19  -  Liquid water absorption coefficient at 19 GHz
c                KL37  -  Liquid water absorption coefficient at 37 GHz
c                KV19  -  Water vapor absorption coefficient at 19 GHz
c                KV37  -  Water vapor absorption coefficient at 37 GHz
C                TOX19 -  Oxygen transmission at 19 GHz
C                TOX37 -  Oxygen transmission at 37 GHz
c
      implicit none
      REAL*4 SST,KL19,KL37,KV19,KV37,TOX19,TOX37
      real*4 TC,TCEL,TSCEL
C
C  Set effective cloud emission temp
      TC = SST - 6.
C  Compute liquid water mass absorption coefficients (m**2/kg)
C  From Petty Ph.D. dissertation, 1990
      TCEL = TC - 273.15
c
      KL19 = 0.0786 - 0.230E-2*TCEL + 0.448E-4*TCEL**2 -
     $         0.464E-6*TCEL**3
      KL37 = 0.267 - 0.673E-2*TCEL + 0.975E-4*TCEL**2 -
     $         0.724E-6*TCEL**3
c
      TSCEL = SST - 273.15
c
      TOX19 = 0.9779 -6.314E-5 * TSCEL + 7.746E-6 * TSCEL**2 -
     $      1.003E-7 * TSCEL ** 3
      TOX37 = 0.9269 -8.525E-5 * TSCEL + 1.807E-5 * TSCEL**2 -
     $      2.008E-7 * TSCEL ** 3
      KV19 = 2.58E-3 * (300./SST)**0.477
      KV37 = 2.12E-3

      RETURN
      END
