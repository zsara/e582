"""
   python translation of the perl script at
   http://oceancolor.gsfc.nasa.gov/cms/L3Bins.html
"""


# The following functions are based on the pseudocode found in Appendix A of:
# 
# Campbell, J.W., J.M. Blaisdell, and M. Darzi, 1995:
# Level-3 SeaWiFS Data Products: Spatial and Temporal Binning Algorithms.
# NASA Tech. Memo. 104566, Vol. 32,
# S.B. Hooker, E.R. Firestone, and J.G. Acker, Eds.,
# NASA Goddard Space Flight Center, Greenbelt, Maryland

from __future__ import division
import numpy as np 

class bin_calc(object):

    def __init__(self,numrows):
        self.numrows=numrows
        basebin=[1]
        numbin=[]
        latbin=[]
        for row in range(numrows):
            latbin.append(((row + 0.5)*180.0/self.numrows) - 90.0)
            numbin.append(int(2*self.numrows*np.cos(latbin[row]*np.pi/180.0) + 0.5))
            if row > 0:
                basebin.append(basebin[row-1] + numbin[row-1])
        self.basebin=np.array(basebin)
        self.numbin=np.array(numbin)
        self.latbin=np.array(latbin)
        self.totbins = basebin[numrows - 1] + numbin[numrows - 1] - 1

    def lat2row(self,lat):
        row=int((90. + lat)*self.numrows/180.)
        if row > self.numrows:
            row = self.numrows - 1
        return row

    def rowlon2bin(self,row,lon):
        lon = self.constrain_lon(lon)
        col = int((lon + 180.0)*self.numbin[row]/360.0)
        if col >= numbin[row]:
            col = numbin[row] - 1
        return self.basebin[row] + col

    def latlon2bin(self,lat,lon):
        lat = self.constrain_lat(lat)
        lon = self.constrain_lon(lon)
        row = self.lat2row(lat)
        col = int((lon + 180.0)*self.numbin[row]/360.0)
        if col >= self.numbin[row]:
            col = self.numbin[row] - 1

        return self.basebin[row] + col

    def bin2latlon(self,bin):
        row = self.numrows - 1
        if bin < 1:
            bin = 1
        while bin < self.basebin[row]:
            row-=1
        clat = self.latbin[row]
        clon = 360.0*(bin - self.basebin[row] + 0.5)/self.numbin[row] - 180.0
        return clat,clon

    def bin2bounds(self,bin):
        row=self.numrows -1
        if bin < 1:
          bin=1
        while bin < self.basebin[row]:
            row-=1
        north = self.latbin[row] + (90.0/self.numrows)
        south = self.latbin[row] - (90.0/self.numrows)
        lon = 360.0*(bin - self.basebin[row] + 0.5)/self.numbin[row] - 180.0
        west = lon - 180.0/self.numbin[row]
        east = lon + 180.0/self.numbin[row]
        return north,south,west,east

    def constrain_lat(self,lat):
        if lat > 90.:
            lat = 90
        if lat < -90.:
            lat = -90
        return lat

    def constrain_lon(self,lon):
        if lon < -180:
          lon += 360
        if lon > 180:
          lon -= 360
        return lon

if __name__ == "__main__":
    
    test18=bin_calc(18)
    print(test18.bin2bounds(367))
    print(test18.bin2bounds(411))
    print(test18.bin2bounds(412))
    print(test18.bin2latlon(367))
    print(test18.latlon2bin(49.2333,-123.25))
    
          
