#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:50:26 2026

@author: carolingold

- inspired and based on legacy code by Bjarke S. Jessen and M. Kapfer
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# %matplotlib qt    # ADD BACK LATER 
from scipy.optimize import curve_fit

#import own library
import os
import pathlib
import sys
libpath=os.path.join(pathlib.Path(__file__).parents[3], '00-Library/') 
print(libpath)
sys.path.insert(1,libpath)
import Asylum_LoadData_v3 as LD
import Asylum_plotData_v2 as PD


def parabola(x, a, b, c):
    return a*x**2 + b*x + c

def line(x, m, q):
    return m*x + q

# Load specific coordinate file
coord_file = "results/coords_Image0005_155649.txt" # Change to your latest file
coord_data = np.loadtxt(coord_file)
X, Y = coord_data[:, 0], coord_data[:, 1]

#load data
filename_bend='../../Data/Image0005.ibw'
Stack = 'Trevor_WSe2_tgr3'
data_bent=LD.JupiterAFM_loadData_toDict(filename_bend, Stack)
# print(data_unbent)
data_labels=data_bent['labels']
print('data_labels=',data_labels)

#
fig = plt.figure()
ax = fig.add_subplot(111)

PD.JupiterAFM_plotData_imshow(data_bent, data_labels[1],ax=ax,cmap_corr=0.7,cmap='gray')#,snap=True)#, axis, title=True,**plotargs)

ax.scatter(X,Y,s=0.1, color='r')
plt.show()

# (4D) Curve fitting with Uncertainty
# Parabolic Fit
p_opt, p_cov = curve_fit(parabola, X, Y)
# p_cov is the covariance matrix. Sqrt of diagonal = standard deviation.
perr = np.sqrt(np.diag(p_cov)) 

# Linear Fit (using mask Y > 25)
mask = X < 10
l_opt, l_cov = curve_fit(line, X[mask], Y[mask])
lerr = np.sqrt(np.diag(l_cov))

# Calculate d and propagate error
x_max = np.max(X)
val_line = line(x_max, *l_opt)
val_para = parabola(x_max, *p_opt)
d = val_line - val_para

print(f"Fit Results:")
print(f"Parabola a: {p_opt[0]:.4e} ± {perr[0]:.4e}")
print(f"Displacement d: {d:.4f} um")


# Visualization
x_grid = np.linspace(X.min(), X.max(), 100)
plt.figure(figsize=(8, 5))
plt.scatter(X, Y, color='black', label='Data')
plt.scatter(X[mask],Y[mask],color='tab:blue')
plt.plot(x_grid, parabola(x_grid, *p_opt), '-', color='orange', label='Parabolic Fit')
plt.plot(x_grid, line(x_grid, *l_opt), '--', color='crimson',label='Linear Reference')
plt.legend()
plt.xlabel("X (um)")
plt.ylabel("Y (um)")
plt.show()



plt.figure(figsize=(8, 5))
plt.scatter(X, np.abs(Y-line(X, *l_opt)), color='black')#, label='Snapped Data')
#plt.plot(x_grid, parabola(x_grid, *p_opt), '-', color='orange', label='Parabolic Fit')
#plt.plot(x_grid, line(x_grid, *l_opt), '--', color='crimson',label='Linear Reference')
#plt.legend()
plt.title('|Data - linear reference|')
plt.xlabel("X (um)")
plt.ylabel("d (um)")
plt.show()

'''
#fit linear fit to deflection plot
deflection=np.abs(Y-line(X, *l_opt))
# Linear Fit (using mask Y > 25)
dmask = X > 22
l_opt_d, l_cov_d = curve_fit(line, X[dmask], deflection[dmask])
lerr_d = np.sqrt(np.diag(l_cov_d))
print(f'slope: {l_cov_d[0][0]}')
print(f'arctan: {np.arctan(l_cov_d[0]*1e6)*180./np.pi}')

plt.figure(figsize=(8, 5))
plt.scatter(X, deflection, color='black')#, label='Snapped Data')
plt.scatter(X[dmask],deflection[dmask],color='tab:blue')
plt.plot(x_grid, line(x_grid, *l_opt_d), '--', color='crimson',label='Linear Reference')
#plt.plot(x_grid, line(x_grid, *l_opt), '--', color='crimson',label='Linear Reference')
#plt.legend()
plt.title('|Data - linear reference|')
plt.xlabel("X (um)")
plt.ylabel("d (um)")
plt.show()
'''

# Combine into 1 figure

fig, ax= plt.subplots(1,3, figsize=(18,9))

#Ax 1: Raw data (AFM()
PD.JupiterAFM_plotData_imshow(data_bent, data_labels[1],ax=ax[0],cmap_corr=0.7,cmap='gray')#,snap=True)#, axis, title=True,**plotargs)
ax[0].scatter(X,Y,s=0.1, color='r')
ax[0].axis('off')

#Ax2: Edge data & fits
ax[1].scatter(X, Y, color='black', label='Data')
ax[1].scatter(X[mask],Y[mask],color='tab:blue')
ax[1].plot(x_grid, parabola(x_grid, *p_opt), '-', color='orange', label='Parabolic Fit')
ax[1].plot(x_grid, line(x_grid, *l_opt), '--', color='crimson',label='Linear Reference')
ax[1].legend()
ax[1].set_xlabel("X (um)")
ax[1].set_ylabel("Y (um)")
ax[1].set_title('Data along edge')

#ax3: displacement
ax[2].scatter(X, np.abs(Y-line(X, *l_opt)), color='black')#, label='Snapped Data')
ax[2].set_title('|Data - linear reference|')
ax[2].set_xlabel("X (um)")
ax[2].set_ylabel("d (um)")
plt.savefig(f"Image05_lowerEdge.png")
plt.tight_layout()
