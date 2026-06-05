#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 19:08:04 2023

@author: carolingold

Routine to plot AFM data - based on 
etelford38/Asylum_Data_Plotting: 
https://github.com/etelford38/Asylum_Data_Plotting/blob/main/Asylum_CAFM.py

- Part 0 - Load Data

--------
This part containts:
--------
natural_sort(l): sorts data files according to their alphanumerical identifier
getMetaData(dat): gets metaData from .ibw files
getData2D(dat): extracts 2d data from .ibw file

v2: remove meta-data read-in. The "error" we saw indicates that the scanframe was changed during scan. 

v3: remove files where scanframe was scanned throughout the scan from meta-data read in completely

"""

# ==============================================================================
# Load packages
# ==============================================================================
import igor.binarywave as igor
import numpy as np
import re
import pandas as pd
from pathlib import Path


# ==============================================================================
# Load functions 
# ==============================================================================


def natural_sort(l):
    def convert(text): return int(text) if text.isdigit() else text.lower()
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def getMetaData(dat):
    note = dat['wave']['note'].decode('ISO-8859-1')
    metaData = {}
    name = []
    val = []
    for line in note.split('\r'):
        name.append(line.split(':')[0])
        try:
            val.append(line.split(':')[1])
        except IndexError:
            val.append('nan')
    metaData = dict(zip(name, val))
    # print('name;', name)

    return metaData


def getData2D(dat):
    data = dat['wave']['wData']
    Label = dat['wave']['labels'][2]
    Label = Label[1:]
    dat = np.zeros((len(Label), np.shape(data)[0], np.shape(data)[1]))
    dict_res = {}
    # print('dat',np.shape(dat))
    for i in range(len(Label)):
        # print('data',np.shape(data[:, :, i]))
        dat[i] = data[:, :, i]

    for l, d in zip(Label, dat):
        dict_res[l] = d
    # print('dat',dat)
    return Label, dict_res


# %%
# ==============================================================================
# correct metadata (outsource later)
# ==============================================================================
def LoadMetadata(filenames, stackname):#, metaTable=False):
    # Make sure that a metadata file ("{Stackname}_metadata.txt") exists,
    # which contains a table listing:
    # Scan Size | x offset | y offset | Imaging mode | Scan angle | #Lines/points

    metadata_file = f'{stackname}_metaData.txt'
    # print(metadata_file)
    metadata_path = Path(metadata_file)
   

    # check if metadata txt already exists, if not read in values from metadata file
    #  & ask to enter values manually if error detected
    if metadata_path.is_file():
        print('%s metadata file exists' % stackname)
    else:
        print('%s metadata file does not exists, create it' % stackname)
        
        filename_list=[]
        ListSize = []
        ListMode = []
        ListXOffset = []
        ListYOffset = []
        ListAngle = []
        ListxPoints = []
        ListyPoints = []
        ListType = []
        
        
        for i, f in enumerate(filenames):
            dat = igor.load(f)

            metaData = {}
            metaData = getMetaData(dat)
            print(f)
            
                        
            try:
                Sizetmp = float(metaData['ScanSize'])
            except ValueError:
                Sizetmp='nan'
                
            try:
                Xtmp = float(metaData['XOffset'])
            except ValueError:
                Xtmp='nan'
        
            try:
                Ytmp = float(metaData['YOffset'])
            except ValueError:
                Ytmp='nan'
            
            if ((Sizetmp!='nan')):
                filename_list.append(f)
                ListSize.append(Sizetmp)
                ListMode.append(metaData['ImagingMode'])
                ListXOffset.append(Xtmp)
                ListYOffset.append(Ytmp)
                ListAngle.append(metaData['ScanAngle'])
                ListxPoints.append(metaData['PointsLines'])
                # print(metaData['PointsLines'])
                ListyPoints.append(metaData['ScanLines'])
                # ListType.append(metaData['Channel2DataType'])
        print('made it here')
        with open(metadata_file, 'w') as filetxt:
            filetxt.write(
                'filename \t Mode  \t Scan size \t X Offset \t Y Offset \t Scan Angle \t #Points \t #Lines \n')
            for i,f in enumerate(filename_list):
                filetxt.write(
                    f'{f} \t {ListMode[i]} \t {ListSize[i]} \t {ListXOffset[i]} \t {ListYOffset[i]} \t {ListAngle[i]} \t {ListxPoints[i]}\t {ListyPoints[i]}\n')
    return metadata_file
    # filetxt.write(f'{f} \t {Mode} \t {scanType} \t {Sizetmp} \t {Xtmp} \t {Ytmp} \t {scanAngle} \t {points}\n')


# ==============================================================================
# load Data into dict (outsource later)
# ==============================================================================
Jupiterdict = {
    'Scan size': 'ScanSize',
    'X Offset': 'XOffset',
    'Y Offset': 'YOffset',
}


def JupiterAFM_loadData_toDict(f, stackname):
    '''

    # loads Jupiter AFM data into dictionary 
    # (see below for more detailed description of each dictionary-entry)
    # 1 input options:
    # (1) give filename f-> will load data from .dat file directly into dict


    # Parameters
    # ----------

    # f : Path instance
    #     Path to datafile (usually .dat file)

    # Returns
    # -------
    # Data_dict : dictionary
    #     Data dictionary, where the data and certain scan parameters are read 
    #     into a dictionary
    #     {'data','labels','scanSize,'points','xOffset','yOffset','scanAngle',filename','ImagingMode','ScanType','fullMetaData'} 

    #     data : dictionary containing data
    #     labels: str, labels to access the data in the data_dict
    #     scanSize: float, Size of the scan frame, currently th
    #     xRange: float, ScanSize in x-direction
    #     yRange:float, ScanSize in y-direction, currently = xRange
    #     points: int, number of points 
    #     lines: int, number of 
    #     xOffset: float, offset of the scan in the x-direction
    #     yOffset: float, offset of the scan in the y-direction
    #     scanAngle: float, scan angle in deg (?)
    #     filename: str, name of the file
    #     ImagingMode: str, type of Imaging mode (topography, contact, etc)
    #     scanType: str, type of scan (Tapping, LFM, PFM, etc)
    #     fullMetaData: contains ALL the metadata 


    # prints name of each dictionary entry in console
    # Acess individual entry via their  name: e.g.
    # ZRetrace=Data_dict['ZSensorRetrace']
    '''
    dat = igor.load(f)
    metaData = getMetaData(dat)
    labels, data_dict = getData2D(dat)
    print('f',f)
    Val_List = []
    for name in ['Scan size', 'X Offset', 'Y Offset']:
        # print('name=',name)
        try:
            value = float(metaData[Jupiterdict[name]])
        except ValueError:
            metadata_file = f'{stackname}_metaData.txt'
            # print(metadata_file)
            metadata_path = Path(metadata_file)

            # check if metadata txt already exists, if not read in values from metadata file
            #  & ask to enter values manually if error detected
            if metadata_path.is_file():
                # print('%s metadata file exists' %Stack)
                scanDetails = pd.read_csv(
                    metadata_file, sep='\s*\t\s*', engine='python')
                # print(scanDetails)
                ind = np.where(scanDetails['filename'] == f)[0][0]
                value = scanDetails[name][ind]
                # print('made it here')
            else:
                print('error in metadata and no corrected metadatafile')
                print('please run the correctMetadata function')
        Val_List.append(value)

    Data_dict = {
        'data': data_dict,
        'labels': labels,
        'scanSize': Val_List[0],
        'xrange': Val_List[0],
        'yrange': Val_List[0],
        'points': metaData['ScanPoints'],
        'lines': metaData['ScanLines'],
        'xOffset': Val_List[1],
        'yOffset': Val_List[2],
        'scanAngle': metaData['ScanAngle'],
        'filename': f,
        'ImagingMode': metaData['ImagingMode'],
        'fullMetaData': metaData
    }

    return Data_dict
