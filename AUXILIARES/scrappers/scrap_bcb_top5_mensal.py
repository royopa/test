import pandas as pd
import requests

# cria uma função que lê o api e transforma em um dataframe
def getbcb(url, proxies):
    response = requests.get(url, proxies=proxies)
    x = response.json()
    df = pd.DataFrame.from_dict(x['value'])
    return df

def rshpBCBdata(df, ind, type): # type pode ser C, M ou L para curto, medio ou longo prazo
    df = df[(df.Indicador == ind) | (df.tipoCalculo == type)]
    df = df.drop(['Indicador','tipoCalculo'], axis=1)
    df = df.stack()
    return df

if __name__ == '__main__':
    proxies = {"http": "http://pietcon:Safrajun19@webproxy:8080",
               "https": "https://pietcon:Safrajun19@webproxy:8080"}
    
    # organizando o caminho dos dados
    origem    = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    secao     = "ExpectativasMercadoTop5Mensais"
    first_obs = "&$skip=0"
    last_obs  = "?top=5"
    format    = "&$format=json"
    vars      = "&$select=Indicador,Data,DataReferencia,tipoCalculo,Media,Mediana,DesvioPadrao,CoeficienteVariacao,Minimo,Maximo"

    url  = origem + secao + last_obs + first_obs + format + vars
    save_path = 'F:\\DADOS\\ASSET\\MACROECONOMIA\\1PIETRO\\DATABASES\\BCB\\ExpecMerc_Top5Mensal_'

    # baixando e organizando os dados
    df = getbcb(url, proxies)
    df.set_index(['Data','DataReferencia'], inplace=True)

    # baixa e organiza a base
    df_igpm_cp = rshpBCBdata(df, ind='IGP-M', type='C')
    df_igpm_mp = rshpBCBdata(df, ind='IGP-M', type='M')
    df_igpm_lp = rshpBCBdata(df, ind='IGP-M', type='l')

    df_igpd_cp = rshpBCBdata(df, ind='IGP-DI', type='C')
    df_igpd_mp = rshpBCBdata(df, ind='IGP-DI', type='M')
    df_igpd_lp = rshpBCBdata(df, ind='IGP-DI', type='L')
    
    df_ipca_cp = rshpBCBdata(df, ind='IPCA', type='C')
    df_ipca_mp = rshpBCBdata(df, ind='IPCA', type='M')
    df_ipca_lp = rshpBCBdata(df, ind='IPCA', type='L')
    
    df_selic_cp = rshpBCBdata(df, ind='Meta para taxa over-selic', type='C')
    df_selic_mp = rshpBCBdata(df, ind='Meta para taxa over-selic', type='M')
    df_selic_lp = rshpBCBdata(df, ind='Meta para taxa over-selic', type='L')

    df_camb_cp = rshpBCBdata(df, ind='Taxa de câmbio', type='C')
    df_camb_mp = rshpBCBdata(df, ind='Taxa de câmbio', type='M')
    df_camb_lp = rshpBCBdata(df, ind='Taxa de câmbio', type='L')

    # salva base no excel
    df_igpm_cp.to_excel(save_path + 'igpm_cp.xlsx', 'val')
    df_igpm_mp.to_excel(save_path + 'igpm_mp.xlsx', 'val')
    df_igpm_lp.to_excel(save_path + 'igpm_lp.xlsx', 'val')

    df_igpd_cp.to_excel(save_path + 'igpdi_cp.xlsx', 'val')
    df_igpd_mp.to_excel(save_path + 'igpdi_mp.xlsx', 'val')
    df_igpd_lp.to_excel(save_path + 'igpdi_lp.xlsx', 'val')
    
    df_ipca_cp.to_excel(save_path + 'ipca_cp.xlsx', 'val')
    df_ipca_mp.to_excel(save_path + 'ipca_mp.xlsx', 'val')
    df_ipca_lp.to_excel(save_path + 'ipca_lp.xlsx', 'val')
    
    df_selic_cp.to_excel(save_path + 'selic_cp.xlsx', 'val')
    df_selic_mp.to_excel(save_path + 'selic_mp.xlsx', 'val')
    df_selic_lp.to_excel(save_path + 'selic_lp.xlsx', 'val')

    df_camb_cp.to_excel(save_path + 'camb_cp.xlsx', 'val')
    df_camb_mp.to_excel(save_path + 'camb_mp.xlsx', 'val')
    df_camb_lp.to_excel(save_path + 'camb_lp.xlsx', 'val')
