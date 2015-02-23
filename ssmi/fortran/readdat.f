      subroutine readdat(bigsst,t19h,t19v,t22v,t37h,t37v)
C
C*    This incomplete program provides the Fortran code necessary
c     to read the brightness temperature and sea surface temperature
c     files.  The retrieval scheme(s) and format of the output file
c     is left up to the student.
c
      implicit none
      integer*4 nsstlon,nsstlat,nlon,nlat,jlat,jlon,ilat,ilon
      parameter(nsstlon=180,nsstlat=91,nlon=360,nlat=180)
      real*4 sst(nsstlon,nsstlat),T19H(nlon,nlat),T19V(nlon,nlat)
      real*4 T37H(nlon,nlat),T37V(nlon,nlat),T22V(nlon,nlat)
      real*4 bigsst(nlon,nlat)
      character*40 sstfile
      character*40 btfile
      sstfile='sst.jan90'
      btfile='sst.jul90'
      open(10,file=btfile,status='old')
      rewind(10)
      open(11,file=sstfile,status='old')
      rewind(11)
C
c* Read in SST. SSTs in file are in Celcius. This code changes the SSTs
c  to Kelvin.
c
      DO  JLAT=1,nsstlat
         DO  JLON=1,nsstlon
            READ(11,*) SST(JLON,JLAT)
            SST(JLON,JLAT)=SST(JLON,JLAT)+273.15
         end do
      end do
C
C* Read in brightness temperatures.  JLAT,JLON are the coordinates
C  which define a SST grid box to the corresponding brightness
C  temperature grid box.  Therefore, at any (ILON,ILAT) brightness
C  temperature grid box, SST(JLON,JLAT) corresponds to that grid box.
C  

      DO  ILAT=1,180
         DO  ILON=1,360
            READ(10,50) T19H(ilon,ilat),T19V(ilon,ilat),T22V(ilon,ilat),
     1              T37H(ilon,ilat),T37V(ilon,ilat)
 50         FORMAT(5(1X,F6.2))
            JLAT=INT(ILAT/2.+1.)
            JLON=INT(ILON/2.+1.)
c
c  copy the  sst  (which is at 2  degree resolution) to a 
c  1 degree grid, including the missing (land) pixels
c  marked by 999. in the T19H field
c
            IF(JLON.GT.nlon) JLON=1
            if (T19H(ilon,ilat) .gt. 500.) then
               bigsst(ilon,ilat)=999.
            else   
               bigsst(ilon,ilat)=sst(jlon,jlat)
            endif
         end do
      end do 
      return
      END



