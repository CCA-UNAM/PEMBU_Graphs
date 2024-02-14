# **Gráficas PEMBU**

* *stations_info.csv*: contiene la información de las estaciones.
*  *.env*: contiene la ruta de la carpeta de salida y la ruta del archivo con información de las esaciones. 

## Enviroments 

### Instalación de anaconda
Comandos linux para la instalación de anaconda
1. Descarga de anaconda
```bash
curl -LO
https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
```
2. Ejecución  del instalador
```bash
bash Anaconda3-2023.09-0-Linux-x86_64.sh
```

### Creación del enviroment

Comandos para crear el enviroment a partir del archivo *env_windRoses.txt*

```bash
conda create -n windRoses --file env_windRoses.txt
```

## Ejecución 

1. Activar el enviroment
```bash
conda activate windRoses
```
2. Generar las gráficas  de 7 días 
   
```bash
python st_pembu_7d.py
```
3. Generar las gráficas  de la última hora
  
```bash
python st_pembu_1h.py
```