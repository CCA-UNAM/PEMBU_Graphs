# **Gráficas PEMBU**

* *stations_info.csv*: contiene la información de las estaciones.
*  *.env*: contiene la ruta de la carpeta de salida y la ruta del archivo con información de las esaciones. 

## Creación del enviroment

conda create -n windRoses --file env_windRoses.txt

## Ejecución 

conda activate windRoses

python st_pembu_7d.py

python st_pembu_1h.py