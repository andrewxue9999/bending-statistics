#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 19:25:11 2023

@author: carolingold

Routine to plot AFM data - based on 
etelford38/Asylum_Data_Plotting: 
https://github.com/etelford38/Asylum_Data_Plotting/blob/main/Asylum_CAFM.py

- Part 1 - plot Data
- v1: add Cmap_corr
"""

import numpy as np
import pandas as pd
import os
import sys
from matplotlib import pyplot as plt
from pathlib import Path

#import own library
libpath=os.path.join(Path(__file__).parents[1], '00-Library/') 
print(libpath)
sys.path.insert(1,libpath)
import Asylum_LoadData_v0 as LD
import Asylum_manipulateData_v0 as MD
# ==============================================================================
# plot Jupiter Data (outsource later)
# ==============================================================================

def JupiterAFM_plotData(data_dict, data_label, axis, title=True,cmap_corr=None,**plotargs):
    Xplot, Yplot = np.meshgrid(
        np.linspace(0, float(data_dict['xrange']), int(data_dict['points'])),
        np.linspace(0, float(data_dict['yrange']), int(data_dict['lines'])))
    
    plotdata= data_dict['data'][data_label].T
    im = axis.pcolormesh(
        Xplot, Yplot, plotdata, **plotargs)
    
    if cmap_corr!=None:
        from scipy.stats import norm
        mean,std=norm.fit(plotdata)
        print(mean,std)
        im.set_clim((mean-cmap_corr*std),(mean+cmap_corr*std))
    # cbar=fig.colorbar(im,ax=axis)
    # cbar.set_label('test')
    if title==True:
        axis.set_title(data_dict['filename']+': '+str(data_label), fontsize=12)
    
    axis.set_xlabel('X (m)')#, fontsize=24)
    axis.set_ylabel('Y (m)')#, fontsize=24)
    axis.set_aspect('equal')
    return axis

# ==============================================================================
# plot Jupiter Data (outsource later)
# ==============================================================================

def JupiterAFM_plotData_imshow(data_dict, data_label, ax, title=True,cmap_corr=None,**plotargs):
    
    plotdata= np.flipud(data_dict['data'][data_label].T)
    # print('overview dict label',overview_channel)
    data=MD.Polyfit_subtract_2d(plotdata,1)
   
    im = ax.imshow(data, extent=[0, float(data_dict['xrange'])
                                  / 1e-6, 0, float(data_dict['yrange'])/1e-6],
                    **plotargs)
    if cmap_corr!=None:
        from scipy.stats import norm
        mean,std=norm.fit(data)
        im.set_clim((mean-cmap_corr*std),(mean+cmap_corr*std))
        
    
    plt.xlabel('x (um)')
    plt.ylabel('y (um)')
    im_ratio = data.shape[0]/data.shape[1]
    '''
    #Colorbar
    # cbar = fig.colorbar(im,fraction=0.046*im_ratio, pad=0.04)
    # cbar.set_label(r'%s'%overview_channel)
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    axins = inset_axes(
    ax,
    width="20%",  # width: 5% of parent_bbox width
    height="5%",  # height: 50%
    loc="lower left",
    bbox_to_anchor=(0.8, 1.01, 1, 1),
    bbox_transform=ax.transAxes,
    borderpad=0,
    )
    cbar=  fig.colorbar(im, cax=axins,orientation='horizontal')#ticks=[-1, 0, 1])
    cbar.set_ticks([])
    # Set the tick labels above the colorbar
    cbar.ax.xaxis.set_ticks_position('top')
'''

    return ax
