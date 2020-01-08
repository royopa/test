library(readxl)
library(lubridate)
library(dplyr)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/AUX_df_filler.R", echo=TRUE)
#### Nome "MONITOR DE PREÇOS - FGV"
#### Origem PORTAL
#### codigo: "FGV_base_media.xlsx",  "FGV_base_ponta.xlsx"

readbase_monitor = function(itens, media=TRUE, end=FALSE, last=FALSE, tri=FALSE, 
                            initial.date="2012-01-01"){
  path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/3.MonitorFGV/"
  initial_date <- as.Date(initial.date, format="%Y-%m-%d")
  
  #### Incluindo um chave para coletar todos os itens disponíveis na base
  if (itens == "all"){itens <- 1000000:10000000}
  
  if (media == TRUE){  
    monitor <- read_excel(paste0(path_data, "bases/FGV_base_media.xlsx"))[,-2] %>% as.data.frame
  } else {             
    monitor <- read_excel(paste0(path_data, "bases/FGV_base_ponta.xlsx"))[,-2] %>% as.data.frame}

  #### Guardando as datas para construir o data.frame
  dts <- names(monitor)[-1] %>% as.Date(format="%d/%m/%Y") %>% as.character
  names(monitor)[1] <- "cods"
  
  #### Selecionando os itens da base a serem coletados
  itens <- intersect(monitor$cods, itens)
  df <- as.data.frame(cbind(datas=dts, t(monitor[which(monitor$cods %in% itens), -1])))
  for (i in 1:ncol(df)){
    if (i == 1){ df[,i] <- gsub(",", ".", df[,i] %>% as.character) 
    } else {     df[,i] <- gsub(",", ".", df[,i] %>% as.character) %>% as.numeric } }
  
  #### Formatando o output
  rownames(df) <- seq(nrow(df))
  names(df)    <- c("datas", paste0("cod", itens))
  df           <- df[which(as.character(df$datas) > initial.date), ]

  #### Preenchendo o data.frame para as datas faltantes
  fill_dates <- data.frame(datas = seq(from=as.Date(head(df$datas, 1)), 
                                       to=as.Date(tail(df$datas, 1)), by="day"))
  fill_dates$datas <- fill_dates$datas %>% as.character
  df <- merge(fill_dates, df, by=c("datas"), all=TRUE)
  df <- df_filler(df)
  
  #### Coletando apenas os valores de fim de mes
  if (end == TRUE){
    cut_dates <- read.csv("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/cut_dates_ipca.csv")[,3]
    cut_dates <- cut_dates %>% as.character
    #### Verificando se o arquivo de datas de coleta do IPCA esta atualizado
    if (tail(cut_dates,1) < today()) 
      stop("update IPCA collection dates file or choose last=TRUE to pick the end of the month information")
    #adiciono o vetor c(FALSE, TRUE) para coletar apenas os elementos em posicao par do vetor
    df <- df[which(df$datas %in% cut_dates[c(FALSE, TRUE)]), ]
    df$datas <- as.Date(df$datas); day(df$datas) <- 1
  } else if (last == TRUE){ 
    ids <- which(month(df$datas[-nrow(df)]) < month(df$datas[-1]))
    df <- df[ids, ]
    df$datas <- as.Date(df$datas); day(df$datas) <- 1}

  #### Acumulando no trimestre
  if (tri == TRUE & (end == TRUE | last == TRUE)){
    ac3m <- df;  ac3m[,-1] <- NA
    for (i in 3:nrow(ac3m)){  
      if (ncol(ac3m) == 2){ac3m[i,-1] <- 100*(prod(1 + df[c((i-2):i), -1]/100) -1)
      } else if (ncol(ac3m) > 2){
        ac3m[i,-1] <- 100*(apply(df[c((i-2):i), -1], 2, function(x){prod(1+x/100)}) -1)} }
      
    df <- ac3m[month(ac3m$datas) %in% c(3,6,9,12), ]  } 
  
  return(df)}
