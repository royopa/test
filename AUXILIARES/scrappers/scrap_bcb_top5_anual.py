import pandas as pd
import requests

# cria uma função que lê o api e transforma em um dataframe
def getbcb(url, proxies):
    response = requests.get(url, proxies=proxies)
    x = response.json()
    df = pd.DataFrame.from_dict(x['value'])
    return df

# type pode ser C, M ou L para curto, medio ou longo prazo
def rshpBCBdata(df, ind, det, type): 
    df = df[(df.Indicador == ind) | (df.IndicadorDetalhe == det) | (df.tipoCalculo == type)]
    df = df.drop(['Indicador','IndicadorDetalhe','tipoCalculo'], axis=1)
    df = df.stack()
    return df

if __name__ == '__main__':
    proxies = {"http": "http://pietcon:Safrajun19@webproxy:8080",
               "https": "https://pietcon:Safrajun19@webproxy:8080"}
    
    # organizando o caminho dos dados
    origem    = "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/"
    secao     = "ExpectativasMercadoTop5Anuais"
    first_obs = "&$skip=0"
    last_obs  = "?top=5"
    format    = "&$format=json"
    vars      = "&$select=Indicador,IndicadorDetalhe,Data,DataReferencia,tipoCalculo,Media,Mediana,DesvioPadrao,CoeficienteVariacao,Minimo,Maximo"

    url  = origem + secao + last_obs + first_obs + format + vars
    save_path = 'F:\\DADOS\\ASSET\\MACROECONOMIA\\1PIETRO\\DATABASES\\BCB\\ExpecMerc_Top5Anual_'

    # baixando e organizando os dados
    df = getbcb(url, proxies)
    df.set_index(['Data','DataReferencia'], inplace=True)

    # baixa e organiza a base
    df_igpm_cp = rshpBCBdata(df, ind='IGP-M', det='None', type='C')
    df_igpm_mp = rshpBCBdata(df, ind='IGP-M', det='None', type='M')
    df_igpm_lp = rshpBCBdata(df, ind='IGP-M', det='None', type='l')

    df_igpd_cp = rshpBCBdata(df, ind='IGP-DI', det='None', type='C')
    df_igpd_mp = rshpBCBdata(df, ind='IGP-DI', det='None', type='M')
    df_igpd_lp = rshpBCBdata(df, ind='IGP-DI', det='None', type='L')
    
    df_ipca_cp = rshpBCBdata(df, ind='IPCA', det='None', type='C')
    df_ipca_mp = rshpBCBdata(df, ind='IPCA', det='None', type='M')
    df_ipca_lp = rshpBCBdata(df, ind='IPCA', det='None', type='L')
    
    df_selic_fim_cp = rshpBCBdata(df, ind='Meta para taxa over-selic', 
                                  det='Fim do ano', type='C')
    df_selic_fim_mp = rshpBCBdata(df, ind='Meta para taxa over-selic', 
                                  det='Fim do ano', type='M')
    df_selic_fim_lp = rshpBCBdata(df, ind='Meta para taxa over-selic', 
                                  det='Fim do ano', type='L')

    df_selic_med_cp = rshpBCBdata(df, ind='Meta para taxa over-selic', 
                                  det='Media do ano', type='C')
    df_selic_med_mp = rshpBCBdata(df, ind='Meta para taxa over-selic', 
                                  det='Media do ano', type='M')
    df_selic_med_lp = rshpBCBdata(df, ind='Meta para taxa over-selic', 
                                  det='Media do ano', type='L')

    df_camb_fim_cp = rshpBCBdata(df, ind='Taxa de câmbio', 
                                  det='Fim do ano', type='C')
    df_camb_fim_mp = rshpBCBdata(df, ind='Taxa de câmbio', 
                                  det='Fim do ano', type='M')
    df_camb_fim_lp = rshpBCBdata(df, ind='Taxa de câmbio', 
                                  det='Fim do ano', type='L')

    df_camb_med_cp = rshpBCBdata(df, ind='Taxa de câmbio', 
                                  det='Media do ano', type='C')
    df_camb_med_mp = rshpBCBdata(df, ind='Taxa de câmbio', 
                                  det='Media do ano', type='M')
    df_camb_med_lp = rshpBCBdata(df, ind='Taxa de câmbio', 
                                  det='Media do ano', type='L')

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
    
    df_selic_fim_cp.to_excel(save_path + 'selic_fim_cp.xlsx', 'val')
    df_selic_fim_mp.to_excel(save_path + 'selic_fim_mp.xlsx', 'val')
    df_selic_fim_lp.to_excel(save_path + 'selic_fim_lp.xlsx', 'val')

    df_selic_med_cp.to_excel(save_path + 'selic_med_cp.xlsx', 'val')
    df_selic_med_mp.to_excel(save_path + 'selic_med_mp.xlsx', 'val')
    df_selic_med_lp.to_excel(save_path + 'selic_med_lp.xlsx', 'val')

    df_camb_fim_cp.to_excel(save_path + 'camb_fim_cp.xlsx', 'val')
    df_camb_fim_mp.to_excel(save_path + 'camb_fim_mp.xlsx', 'val')
    df_camb_fim_lp.to_excel(save_path + 'camb_fim_lp.xlsx', 'val')

    df_camb_med_cp.to_excel(save_path + 'camb_med_cp.xlsx', 'val')
    df_camb_med_mp.to_excel(save_path + 'camb_med_mp.xlsx', 'val')
    df_camb_med_lp.to_excel(save_path + 'camb_med_lp.xlsx', 'val')
