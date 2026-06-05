#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:49:28 2026

@author: carolingold

- inspired and based on legacy code by Bjarke S. Jessen and M. Kapfer
"""

import sys, pathlib, datetime, numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_point_clicker import clicker

# ==============================================================================
# 1. SMART LIBRARY LOADING
# ==============================================================================
libpath = str(pathlib.Path(__file__).parents[3] / '00-Library')
if libpath not in sys.path: sys.path.insert(1, libpath)

import Asylum_LoadData_v3 as LD

# ==============================================================================
# 2. Main Application Class
# ==============================================================================

class AFM_Digitizer:
    def __init__(self, filename, stack_name):
        self.filename = filename
        
        # Load and Transpose immediately for visual correctness
        self.full_dict = LD.JupiterAFM_loadData_toDict(filename, stack_name)
        self.data = self.full_dict['data'][self.full_dict['labels'][1]].T 
        
        # Micron ranges
        self.um_x = float(self.full_dict.get('xrange', 0)) * 1e6
        self.um_y = float(self.full_dict.get('yrange', 0)) * 1e6
        
        # Setup Figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.2)
        
        # Contrast Clipping (1st and 99th percentile)
        vmin, vmax = np.percentile(self.data[~np.isnan(self.data)], [1, 99])
        
        # Transposed Plotting: Matches hover coords to saved coords
        self.im = self.ax.imshow(self.data, 
                                 cmap='gray', vmin=vmin, vmax=vmax, 
                                 origin='lower', 
                                 extent=[0, self.um_x, 0, self.um_y],
                                 aspect='equal')
        
        plt.colorbar(self.im, ax=self.ax, label="Height (m)")
        self.ax.set_xlabel("X ($\mu m$)")
        self.ax.set_ylabel("Y ($\mu m$)")
        
        # 1. Re-enable Clicker
        self.klicker = clicker(self.ax, ["edge"], markers=["x"], colors=["red"])
        
        # 2. RE-ENABLE SCROLL ZOOM
        self.fig.canvas.mpl_connect('scroll_event', self.handle_zoom)
        
        # Save Button
        self.btn_ax = plt.axes([0.7, 0.05, 0.15, 0.075])
        self.btn = Button(self.btn_ax, 'Save & Exit', color='honeydew')
        self.btn.on_clicked(self.close_app)

    def handle_zoom(self, event):
        """ Standard zoom logic integrated into the class. """
        if event.inaxes != self.ax: return
        
        base_scale = 1.3
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # Determine zoom in or out
        scale_factor = 1/base_scale if event.button == 'up' else base_scale
        
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        rel_x = (cur_xlim[1] - event.xdata) / (cur_xlim[1] - cur_xlim[0])
        rel_y = (cur_ylim[1] - event.ydata) / (cur_ylim[1] - cur_ylim[0])
        
        self.ax.set_xlim([event.xdata - new_width * (1-rel_x), event.xdata + new_width * rel_x])
        self.ax.set_ylim([event.ydata - new_height * (1-rel_y), event.ydata + new_height * rel_y])
        self.fig.canvas.draw_idle()

    def close_app(self, event):
        pts = self.klicker.get_positions()['edge']
        if len(pts) > 0:
            out = pathlib.Path("results")
            out.mkdir(exist_ok=True)
            ts = datetime.datetime.now().strftime("%H%M%S")
            stem = pathlib.Path(self.filename).stem
            
            # Reset view for the saved PNG
            self.ax.set_xlim(0, self.um_x)
            self.ax.set_ylim(0, self.um_y)
            
            self.fig.savefig(out / f"plot_{stem}_{ts}.png", bbox_inches='tight')
            np.savetxt(out / f"coords_{stem}_{ts}.txt", pts, fmt='%.6f', header="X_um\tY_um")
            print(f"Saved {len(pts)} points.")
            
        plt.close('all')


if __name__ == "__main__":
    # Ensure correct params
    app = AFM_Digitizer('../../Data/Image0005.ibw', 'Trevor_WSe2_tgr3')
    plt.show(block=True)