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
        start_time = last_time - timedelta(days=7)
        daysplot = pd.date_range(start_time, last_time)
        daysplot = daysplot.strftime('%Y-%m-%d')
        last_records=datahr.loc[start_time:last_time]
        last_record=last_records.tail(1)
        last_r=last_record.values[0].tolist()
        
        last_records=last_records.replace(to_replace='---', value=np.nan, regex=True, inplace=False)
        last_records = last_records.astype(float)
        last_records=last_records.resample('60Min').agg({'Temp_Out': np.nanmean, 'Out_Hum': np.nanmean, 
                                         'Wind_Speed': np.nanmean, 'Wind_Dir': circ_mean_np,"Solar_Rad":np.nanmean,
                                         'Rain': np.nansum, 'Bar': np.nanmean,'UV_Index': np.nanmean}).round(1)
        
        last_records.columns=['Temp_Avg','RH_Avg','WSpeed_Avg','WDir_Avg','Press_Avg','Rain_Tot','Rad_Avg','UVIndex_Avg']
        plot_title = r'   Estación Meteorológica ' + station["short"]  + '\n'r'   Condiciones meteorol'+u'ó'+'gicas '+u'ú'+'ltimos 7 días\n\n\n\n\n '
        
        output_graphs_dir=output_dir+station_id
        if not os.path.exists(output_graphs_dir):
            os.makedirs(output_graphs_dir)

        fig,(ax1,ax3,ax5,ax7) = plt.subplots(4,1,sharex=True, gridspec_kw={'hspace':0.03})
        plt.suptitle(plot_title ,fontsize=13,ha='left',x=0.1, y=0.95,color="midnightblue")
        fig.figimage(im, xo=25, yo=1770 , zorder=1, alpha=1)
        # Parea ejes en cada panel
        ax2=ax1.twinx()
        ax4=ax3.twinx()
        ax6=ax5.twinx()
        ax8=ax7.twinx()
        # Grafica lineas, puntos o barras segun variable y da formato a eje Y
        ax1.plot(last_records['Temp_Avg'],color='red',label='Temperatura\n (°C')
        ax1.set_ylabel('Temperatura\n (°C)',color='red',fontsize = 11)

        ax2.plot(last_records['RH_Avg'],color='navy',label='Humedad\nRelativa (%)')
        ax2.set_ylabel('Humedad\n relativa (%)',color='navy',fontsize = 11)

        ax3.plot(last_records['WSpeed_Avg'],color='goldenrod',label='Rapidez viento\n (m/s)')
        ax3.set_ylabel('Rapidez viento\n (m/s)',color='goldenrod',fontsize = 11)

        ax4.plot(last_records['WDir_Avg'],'D', ms=4, linestyle='',color='green',label='Direccion viento (°)')
        ax4.set_ylabel('Direccion viento\n (°)',color='green',fontsize = 11)

        ax5.plot(last_records['Rad_Avg'],color='crimson',label='Radiacion solar\n (W/m2)')
        ax5.set_ylabel('Radiacion\n solar (W/m\u00b2)',color='crimson',fontsize = 11)

        ax6.plot(last_records['UVIndex_Avg'],color='blueviolet',label='Indice UV\n (adim)')
        ax6.set_ylabel('Indice UV\n (adim)',color='blueviolet',fontsize = 11)

        ax7.plot(last_records['Press_Avg'],color='black',label='Presion atm\n (hPa)')
        ax7.set_ylabel('Presion atm\n (hPa)',color='black',fontsize = 11)

        ax8.bar(last_records.index,last_records['Rain_Tot'],width = 0.03,color='blue',label='Precipitacion\n (mm)')
        ax8.set_ylim(0,None)
        ax8.set_ylabel('Precipitación\n (mm)',color='blue',fontsize = 11)
        ax8.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))

            
        axi=[ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8] 
            
        # Lineas verticales cada 6 h, da formato a eje X
        for ax in axi:
            ax.set_xlim(start_time,last_time)       
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))	
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(n=4))
            ax.xaxis.grid(True,'minor', color='lightgray',linestyle='--') 
            ax.xaxis.grid(True,'major', color='k',linestyle='--')
            ax.tick_params(axis='x',labelsize=10)
                
                
        # Ajusta tamaño de figura y titulo antes de guardar imagen
        fig.set_size_inches(7.56, 6.71)
        fig.subplots_adjust(top=0.85,right=0.86)         
        # Nombra y guarda imagen
        plotname = output_graphs_dir+'/ST7d_'+ station_id +'.png'
        #plotloc = plots_folder + plotname
        plt.savefig(plotname,format ='png', dpi = 300)
        
        
        calms = (100*(last_records.WSpeed_Avg < 0.3).sum())/((last_records.WSpeed_Avg).count())
        max_speed= max(math.ceil(max(last_records.WSpeed_Avg)),5)
        min_rang=0.3
        bins_range = [min_rang]
        bins_range.extend(range(1,max_speed,1)) 
        time_plotRV = last_time.now().strftime('%Y-%m-%d %H')+':00'
        
        figwr=plt.figure()
        figwr.set_size_inches(7.56,6.71)
        rect=[0.1,0.1,0.6,0.6] 
        wa=WindroseAxes(figwr,rect)
        figwr.add_axes(wa)
        wa.bar(last_records.WDir_Avg, last_records.WSpeed_Avg, normed=True, opening=0.8, edgecolor='white',bins=bins_range)
        wa.set_xticklabels(["E", "NE", "N", "NW", "W", "SW", "S", "SE"], fontsize=14)
        legend = wa.legend(title=r'Intensidad ($m\,s^{-1}$)', fontsize=12, loc=4, bbox_to_anchor=(1.55,0.09), frameon=False)
        plt.setp(legend.get_title(),fontsize=12)
        plot_title = r'Estaci'+u'ó'+'n Meteorológica ' + station["short"] + '\n'r'Rosa de vientos '+u'ú'+'ltimos 7 días\n '+'\n' 
        plt.suptitle(plot_title,fontsize=14,x=0.5,y=0.94,color="midnightblue")
        figwr.figimage(im, xo=300, yo=1770 , zorder=1, alpha=1)
        newax2 = figwr.add_axes([0.17, 0.82, 0.5, 0.15], zorder=0) 
        newax2.text(0,0.1, 'latitud: '+ str(station["lat"])+'    longitud: '+str(station["lon"])+'    altitud: '+str(station["lat"]), fontsize=12)
        newax2.text(0,-0.2,time_plotRV + '    ' +'UTC-6', fontsize=12)
        newax2.axis('off')

        newax3 = figwr.add_axes([0.75, 0.135, 0.3, 0.15]) 
        newax3.text(0,0,'Calmas: ' + str(calms.round(1))+ '%', fontsize=11)
        newax3.axis('off')                
            
        # Nombra y guarda imagen
        plotname2 = output_graphs_dir+'/WR7d_'+ station_id +'.png'

        plt.savefig(plotname2, format ='png',dpi = 300)
        print(url," Procesada ")
    
    except Exception as err:
        print("Error al procesar la estación: "+url)
        print(f"error {err=}, {type(err)=}")
        continue   

        

    
     