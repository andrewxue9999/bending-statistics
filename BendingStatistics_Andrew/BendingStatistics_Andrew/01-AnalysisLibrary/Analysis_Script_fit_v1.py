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
%matplotlib qt
from scipy.optimize import curve_fit
from functools import partial

# ---- import own library ------------------------------------------------------
import os
import pathlib
import sys
libpath=os.path.join(pathlib.Path(__file__).parents[3], '00-Library/') 
print(libpath)
sys.path.insert(1,libpath)
import Asylum_LoadData_v0 as LD
import Asylum_plotData_v2 as PD

# ==============================================================================
# Define Functions
# ==============================================================================

def parabola(x, a, b, c):
    return a*x**2 + b*x + c

def line(x, m, q):
    return m*x + q

def deflection_bent_ribbon(x,d0,L):
    return d0/(L**3)*(x-L)**3

def derivative_deflection_bent_ribbon(x,d0,L):
    return d0/(L**3)*3*(x-L)**2

# ==============================================================================
# Load Data Files
# ==============================================================================
# ---- Load specific coordinate file -------------------------------------------
coord_file = "results/coords_Image0005_155649.txt" # Change to your latest file
coord_data = np.loadtxt(coord_file)
Xt, Yt = coord_data[:, 0], coord_data[:, 1]
X=Xt-Xt.min()
Y=Yt-Yt.min()

# ---- load data ------------------------------------------------------
filename_bend='../../Data/Image0005.ibw'
Stack = 'Trevor_WSe2_tgr3'
data_bent=LD.JupiterAFM_loadData_toDict(filename_bend, Stack)
# print(data_unbent)
data_labels=data_bent['labels']
print('data_labels=',data_labels)

# ==============================================================================
# Work with Data
# ==============================================================================

# ---- plot data & coordinates -------------------------------------------------
fig = plt.figure()
ax = fig.add_subplot(111)
PD.JupiterAFM_plotData_imshow(data_bent, data_labels[1],ax=ax,cmap_corr=0.7,cmap='gray')#,snap=True)#, axis, title=True,**plotargs)
ax.scatter(Xt,Yt,s=0.1, color='r')
plt.show()

# ---- fit cooordinates  ------------------------------------------------------
# (4D) Curve fitting with Uncertainty
# Parabolic Fit
p_opt, p_cov = curve_fit(parabola, X, Y)
# p_cov is the covariance matrix. Sqrt of diagonal = standard deviation.
perr = np.sqrt(np.diag(p_cov)) 

print(f"Fit Results:")
#print(f'p_cov={p_cov}')
print(f"Parabola a: {p_opt[0]:.4e} ± {perr[0]:.4e}")

# Linear Fit (using mask Y > 25)
mask = X < 10
l_opt, l_cov = curve_fit(line, X[mask], Y[mask])
lerr = np.sqrt(np.diag(l_cov))

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


'''
# Calculate d and propagate error
x_max = np.max(X)
val_line = line(x_max, *l_opt)
val_para = parabola(x_max, *p_opt)
d = val_line - val_para
print(f"Displacement d: {d:.4f} um")
'''

# ---- deflection  ------------------------------------------------------
deflection_data=Y-line(X, *l_opt)

np.savetxt(f"results/displacement.txt", np.column_stack([X, deflection_data]),
               header="X D", comments="", fmt="%.10f")

# Fit
#deflection_bent = deflection_bent_ribbon # partial(deflection_bent_ribbon, L=31.2)
mask_d= X >10
d_opt,d_cov=curve_fit(deflection_bent_ribbon, X[mask_d],deflection_data[mask_d])
derr=np.sqrt(np.diag(p_cov)) 
print(f"Fit Results displacement: d(x)=d0*(x/L-1)^3")
print(f'dopt={d_opt}')
print(f" d0: {d_opt[0]:.4e} ± {derr[0]:.4e}")
print(f'L: {d_opt[1]:.4e} ± {derr[1]:.4e}')

# After your curve_fit, build a text string with your parameters
textstr = '\n'.join([f'$d(x)=d_0(x/L-1)^3$',
    f'$d_0$ = {d_opt[0]:.2e} ± {derr[0]:.2e}',
    f'$L$  = {d_opt[1]:.2e} ± {derr[1]:.2e}',
])



fig, ax=plt.subplots(figsize=(8, 5))
plt.scatter(X,deflection_data , color='black')#, label='Snapped Data')
plt.scatter(X[mask_d],deflection_data[mask_d] , color='tab:blue')#, label='Snapped Data')
#plt.plot(x_grid, parabola(x_grid, *p_opt), '-', color='orange', label='Parabolic Fit')
#plt.plot(x_grid, line(x_grid, *l_opt), '--', color='crimson',label='Linear Reference')
plt.plot(x_grid,deflection_bent_ribbon(x_grid,*d_opt))
# Add a text box to the plot
props = dict(boxstyle='round', facecolor='gray', alpha=0.2)
ax.text(0.05, 0.95, textstr,
        transform=ax.transAxes,   # coordinates relative to axes (0-1)
        fontsize=10,
        verticalalignment='top',
        bbox=props)

plt.legend()
plt.title('|Data - linear reference|')
plt.xlabel("X (um)")
plt.ylabel("d (um)")
plt.show()

# ---- local twist angle  ------------------------------------------------------
mask_twist= X>10#(X.max()-d_opt[1]) #maximum X-coord minus bend length L


d_deriv=derivative_deflection_bent_ribbon(X[mask_twist],*d_opt)
theta=np.arctan(np.abs(d_deriv))*180/np.pi

fig, ax=plt.subplots(figsize=(8, 5))
plt.scatter(X[mask_twist],theta , color='black')#, label='Snapped Data')

plt.legend()
plt.title('local twist-angle')
plt.xlabel("X (um)")
plt.ylabel(f"$ \\Delta \\theta$  (degree)")
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

fig, ax= plt.subplots(1,4, figsize=(18,9))

#Ax 1: Raw data (AFM()
PD.JupiterAFM_plotData_imshow(data_bent, data_labels[1],ax=ax[0],cmap_corr=0.7,cmap='gray')#,snap=True)#, axis, title=True,**plotargs)
ax[0].scatter(Xt,Yt,s=0.1, color='r')
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
ax[2].scatter(X, np.abs(deflection_data), color='black',label='Data')#, label='Snapped Data')
ax[2].scatter(X[mask_d],np.abs(deflection_data[mask_d]) , color='tab:blue',label='fit Data')#, label='Snapped Data')
ax[2].plot(x_grid,np.abs(deflection_bent_ribbon(x_grid,*d_opt)), '--',c='crimson',label='Fit')
ax[2].set_title('|Data - linear reference|')
ax[2].set_xlabel("X (um)")
ax[2].set_ylabel("d (um)")
# Add a text box to the plot
props = dict(boxstyle='round', facecolor='gray', alpha=0.2)
ax[2].text(0.05, 0.98, textstr,
        transform=ax[2].transAxes,   # coordinates relative to axes (0-1)
        fontsize=10,
        verticalalignment='top',
        bbox=props)
ax[2].legend(loc='upper right')

#ax4: local angle
ax[3].scatter(X[mask_twist],theta , color='black')#, label='Snapped Data')
ax[3].set_title('local twist-angle')
ax[3].set_xlabel("X (um)")
ax[3].set_ylabel(f"$ \\Delta \\theta$  (degree)")


plt.savefig(f"Image05_lowerEdge.png")
plt.tight_layout()
