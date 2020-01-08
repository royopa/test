library(readxl)
library(lubridate)
library(dplyr)
#### Nome "ÍNDICE de PRECOS ao CONSUMIDOR AMPLO"
#### Origem IBGE
#### codigo: "IPCA_base_var.csv",  "IPCA_base_peso.csv"

readbase_ipca = function(itens, day = 28, var=TRUE, tri=FALSE, initial.date = "1996-01-01"){
  path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/1.IPCA/"
  
  #### Incluindo um chave para coletar todos os itens disponíveis na base
  if (itens == "all"){itens <- 1000000:10000000}
  
  #### Escolhendo a data de fechamento da coleta do IPCA
  if (length(day) != 1) 
    stop("choose one day for IPCA collection (15, 28) or if you want them all ('all') ")
  
  #### Escolhendo entre a base de pesos e a base de variacoes
  if (var == TRUE){ipca <- read_excel(paste0(path_data,"bases/IPCA_base_var.xlsx")) %>% as.data.frame
  } else {         ipca <- read_excel(paste0(path_data,"bases/IPCA_base_peso.xlsx")) %>% as.data.frame}
  names(ipca)[1] <- "cods"

  #### Guardando as datas para construir o data.frame
  dts <- names(ipca)[-1] %>% as.numeric %>% as.Date(origin="1899-12-31") %>% as.character
 
  #### Selecionando os itens da base a serem coletados
  itens <- intersect(ipca$cods, itens)
  df <- as.data.frame(cbind(dts, t(ipca[which(ipca$cods %in% itens), -1])))
  for (i in 1:ncol(df)){
    if (i == 1){ df[,i] <- df[,i] %>% as.character 
    } else { df[,i] <- df[,i] %>% as.character %>% as.numeric } }
  
  #### Formatando o output
  rownames(df) <- seq(nrow(df))
  names(df) <- c("datas", paste0("cod", itens))
  df <- df[which(as.character(df$datas) > initial.date), ]
  
  #### Padronizando as datas do data.frame
  if (is.numeric(day)){
    df <- df[day(df$datas) == day, ]
    df$datas <- as.Date(df$datas); day(df$datas) <- 1
    df$datas <- df$datas %>% as.character}
  
  #### Excluindo as colunas que possuem apenas NAs
  df <- df[, lapply(df, function(x){ length(which(!is.na(x)))}) %>% unlist != 0]
  
  #### Escolhendo se queremos os dados trimestrais ou mensais
  if (tri == TRUE & var == TRUE){
    ac3m <- df;  ac3m[,-1] <- NA
    for (i in 3:nrow(ac3m)){  
      if (ncol(ac3m) == 2){ac3m[i,-1] <- 100*(prod(1 + df[c((i-2):i), -1]/100) -1)
      } else if (ncol(ac3m) > 2){
        ac3m[i,-1] <- 100*(apply(df[c((i-2):i), -1], 2, function(x){prod(1+x/100)}) -1)} }
    
    df <- ac3m[month(ac3m$datas) %in% c(3,6,9,12), ]
    
  } else if (tri == TRUE & var == FALSE){
    ac3m <- df;  ac3m[,-1] <- NA
    for (i in 3:nrow(ac3m)){  
      if (ncol(ac3m) == 2){ac3m[i,-1] <- mean(df[c((i-2):i), -1])
      } else if (ncol(ac3m) > 2){
        ac3m[i,-1] <- apply(df[c((i-2):i), -1], 2, mean) -1} } 
    
    df <- ac3m[month(ac3m$datas) %in% c(3,6,9,12), ]}
    
  return(df)}