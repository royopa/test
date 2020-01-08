from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import glob, os, time

def download_mcm(cod_plan):
    pags = 'http://www.mcmconsultores.com.br/'
    path_down = 'C:\\Users\\pietcon\\Downloads\\'
    html_plan = "http://www.mcmconsultores.com.br/arearestrita/bancodedadositem/download/" + str(cod_plan)
    
    # carregando driver remoto
    driver = webdriver.Chrome('Z:\Macroeconomia\databases\Atacado\drivers_selenium\chromedriver.exe')
    # carregando a pagina
    driver.set_page_load_timeout(10)
    
    # logando na MCM
    driver.get(pags)
    driver.find_element_by_name('UserName').send_keys('pietro.consonni@safra.com.br')
    driver.find_element_by_name('Password').send_keys('mcmmcm')
    driver.find_element_by_name('Password').send_keys(Keys.ENTER)
    
    # baixando planilha de interesse
    driver.get(html_plan)
    time.sleep(2)
    driver.quit()
        
    # coletando planilha de interesse na pasta Downloads do meu PC
    files = [f for f in glob.glob(path_down + "**/*.xls", recursive=True)]
    last_file = max(files, key=os.path.getctime)
    plan = pd.read_excel(last_file, sheet_name=None)
    return (plan)
        
