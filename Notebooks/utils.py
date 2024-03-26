import pandas as pd
import os
import pyarrow as pa
import pyarrow.parquet as pq
from uszipcode import SearchEngine

#Recibe como variable un Dataframe y una columna, y devuelve el conteo de los datos. Útil para columnas con datos categóricos o booleanos.
def dataPercentage(df, column):
    counts = df[column].value_counts()
    percentages = round(100 * counts / len(df), 2)
    dfResults = pd.DataFrame({
        "Cantidad":counts,
        "Porcentaje":percentages
    })
    return dfResults

#Recibe como variable un Dataframe. Devuelve un Dataframe con la distribución de datos nulos y no nulos por columna.
def dataType(df):
    dfDict = {
        "name": [], "data_type": [], "not_null_%": [], "null_%": [],"not_null":[], "null": []
    }
    for column in df.columns:
        notNull = (df[column].count() / len(df)) * 100
        dfDict["name"].append(column)
        dfDict["data_type"].append(df[column].apply(type).unique())
        dfDict["not_null_%"].append(round(notNull, 4))
        dfDict["null_%"].append(round(100-notNull, 4))
        dfDict["not_null"].append(df[column].notnull().sum())
        dfDict["null"].append(df[column].isnull().sum())
    dataTypeDf = pd.DataFrame(dfDict)
    return dataTypeDf

#Recibe como variable la ruta de un archivo. Devuelve un Dataframe con los datos de ese archivo. Para archivos tipo json, realiza una carga por chunks. Modificar ´'chunkSize'´ (tamaño de cada chunk en bytes) de acuerdo a las capacidades de su PC.
def loadFile(path):
    fileExt = path.split('.')[-1].lower()
    
    readFunction = {
        'csv': pd.read_csv,
        'parquet': pd.read_parquet,
        'json': pd.read_json,
        'pkl': pd.read_pickle
    }
    
    if fileExt in readFunction:
        if fileExt == 'json':
            chunkSize = 1000000

            chunks = []

            for chunk in readFunction[fileExt](path, lines=True, chunksize=chunkSize):
                chunks.append(chunk)

            df = pd.concat(chunks, ignore_index=True)
        elif fileExt == 'parquet':
            df = readFunction[fileExt](path, engine='pyarrow')
        else:
            df = readFunction[fileExt](path)
    else:
        print(f"Archivo inválido: {fileExt}")
        return None
    
    return df

#Recibe como variable la ruta de un archivo. Carga el archivo utilizando ´loadFile()´. Verifica la existencia de columnas duplicadas vacías, datos nulos, filas duplicadas y columnas con múltiples tipos de dato.
def dataHealthCheck(path):
    df = loadFile(path)

    check = False

    if type(df) == type(None):
        return

    if df.columns.duplicated().any():
        duppedDf = df.loc[:, df.columns.duplicated()]
        df = df.loc[:, ~df.columns.duplicated()]
        if duppedDf.dropna(axis=0,how='all').empty:
            print(f'Se encontraron columnas duplicadas vacías en {path}')
        else:
            print(f'Se encontraron columnas duplicadas con datos en {path}.')
    
    datType = dataType(df)

    if datType['data_type'].apply(lambda x: len(x) > 1).any():
        print(f'{path} contiene múltiples tipos de dato.')
        check = True
        
    if datType['null'].apply(lambda x: x > 0).any():
        print(f'{path} contiene datos nulos.')
        check = True

    if df.map(str).duplicated(keep=False).any():
        df = df.map(str).drop_duplicates(subset=df.columns, keep = 'first')
        print(f'Se encontraron filas duplicadas {path}')
        check = True

    if check == True:
        return
    else:
        return print(f'{path} está OK.')

#Recibe como variable la ruta de una carpeta. Itera sobre todos los archivos de la carpeta aplicando ´dataHealthCheck()´.
def processFiles(folderPath):
    for folderName, subfolders, fileNames in os.walk(folderPath):
        for fileName in fileNames:
            filePath = os.path.join(folderName, fileName)
            dataHealthCheck(filePath)

#Recibe como variable la ruta de una carpeta. Itera sobre todos los archivos de la carpeta. Carga los archivos con ´loadFile()´ y verifica que todos contengan la misma estructura de columnas.
def dataStructure(folderPath):
    columns = []
    for folderName, subfolders, fileNames in os.walk(folderPath):
        for fileName in fileNames:
            filePath = os.path.join(folderName, fileName)
            df = loadFile(filePath)
            
            if type(df) != type(None):
                if columns == []:
                    columns = df.columns.tolist()
                else:
                    for i in df.columns.tolist():
                        if i not in columns:
                            columns.append(i)
                            print(f'Se añadió la columna {i} del archivo {filePath}')
    return columns

#Recibe como variable la ruta de una carpeta. Itera sobre todos losa rchivos de la carpeta y los une en un solo DataFrame.
def concat(folderPath):
    resultDf = pd.DataFrame()
    for folderName, subfolders, fileNames in os.walk(folderPath):
        for fileName in fileNames:
            filePath = os.path.join(folderName, fileName)
            df = loadFile(filePath)
            print(f'Cargando {fileName}')
            if not resultDf.empty:
                resultDf = pd.concat([resultDf, df], axis = 0)
            else:
                resultDf = df
    return resultDf

#Recibe como variable un código postal y devuelve el estado al que pertenece.
def stateFromZip(zipCode):
    search = SearchEngine()
    result = search.by_zipcode(zipCode)

    if result:
        state = result.state
        return state
    else:
        return "Estado no encontrado"
    
def etlReviews(folderPath):
    resultDf = pd.DataFrame()
    for folderName, subfolders, fileNames in os.walk(folderPath):
        for fileName in fileNames:
            filePath = os.path.join(folderName, fileName)
            df = loadFile(filePath)
            print(f'Cargando {filePath}...')

            if not resultDf.empty:
                resultDf = pd.concat([resultDf, df], axis = 0)
            else:
                resultDf = df
        resultDf = resultDf.drop(columns=['pics','resp'])

        if resultDf.duplicated().any():
            print(f'Se eliminaron filas duplicadas en {folderName}')
            resultDf = resultDf.drop_duplicates()

        if resultDf['text'].isnull().any():
            resultDf['text'] = resultDf['text'].fillna('No comment')

        # ETL
        
        resultDf['time'] = pd.to_datetime(resultDf['time'], unit='ms')
        resultDf['date'] = pd.to_datetime(resultDf['time']).dt.date
        resultDf['hour'] = pd.to_datetime(resultDf['time']).dt.hour
        resultDf['time'] = pd.to_datetime(resultDf['time']).dt.time

    return resultDf