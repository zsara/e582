      subroutine epsilon(ifreq,speed,sst,emissh,emissv,nlats,nlons)
C
C*    This incomplete program provides the Fortran code necessary
c     to read the brightness temperature and sea surface temperature
c     files.  The retrieval scheme(s) and format of the output file
c     is left up to the student.
c
      implicit none
      real theta
      parameter(theta=53.1)
      integer nlats,nlons,j,k,ifreq
      real speed(nlats,nlons),sst(nlats,nlons),emissh(nlats,nlons)
      real emissv(nlats,nlons)
      do  j=1,nlats
         do k=1,nlons
            call emiss(ifreq,speed(j,k),sst(j,k),theta,emissh(j,k),
     c         emissv(j,k))
         end do
      end do   
      return
      END


