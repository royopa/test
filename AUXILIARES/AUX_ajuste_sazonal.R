library(stats)
library(base)
library(utils)
library(seasonal)
library(dplyr)

   # Criando uma função do R:
   # Função será rseas(ts), terá como imput uma time series e vai cuspir
   # uma outra time series com o dado dessazonalizado.
   # Dessazonalização será PADRÃO: utilizará o carnaval, mas vai deixar
   # o modelo em aberto para o programa selecionar o melhor fit e retirar
   # outliers.

ajuste_sazonal = function(ts){
  
  # Pega o arquivo de carnaval
  carnaval = read.delim("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Atividade/Dessazonalizacao/X12/carnaval.txt",
                       sep = "", header = FALSE)
  
  seg = ts(carnaval$V3, start=1990, frequency = 12)
  ter = ts(carnaval$V4, start=1990, frequency = 12)
  qua = ts(carnaval$V5, start=1990, frequency = 12)
  qui = ts(carnaval$V6, start=1990, frequency = 12)
  sex = ts(carnaval$V7, start=1990, frequency = 12)
  sab = ts(carnaval$V8, start=1990, frequency = 12)

  ts_sa = seas(ts, regression.aictest = NULL, xreg = cbind(seg,ter,qua,qui,sex,sab),
               regression.usertype = "td")$data[,"seasonaladj"]
  return(ts_sa)}

sazonalidade = function(ts){
  
  # Pega o arquivo de carnaval
  carnaval = read.delim("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Atividade/Dessazonalizacao/X12/carnaval.txt",
                        sep = "", header = FALSE)
  
  seg = ts(carnaval$V3, start=1990, frequency = 12)
  ter = ts(carnaval$V4, start=1990, frequency = 12)
  qua = ts(carnaval$V5, start=1990, frequency = 12)
  qui = ts(carnaval$V6, start=1990, frequency = 12)
  sex = ts(carnaval$V7, start=1990, frequency = 12)
  sab = ts(carnaval$V8, start=1990, frequency = 12)
  
  ts_sa = seas(ts, regression.aictest = NULL, xreg = cbind(seg,ter,qua,qui,sex,sab),
               regression.usertype = "td")$data[,"seasonal"]
  return(ts_sa)}

#############################################################################################

ajuste_sazonal_df = function(df){
  new_df <- df; new_df[,-1] <- NA
  st <- head(df$datas, 1) %>% as.Date
  ed <- tail(df$datas, 1) %>% as.Date

  for (i in 2:ncol(df)){ 
    new_df[,i] <- ts(as.matrix(df[,i]), start = c(year(st), month(st)), 
                             end = c(year(ed), month(ed)), frequency = 12) %>% ajuste_sazonal }
  
  names(new_df)[-1] <- paste0(names(df)[-1],"_dessaz")

  return(new_df)}

# ESTA CAGADO
sazonalidade_df = function(df){
  new_df <- df; new_df[,-1] <- NA
  st <- head(df$datas, 1) %>% as.Date
  ed <- tail(df$datas, 1) %>% as.Date
  
  for (i in 2:ncol(df)){ 
    new_df[,i] <- ts(as.matrix(df[,i]), start = c(year(st), month(st)), 
                     end = c(year(ed), month(ed)), frequency = 12) %>% sazonalidade }
  
  names(new_df)[-1] <- paste0(names(df)[-1],"_saz")
  
  return(new_df)}