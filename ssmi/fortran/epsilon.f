C     The gateway routine
c     $Id: epsilon.f,v 1.2 2002/10/03 19:57:14 phil Exp $
      subroutine mexFunction(nlhs, plhs, nrhs, prhs)
      implicit none
      character*100 rcsid
      data rcsid
     1 /"$Id: epsilon.f,v 1.2 2002/10/03 19:57:14 phil Exp $"/
      integer nlons,nlats,size
      parameter(nlons=360,nlats=180)
c
c  original sounding pressure, temperature, h2o mixing ratio, column integrated ozone
c
      real speed(nlats,nlons),sst(nlats,nlons),emissh(nlats,nlons)
      real emissv(nlats,nlons)
      real*8 hold8(nlats,nlons)
      integer m,n,ifreq

c
c     number of sounding levels
      integer nlhs, nrhs
      integer plhs(*), prhs(*)
      integer mxGetPr, mxCreateFull,mxGetM,mxGetN
C--------------------------------------------------------------
C     
      integer hold_pr
      character*100 msg
C     Check for proper number of arguments.
      msg=
     1 'usage: [emissv,emissh]=epsget(ifreq,speed,sst)'
      if (nrhs .ne. 3) then
         call mexErrMsgTxt(msg)
      elseif (nlhs .ne. 2) then
         call mexErrMsgTxt(msg)
      endif
      m=mxGetM(prhs(1))
      n=mxGetN(prhs(1))   
      if (m*n .ne. 1) then
         call mexErrMsgTxt
     1        ('expecting single number for ifreq')
      endif   
      hold_pr=mxGetPr(prhs(1))
      call mxCopyPtrToReal8(hold_pr, hold8(1,1), 1)
      ifreq=int(hold8(1,1))
      m=mxGetM(prhs(2))
      n=mxGetN(prhs(2))   
      size=m*n
      if (size .ne. nlats*nlons) then
         call mexErrMsgTxt
     1        ('expecting nlats,nlons for speed')
      endif   
      hold_pr=mxGetPr(prhs(2))
      call mxCopyPtrToReal8(hold_pr, hold8, size)
      call transfer84(hold8,speed,m,n)
      m=mxGetM(prhs(3))
      n=mxGetN(prhs(3))   
      if (m*n .ne. nlats*nlons) then
         call mexErrMsgTxt
     1        ('expecting nlats,nlons for sst')
      endif   
      hold_pr=mxGetPr(prhs(3))
      call mxCopyPtrToReal8(hold_pr, hold8, size)
      call transfer84(hold8,sst,m,n)
      call epsget(ifreq,speed,sst,emissh,emissv,m,n)
      plhs(1) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(1))
      call transfer48(emissv,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      plhs(2) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(2))
      call transfer48(emissh,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      return
      end

      subroutine epsget(ifreq,speed,sst,emissh,emissv,nlats,nlons)
C
C     This incomplete program provides the Fortran code necessary
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
c            emissh(j,k)=speed(j,k)
c            emissv(j,k)=sst(j,k)
            call emiss(ifreq,speed(j,k),sst(j,k),theta,emissh(j,k),
     c         emissv(j,k))
         end do
      end do   
      return
      END


      subroutine transfer84(var8,var4,m,n)
      implicit none
      integer j,k,m,n
      real*8 var8(m,n)
      real*4 var4(m,n)
      do k=1,n
         do j=1,m
           var4(j,k)=var8(j,k)
         end do
      end do
      return
      end


      subroutine transfer48(var4,var8,m,n)
      implicit none
      integer j,k,m,n
      real*8 var8(m,n)
      real*4 var4(m,n)
      do k=1,n
         do j=1,m
           var8(j,k)=var4(j,k)
         end do
      end do
      return
      end


