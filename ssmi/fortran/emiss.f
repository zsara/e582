*-------------------------------------------------------------------------
* $Id: emiss.f,v 1.4 2002/10/03 22:27:00 phil Exp $
*  Reference:
*
*       Petty, 1990: "On the Response of the Special Sensor Microwave/Imager
*         to the Marine Environment - Implications for Atmospheric Parameter
*         Retrievals"  Ph.D. Dissertation, University of Washington, 291 pp.
*      (Journal articles pending)
*
*   coded in a quick-and-dirty fashion, and without any warranty, by:
*   Grant W. Petty
*   Earth and Atmospheric Sciences Dept.
*   Purdue University
*   West Lafayette, IN  47907
*   USA
*
*   Tel. No. (317) 494-2544
*   Internet address : gpetty@rain.atms.purdue.edu
*
*----------------------------------------------------------------------
      subroutine emiss(ifreq,speed,sst,theta,emissh,emissv)
*
*   INPUT:
*
*   ifreq = 1 (19.35)        speed = wind speed (m/s)
*           2 (22.235)       sst   = sea surface temperature in kelvin
*           3 (37.0)         theta = view angle of satellite in degrees
*           4 (85.5)
*
*   OUTPUT:
*
*           emissh = horizontally polarized emissivity
*           emissv = vertically polarized emissivity
*  
      implicit none
      real*4 ebiasv(4),ebiash(4),cf(4),cg(4),emissv,emissh
      real*4 theta,sst,speed,fem,foam,gx2,remv,remh
      integer ifreq
      data cf /0.008,0.008,0.008,0.008/
      data cg /3.49e-3, 3.60e-3, 4.85e-3, 6.22e-3 /
* empirical bias corrections for surface emissivity
c      data ebiasv /0.00400,-0.00451,-0.0124,-0.00189/
c      data ebiash /0.00354,     0.0,-0.0125, 0.05415/
      data ebiasv /0.00,0.00,0.0,0.00/
      data ebiash /0.00,0.00,0.0,0.00/
* 'foam' emissivity
      data fem /1.0/
c
c* SST adjustment (not part of Petty's original code)
c
      if(sst .lt. 271.25) then
         sst = 271.25
      endif

* effective surface slope variance
      gx2 = cg(ifreq)*speed

* get rough surface emissivity

      call roughem(ifreq,gx2,sst,theta,remv,remh)
c      remv=1.
c      remh=1.

* compute 'foam' coverage

      if (speed .gt. 7.0) then
        foam = cf(ifreq)*(speed-7.0)
      else
        foam = 0.0
      endif

* compute surface emissivities and reflectivity

      emissv = foam*fem + (1.0 - foam)*(remv + ebiasv(ifreq))
      emissh = foam*fem + (1.0 - foam)*(remh + ebiash(ifreq))

      return
      end

*================================================================
      subroutine roughem(ifreq,gx2,tk,theta,remv,remh)
      implicit none
*
* Calculates rough-surface emissivity of ocean surface at SSM/I
* frequencies.
*
      real a19v(4),a22v(4),a37v(4),a85v(4)
      real a19h(4),a22h(4),a37h(4),a85h(4)
      real f(4),tp,tk,dtheta,theta,g,x1,x2,x3,x4,remv,remh
      real gx2,semv,semh,ev,eh
      integer ifreq
*
      data a19v/  -0.111E+01,   0.713E+00,  -0.624E-01,   0.212E-01 /
      data a19h/   0.812E+00,  -0.215E+00,   0.255E-01,   0.305E-02 /
      data a22v/  -0.134E+01,   0.911E+00,  -0.893E-01,   0.463E-01 /
      data a22h/   0.958E+00,  -0.350E+00,   0.566E-01,  -0.262E-01 /
      data a37v/  -0.162E+01,   0.110E+01,  -0.730E-01,   0.298E-01 /
      data a37h/   0.947E+00,  -0.320E+00,   0.624E-01,  -0.300E-01 /
      data a85v/  -0.145E+01,   0.808E+00,  -0.147E-01,  -0.252E-01 /
      data a85h/   0.717E+00,  -0.702E-01,   0.617E-01,  -0.243E-01 /
*
      data f/ 19.35, 22.235, 37.0, 85.5 /
*
      tp = tk/273.0
      dtheta = theta-53.0
      g =  0.5*gx2
      x1 = g
      x2 = tp*g
      x3 = dtheta*g
      x4 = tp*x3
*
      if (ifreq .eq. 1) then
         remv = x1*a19v(1) + x2*a19v(2) + x3*a19v(3) + x4*a19v(4)
         remh = x1*a19h(1) + x2*a19h(2) + x3*a19h(3) + x4*a19h(4)
      else if (ifreq .eq. 2) then
         remv = x1*a22v(1) + x2*a22v(2) + x3*a22v(3) + x4*a22v(4)
         remh = x1*a22h(1) + x2*a22h(2) + x3*a22h(3) + x4*a22h(4)
      else if (ifreq .eq. 3) then
         remv = x1*a37v(1) + x2*a37v(2) + x3*a37v(3) + x4*a37v(4)
         remh = x1*a37h(1) + x2*a37h(2) + x3*a37h(3) + x4*a37h(4)
      else if (ifreq .eq. 4) then
         remv = x1*a85v(1) + x2*a85v(2) + x3*a85v(3) + x4*a85v(4)
         remh = x1*a85h(1) + x2*a85h(2) + x3*a85h(3) + x4*a85h(4)
      endif
      call spemiss(f(ifreq),tk,theta,36.5,semv,semh)
      remv = remv + semv
      remh = remh + semh
      return
      end
      
********************
*
      subroutine epsalt(f,t,ssw,epsr,epsi)
*     returns the complex dielectric constant of sea water, using the
*     model of Klein and Swift (1977)
*
*     Input   f = frequency (GHz)
*             t = temperature (C)
*             ssw = salinity (permil) (if ssw < 0, ssw = 32.54)
*     Output  epsr,epsi  = real and imaginary parts of dielectric constant
*
      implicit none
      real*4 f,t,epsr,epsi,pi,ssw,ssw2,ssw3,t2,t3,es,a,tau
      real*4 delt,delt2,beta,om,b,sig,epsrhold,epsihold
      complex cdum1,cdum2,cdum3,cmplx
      parameter (pi = 3.14159265)
*
      if (ssw .lt. 0.0) ssw = 32.54
      ssw2 = ssw*ssw
      ssw3 = ssw2*ssw
      t2 = t*t
      t3 = t2*t
      es = 87.134 - 1.949e-1*t - 1.276e-2*t2 + 2.491e-4*t3
      a = 1.0 + 1.613e-5*ssw*t - 3.656e-3*ssw + 3.21e-5*ssw2 -
     &   4.232e-7*ssw3
      es = es*a
*
      tau = 1.768e-11 - 6.086e-13*t + 1.104e-14*t2 - 8.111e-17*t3
      b = 1.0 + 2.282e-5*ssw*t - 7.638e-4*ssw - 7.760e-6*ssw2 +
     &   1.105e-8*ssw3
      tau = tau*b
*
      sig = ssw*(0.182521 - 1.46192e-3*ssw + 2.09324e-5*ssw2 -
     &   1.28205e-7*ssw3)
      delt = 25.0 - t
      delt2 = delt*delt
      beta = 2.033e-2 + 1.266e-4*delt + 2.464e-6*delt2 -
     &   ssw*(1.849e-5 - 2.551e-7*delt + 2.551e-8*delt2)
      sig = sig*exp(-beta*delt)
*
      om = 2.0e9*pi*f
      cdum1 = cmplx(0.0,om*tau)
      cdum2 = cmplx(0.0,sig/(om*8.854e-12))
      cdum3 = 4.9 + (es-4.9)/(1.0 + cdum1) - cdum2
      epsrhold = real(cdum3)
      epsihold = -aimag(cdum3)
      epsi=0.5
      epsr=0.5
      if (epsrhold .gt. 1.) then
         epsr=epsrhold
      endif
      if (epsihold .gt. 1.) then
         epsi=epsihold
      endif
      print *,"in epsalt III",epsr," test ",epsi
c$$$      epsi=1.
c$$$      epsr=1.
      return
      end
*
**************************************
      subroutine spemiss(f,tk,theta,ssw,ev,eh)
*     returns the specular emissivity of sea water for given freq. (GHz), 
*     temperature T (K), incidence angle theta (degrees), salinity (permil)
*     
*     Returned values verified against data in Klein and Swift (1977) and
*     against Table 3.8 in Olson (1987, Ph.D. Thesis)
*
      implicit none
      real*4 f,tk,theta,ssw,ev,eh
      real*4 fold,tkold,sswold,epsr,epsi,epsrold,epsiold
      save fold,tkold,sswold,epsrold,epsiold
*
      real*4 tc,costh,sinth,rthet
      complex*8 etav,etah,eps,cterm1v,cterm1h,cterm2,cterm3v,cterm3h
*
      if (f.ne.fold.or.tk.ne.tkold.or.ssw.ne.sswold) then
        tc = tk - 273.15
        fold = f
        tkold = tk
        sswold = ssw
        call epsalt(f,tc,ssw,epsr,epsi)
        epsrold = epsr
        epsiold = epsi
      else
        epsr = epsrold
        epsi = epsiold
      endif
      eps = cmplx(epsr,epsi)
      etav = eps
      etah = (1.0,0.0)
      rthet = theta*0.017453292
      costh = cos(rthet)
      sinth = sin(rthet)
      sinth = sinth*sinth
      cterm1v = etav*costh
      cterm1h = etah*costh
      eps = eps - sinth
      cterm2 = csqrt(eps)
      cterm3v = (cterm1v - cterm2)/(cterm1v + cterm2)
      cterm3h = (cterm1h - cterm2)/(cterm1h + cterm2)
      ev = 1.0 - cabs(cterm3v)**2
      eh = 1.0 - cabs(cterm3h)**2
      return
      end
