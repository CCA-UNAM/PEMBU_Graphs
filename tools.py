
from datetime import timedelta, datetime
import numpy as np
import requests
import io
import re

directions = {"N":0,"NNE":22.5,"NE":45,"ENE":67.5,"E":90,"ESE":112.5,"SE":135,"SSE":157.5,"S":180,"SSW":202.5,"SW":225,"WSW":247.5,"W":270,"WNW":292.5,"NW":315,"NNW":337.5,"---":np.nan}


def get_cols(x):
    if x== "cchv":
        cols_name_array=["Date","Time","Temp_Out","Hi_Temp","Low_Temp", "Out_Hum","Dew_Pt","Wind_Speed","Wind_Dir","Wind_Run","Hi_Speed","Hi_Dir","Wind_Chill","Heat_Index","Thw_Index","Thsw_Index","Bar","Rain","Rain_Rate","Solar_Rad","Solar_Energy","Hi_Solar_Rad","UV_Index","Uv_Dose","Hi_UV","Heat_D-D","Cool_D-D","In_temp", "In_hum", "In_dew", "In_heat", "In EMC", "InAirDensity" , "ET",  "Soil1_moist", "Soil_Temp","Leaf_Wet1", "leaf_wet2","leaf_temp1","leaf_temp2","Wind_Samp", "Wind_Tx", "Iss_Recept","Arc_Int"]
    else:     
        cols_name_array=["Date","Time","Temp_Out","Hi_Temp","Low_Temp","Out_Hum","Dew_Pt","Wind_Speed","Wind_Dir","Wind_Run","Hi_Speed","Hi_Dir","Wind_Chill","Heat_Index","Thw_Index","Thsw_Index","Bar","Rain","Rain_Rate","Solar_Rad","Solar_Energy","Solar_Hi_Rad","UV_Index","UV_Dose","Hi_UV","Heat_D-D","Cool_D-D","In_Temp","In_Hum","In_Dew","In_Heat","In_EMC","In_Density","ET","Wind_Samp","Wind_TX","Iss_Recept","Arc_Int"]
    usecols=['Date','Time','Temp_Out','Out_Hum', 'Wind_Speed','Wind_Dir' ,'Rain' , 'Bar','Solar_Rad','UV_Index']
    return cols_name_array, usecols

def get_date(x):
      
        x = x.strip()
        x = re.sub('\\s+', '_', x)
        
        if ('a'in x or 'p' in x): 
            formato = '%d/%m/%y_%I:%M%p'
            x=x.upper()+'M'             
        else:
            formato = "%d/%m/%y_%H:%M" 
        val_date=datetime.strptime(x,formato)
        return  val_date
        
    

def circ_mean_np(angles,azimuth=True):
    
            rads = np.deg2rad(angles)  
            av_sin = np.nanmean(np.sin(rads))  
            av_cos = np.nanmean(np.cos(rads))  
            ang_rad = np.arctan2(av_sin,av_cos)  
            ang_deg = np.rad2deg(ang_rad)  
            if azimuth:  
                ang_deg = np.mod(ang_deg,360.)  
            return ang_deg
        
def read_clean(url):
    # Realizar la solicitud GET para descargar el archivo
    response = requests.get(url)
    data_io=''
    # Verificar que la solicitud fue exitosa
    if response.status_code ==  200:
        data = response.content.decode('utf-8')
        #  remover espacios en blanco al inicio y final de las líneas)
        clean_data = '\n'.join([line.strip() for line in data.splitlines()]) 
        # Crear un StringIO para leer los datos limpios con pandas
        data_io = io.StringIO(clean_data)
    
    return data_io