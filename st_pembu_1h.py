import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from datetime import timedelta, datetime
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from ftplib import FTP
import os
import math
from windrose import WindroseAxes
from dotenv import dotenv_values
import matplotlib.image as image 
from tools import *
import requests
import io
import warnings
warnings.filterwarnings('ignore')

config = dotenv_values(".env") 
station_data_dir=config['data_dir']
output_dir=config['graphs_dir']
station_info_file=config['info_file']
im = image.imread("logo.jpg")

stationsinfo = pd.read_csv(station_info_file, sep=',', encoding = 'latin1')

for station_ind, station in stationsinfo.iterrows():
    try:
    
        station_id=station["stations"]
        url ='https://www.ruoa.unam.mx/pembu/datos/'+station_id+'/downld08.txt'
        data_io=read_clean(url)
        cols_name_array, usecols =get_cols(station_id)
        datahr = pd.read_csv(data_io, sep='\\s+', engine='python',skiprows=3, header=None,names=cols_name_array, usecols=usecols)
        ts_col=datahr.Date +" "+datahr['Time']
        datahr.insert(loc=0, column='ts', value=ts_col)
        datahr['Datetime'] = datahr['ts'].apply(get_date)
        datahr=datahr.set_index('Datetime')
        datahr=datahr.drop(['ts','Date','Time'  ], axis=1)
        datahr["Wind_Dir"]=datahr["Wind_Dir"].map(directions)
        last_time = datahr.tail(1).index[0]
        start_time = last_time - timedelta(minutes=60)
        daysplot = pd.date_range(start_time, last_time)
        daysplot = daysplot.strftime('%Y-%m-%d')
        last_records=datahr.loc[start_time:last_time]
        last_record=last_records.tail(1)
        last_r=last_record.values[0].tolist()
        
        labels=[ 'Temperatura (°C)', 'Humedad relativa (%)', 'Rapidez viento (m/s)','Dirección viento (°)', 'Precipitación (mm)', 'Presión atm (hPa)','Radiación solar (W/m\u00b2)', 'Índice UV']
        rows_color=[['lightyellow','lightyellow'],['lightsteelblue','lightsteelblue']]*4
        calms = (100*(last_records.Wind_Speed < 0.3).sum())/((last_records.Wind_Speed).count())
        max_speed= max(math.ceil(max(last_records.Wind_Speed)),5)
        min_rang=0.3
        bins_range = [min_rang]
        bins_range.extend(range(1,max_speed,1)) 
        last_records["Wind_Speed"]=last_records['Wind_Speed'].clip(lower=0.3)

        output_graphs_dir=output_dir+station_id
        if not os.path.exists(output_graphs_dir):
            os.makedirs(output_graphs_dir)

        fig,[ax1,ax2] =plt.subplots(nrows=1,ncols=2, squeeze='False',gridspec_kw={'wspace':1.0})  
        fig.set_size_inches(7.56,6.71)
        ax1.axis('tight')
        ax1.axis('off')
        ax2.axis('off')
        fig.figimage(im, xo=300, yo=1770 , zorder=0, alpha=1)
        tablelastmin = ax1.table(cellText = np.array([labels, last_r]).transpose(), colLabels = None, cellColours=rows_color, bbox=[-0.25, 0.07, 1.5, 0.7], cellLoc='right', rowLoc='right', edges='closed')
        tablelastmin.scale(1,2.5)
        tablelastmin.auto_set_font_size(False)
        tablelastmin.auto_set_column_width([0,1])
        tablelastmin.set_fontsize(12)
        for cell in tablelastmin.get_children():
            cell.set_edgecolor('darkblue')

        ax2 = fig.add_subplot(122, projection='windrose')
        ax2.bar(last_records.Wind_Dir, last_records.Wind_Speed, normed=True, opening=0.8,edgecolor='white',bins=bins_range)
        ax2.set_xticklabels(["E", "NE", "N", "NW", "W", "SW", "S", "SE"], fontsize=11)
        legend = ax2.legend(title=r'Intensidad ($m\,s^{-1}$)', fontsize=10, loc=0, bbox_to_anchor=(0.79,-0.1), frameon = False)
        plt.setp(legend.get_title(),fontsize=11)

        plot_title = r'Estación Meteorológica ' +  station["short"]  +'\n'r'Condiciones meteorológicas recientes'
        plt.suptitle(plot_title ,fontsize=14, x=0.5, y=0.95,color="midnightblue")
                    
        newax2 = fig.add_axes([0.08, 0.77, 0.5, 0.15])
        newax2.text(0,0,str(last_record.index[0]) + '    ' +'UTC-6', fontsize=12)
        newax2.axis('off') 
        newax3 = fig.add_axes([0.55, 0.74, 0.5, 0.15]) 
        newax3.text(0,0,'Rosa de vientos última hora' +'\n', fontsize=12)
        newax3.axis('off')
        newax4 = fig.add_axes([0.645, 0.04, 0.3, 0.15]) 
        newax4.text(0,0,'Calmas: ' + str(calms.round(1))+ '%', fontsize=10)
        newax4.axis('off')
        # Nombra y guarda imagen
        plotname = output_graphs_dir+'/table_RV_1h_'+ station_id +'.png'
        plt.savefig(plotname,format ='png', dpi = 300)
        print(url," Procesada ")
    
    except Exception as err:
        print("Error al procesar la estación: "+url)
        print(f"error {err=}, {type(err)=}")
        continue   

        

    
     