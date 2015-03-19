from matplotlib import pyplot as plt
plt.switch_backend('Agg') #batch
#plt.switch_backend('MacOSX') #interactive
import numpy as np
import hist2d
reload(hist2d)
from hist2d import hist2d, numba_hist2d
import numpy.random as nr

from matplotlib import cm
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt

import contextlib,time
@contextlib.contextmanager
def timeit():
    t=time.time()
    yield
    print(time.time()-t,"sec")
    

def makeRandom(meanx=None,stdx=None,meany=None,stdy=None,rho=None,
               numpoints=4000):
    """
    return a tuple with two vectors (xvec,yvec) giving the
    coordinates of numpoints chosen from a two dimensional
    Gauassian distribution

    Parameters
    ----------

    meanx: float -- mean in x direction
    stdx:  float -- standard deviation in x direction
    meany: float -- mean in y direction
    stdy:  float -- standar deviation in y direction
    numpoints:  length of returned xvec and yvec


    Returns
    -------

    (xvec, yvec): tuple of ndarray vectors of length numpoints

    Example
    -------

    invalues={'meanx':450.,
              'stdx':50,
              'meany':-180,
              'stdy':40,
              'rho':0.8}

    chanx,chany=makeRandom(**invalues)


    """
 
    nr.seed(50)
    sigma=np.array([stdx**2., rho*stdx*stdy, rho*stdx*stdy, stdy**2.])
    sigma.shape=[2,2]
    meanvec=[meanx,meany]
    outRandom=nr.multivariate_normal(meanvec,sigma,[numpoints,])
    chan1=outRandom[:,0]
    chan2=outRandom[:,1]
    return (chan1,chan2)


if __name__=="__main__":

    #
    # first bullseye centered at (x=450,y= -180)
    #
    invalues={'meanx':450.,
              'stdx':50,
              'meany':-180,
              'stdy':40,
              'rho':0.8}


    chanx,chany=makeRandom(**invalues)

    #
    # second bullseye centered at (x=50,y=-80)
    #
    bullseye={'meanx':50.,
              'stdx':14,
              'meany':-80,
              'stdy':14,
              'rho':0.0}

    chanxB,chanyB=makeRandom(**bullseye)
    chanx=np.concatenate((chanx,chanxB))
    chany=np.concatenate((chany,chanyB))
    x_edges=np.linspace(0,700,70)
    y_edges=np.linspace(-400,0,50)

    print('plain python')
    for i in range(5):
        with timeit():
            hist_array,x_centers,y_centers=hist2d(chanx,chany,x_edges,y_edges)

    print('now numba')
    for i in range(5):
        with timeit():
            hist_array,x_centers,y_centers=numba_hist2d(chanx,chany,x_edges,y_edges)
        
    plt.close('all')
    fig1=plt.figure(1)
    fig1.clf()
    ax=fig1.add_subplot(111)
    ax.plot(chanx,chany,'b.')
    ax.set_title('scatterplot')
    fig1.canvas.draw()
    fig1.savefig('scatter.png')

    cmap=cm.RdBu_r
    cmap.set_over('y')
    cmap.set_under('w')
    vmin= 0.
    vmax= 300.
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    fig2=plt.figure(2)
    fig2.clf()
    ax=fig2.add_subplot(111)
    im=ax.pcolormesh(x_centers,y_centers,hist_array,cmap=cmap,norm=the_norm)
    cb=fig2.colorbar(im,extend='both')
    ax.set_title('2d histogram')
    fig2.canvas.draw()
    fig2.savefig('histogram.png')
    plt.show()
    


