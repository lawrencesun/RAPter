from pylab import *
import argparse
import packages.primitive as primitive
import scipy.signal

parser = argparse.ArgumentParser(description='Generate polar view of the lines directions.')
parser.add_argument('primitivefile')
parser.add_argument('--shownormals', action="store_true", help="Shows the normal distribution and not the angles between the primitives (by default).")
parser.add_argument('--invertnormals', action="store_true", help="Invert normal directions.")
parser.add_argument('--logscale', action="store_true", help="Use log scale.")
parser.add_argument('--useInactivePrims', action="store_true", help="compute the orientation of all the primitives.")

args = parser.parse_args()

primitivefile    = args.primitivefile
shownormals      = args.shownormals
logscale         = args.logscale
invertnormals    = args.invertnormals
useInactivePrims = args.useInactivePrims

print 'Processing ', primitivefile

primitives  = primitive.readPrimitivesFromFile(primitivefile, useInactivePrims)
filename    = primitivefile.split('/')[-1]

import  mpl_toolkits.axisartist.angle_helper as angle_helper
from matplotlib.projections import PolarAxes
from matplotlib.transforms import Affine2D
from  mpl_toolkits.axisartist.grid_helper_curvelinear import GridHelperCurveLinear
from mpl_toolkits.axisartist import Subplot

from mpl_toolkits.axisartist import SubplotHost, \
     ParasiteAxesAuxTrans
     
     
class mFormatterDMS(object):
 
     deg_mark = ""
     min_mark = "^{\prime}"
     sec_mark = "^{\prime\prime}"
 
     fmt_d = "$%d"+deg_mark+"$"
     fmt_ds = r"$%d.\!\!"+deg_mark+"%s$"
 
     # %s for signe
     fmt_d_m = r"$%s%d"+deg_mark+"\,%02d"+min_mark+"$"
     fmt_d_ms = r"$%s%d"+deg_mark+"\,%02d.\mkern-4mu"+min_mark+"%s$"
 
 
     fmt_d_m_partial = "$%s%d"+deg_mark+"\,%02d"+min_mark+"\,"
     fmt_s_partial = "%02d"+sec_mark+"$"
     fmt_ss_partial = "%02d.\!\!"+sec_mark+"%s$"

 
 
     def _get_number_fraction(self, factor):
         ## check for fractional numbers
         number_fraction = None
         # check for 60
 
         for threshold in [1, 60, 3600]:
             if factor <= threshold:
                 break
 
             d = factor // threshold
             int_log_d = int(floor(math.log10(d)))
             if 10**int_log_d == d and d!=1:
                 number_fraction = int_log_d
                 factor = factor // 10**int_log_d
                 return factor, number_fraction
 
         return factor, number_fraction
 
     def __call__(self, direction, factor, values):
         if len(values) == 0:
             return []
         #ss = [[-1, 1][v>0] for v in values] #not py24 compliant
         values = np.asarray(values)
         ss = np.where(values>0, 1, -1)
 
         sign_map = {(-1, True):"-"}
         signs = [sign_map.get((s, v!=0), "") for s, v in zip(ss, values)]
 
         factor, number_fraction = self._get_number_fraction(factor)
 
         values = np.abs(values)
 
         if number_fraction is not None:
             values, frac_part = divmod(values, 10**number_fraction)
             frac_fmt = "%%0%dd" % (number_fraction,)
             frac_str = [frac_fmt % (f1,) for f1 in frac_part]
 
         if factor == 1:
             if number_fraction is None:
                 return [self.fmt_d % (s*int(v),) for (s, v) in zip(ss, values)]
             else:
                 return [self.fmt_ds % (s*int(v), f1) for (s, v, f1) in \
                         zip(ss, values, frac_str)]
         elif factor == 60:
             deg_part, min_part = divmod(values, 60)
             if number_fraction is None:
                 return [self.fmt_d_m % (s1, d1, m1) \
                         for s1, d1, m1 in zip(signs, deg_part, min_part)]
             else:
                 return [self.fmt_d_ms % (s, d1, m1, f1) \
                         for s, d1, m1, f1 in zip(signs, deg_part, min_part, frac_str)]
 
         elif factor == 3600:
             if ss[-1] == -1:
                 inverse_order = True
                 values = values[::-1]
                 sings = signs[::-1]
             else:
                 inverse_order = False
 
             l_hm_old = ""
             r = []
 
             deg_part, min_part_ = divmod(values, 3600)
             min_part, sec_part = divmod(min_part_, 60)
 
             if number_fraction is None:
                 sec_str = [self.fmt_s_partial % (s1,) for s1 in sec_part]
             else:
                 sec_str = [self.fmt_ss_partial % (s1, f1) for s1, f1 in zip(sec_part, frac_str)]
 
             for s, d1, m1, s1 in zip(signs, deg_part, min_part, sec_str):
                 l_hm = self.fmt_d_m_partial % (s, d1, m1)
                 if l_hm != l_hm_old:
                     l_hm_old = l_hm
                     l = l_hm + s1 #l_s
                 else:
                     l = "$"+s1 #l_s
                 r.append(l)
 
             if inverse_order:
                 return r[::-1]
             else:
                 return r
 
         else: # factor > 3600.
             return [r"$%s^{\circ}$" % (str(v),) for v in ss*values]

    

fig = plt.figure(1, figsize=(7, 4))
fig.clf()


N = 360

theta = np.arange(0.0, np.pi, np.pi/N)


radii=np.empty(N)
if logscale:
    radii.fill(sys.float_info.min)
else :
    radii.fill(0.0)

if invertnormals:
    for p1 in primitives:
        p1.normal = -p1.normal
    
angles = np.empty(len(primitives))

if shownormals:
    ref  = np.array([-1.,0.])
    ref2 = np.array([ 1.,0.])
    for idx, p1 in enumerate( primitives ):
        if p1.normal[1] > 0.:
            p1.normal = -p1.normal

        angle = ( math.acos( np.dot(p1.normal[0:2], ref) ) )
        angles[idx] = angle
        
        angle = (angle / (math.pi) * N)
        radii [int(0.5*int(round(angle-0.5)))] += 1

else:
    for p1 in primitives:
        for p2 in primitives:
            angle = math.atan2( np.linalg.norm(np.cross( p1.normal, p2.normal )), 
                                np.dot(p1.normal, p2.normal ))
            angle = (angle / (math.pi) * N)

            radii [int(angle)] += 1

        
if logscale:
    radii = np.log(radii)
    
    
# images are
radiirev = radii[0:N/2][::-1]
radii[1:N/2+1] = radiirev

    
width = (2*np.pi) / N
bottom = max(radii)/2.
    
theta = np.linspace(0.0,360, N, endpoint=False)



"""
polar projection, but in a rectangular box.
"""

# PolarAxes.PolarTransform takes radian. However, we want our coordinate
# system in degree
tr = Affine2D().scale(np.pi/180., 1.) + PolarAxes.PolarTransform()

# polar projection, which involves cycle, and also has limits in
# its coordinates, needs a special method to find the extremes
# (min, max of the coordinate within the view).

# 20, 20 : number of sampling points along x, y direction
extreme_finder = angle_helper.ExtremeFinderCycle(20, 20,
                                                 lon_cycle = 360,
                                                 lat_cycle = None,
                                                 lon_minmax = None,
                                                 lat_minmax = (0, np.inf),
                                                 )

grid_locator1 = angle_helper.LocatorDMS(3)
# Find a grid values appropriate for the coordinate (degree,
# minute, second).
deg_mark = "^{\circ}"
min_mark = "^{\prime}"
sec_mark = "^{\prime\prime}"
tick_formatter1 = mFormatterDMS()
# And also uses an appropriate formatter.  Note that,the
# acceptable Locator and Formatter class is a bit different than
# that of mpl's, and you cannot directly use mpl's Locator and
# Formatter here (but may be possible in the future).

grid_helper = GridHelperCurveLinear(tr,
                                    extreme_finder=extreme_finder,
                                    grid_locator1=grid_locator1,
                                    tick_formatter1=tick_formatter1
                                    )


#ax1 = axes([0.025,0.025,0.95,0.95], grid_helper=grid_helper)
ax1 = SubplotHost(fig, 1, 1, 1, grid_helper=grid_helper)

# make ticklabels of right and top axis visible.
ax1.axis["right"].major_ticklabels.set_visible(True)
ax1.axis["top"].major_ticklabels.set_visible(True)

# let right axis shows ticklabels for 1st coordinate (angle)
ax1.axis["right"].get_helper().nth_coord_ticks=0
ax1.axis["left"].get_helper().nth_coord_ticks=0
# let bottom axis shows ticklabels for 2nd coordinate (radius)
ax1.axis["bottom"].get_helper().nth_coord_ticks=1
ax1.axis["bottom"].major_ticklabels.set_visible(False)

#ax1.tick_params(direction='out', length=6, width=2, colors='r')



fig.add_subplot(ax1)

limitvalue=bottom+np.max(radii)+1

# A parasite axes with given transform
ax2 = ParasiteAxesAuxTrans(ax1, tr, "equal")
# note that ax2.transData == tr + ax1.transData
# Anthing you draw in ax2 will match the ticks and grids of ax1.
ax1.parasites.append(ax2)
intp = cbook.simple_linear_interpolation

ax2.bar(theta[0:N/2], radii[0:N/2], width=width, bottom=bottom, linewidth=2)


ax1.set_aspect(1.)
ax1.set_xlim(limitvalue, -limitvalue)
ax1.set_ylim(0, limitvalue)

ax1.grid(color='0.75', linestyle='-', linewidth=0.5, zorder=-1)


savefig(primitivefile[:-4]+'.svg', format="svg")

