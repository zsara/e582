C     The gateway routine
c     $Id: kappa.f,v 1.2 2002/10/03 19:57:34 phil Exp $
      subroutine mexFunction(nlhs, plhs, nrhs, prhs)
      implicit none
      character*100 rcsid
      data rcsid
     1 /"$Id: kappa.f,v 1.2 2002/10/03 19:57:34 phil Exp $"/
      integer nlons,nlats,size
      parameter(nlons=360,nlats=180)
c
c  original sounding pressure, temperature, h2o mixing ratio, column integrated ozone
c
      real sst(nlats,nlons),kl19(nlats,nlons),kl37(nlats,nlons)
      real kv19(nlats,nlons),kv37(nlats,nlons),tox19(nlats,nlons)
      real tox37(nlats,nlons)
      real*8 hold8(nlats,nlons)
      integer m,n,mxGetM,mxGetN,j,k

c
c     number of sounding levels
      integer nlhs, nrhs
      integer plhs(*), prhs(*)
      integer mxGetPr, mxCreateFull
C--------------------------------------------------------------
C     
      integer hold_pr
      character*100 msg
C     Check for proper number of arguments.
      msg=
     1 'usage: [kl19,kl37,kv19,kv37,tox19,tox37]=kappa(sst)'
      if (nrhs .ne. 1) then
         call mexErrMsgTxt(msg)
      elseif (nlhs .ne. 6) then
         call mexErrMsgTxt(msg)
      endif
      m=mxGetM(prhs(1))
      n=mxGetN(prhs(1))   
      size=m*n
      if (size .ne. nlats*nlons) then
         call mexErrMsgTxt
     1        ('expecting nlats,nlons for sst')
      endif   
      hold_pr=mxGetPr(prhs(1))
      call mxCopyPtrToReal8(hold_pr, hold8, size)
      call transfer84(hold8,sst,m,n)
      call kappa(sst,kl19,kl37,kv19,kv37,tox19,tox37)
      size=nlons*nlats
      plhs(1) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(1))
      call transfer48(kl19,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      plhs(2) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(2))
      call transfer48(kl37,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      plhs(3) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(3))
      call transfer48(kv19,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      plhs(4) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(4))
      call transfer48(kv37,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      plhs(5) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(5))
      call transfer48(tox19,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      plhs(6) = mxCreateFull(m, n, 0)
      hold_pr=mxGetPr(plhs(6))
      call transfer48(tox37,hold8,m,n)
      call mxCopyReal8ToPtr(hold8, hold_pr, size)
      return
      end

      subroutine kappa(sst,kl19,kl37,kv19,kv37,tox19,tox37)
      implicit none
      integer nlats,nlons,j,k
      parameter(nlats=180,nlons=360)
      real sst(nlats,nlons),kl19(nlats,nlons)
      real kl37(nlats,nlons)
      real kv19(nlats,nlons),kv37(nlats,nlons)
      real tox37(nlats,nlons),tox19(nlats,nlons)
      do  j=1,nlats
         do k=1,nlons
            call coef(sst(j,k),kl19(j,k),kl37(j,k),
     c            kv19(j,k),kv37(j,k),tox19(j,k),tox37(j,k))
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


