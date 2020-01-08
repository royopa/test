library(readxl)
library(dplyr)
library(lubridate)

#EXEMPLO
#plan = "ATVMCM4.xls"
#sheet="pnad_dessaz"
#skip_lines =1
#names <- c("pes_ocup", "pea", "tx_desemp", "pia", "massa_sal")

readbase_MCM = function(plan, sheet, skip_lines, cols, names=c(), 
                        tri=FALSE, initial_date="1996-01-01"){
  path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/"
  
  #### Verificando se a coluna de datas foi inputada nas variáveis selecionadas
  if (!(1 %in% cols)) stop("the first column (dates) must be included in the data.fame")
  
  #### Verificando se as colunas desejadas tem a mesma dimensao dos nomes inputados  
  if (length(cols) != length(names)) 
    stop("length of cols variable must equal to the number of names inputed")
  
  #### Importando os dados e selecionando as variáveis de interesse
  df <- as.data.frame(read_excel(paste0(path_data,"MCM/", plan), 
                                 sheet=sheet, skip=skip_lines))[,cols]
  names(df) <- names
  
  #### Cortando o data.frame ate a ultima data disponivel
  for (i in 1:nrow(df)){if (df$datas[i+1] %>% as.character %>% as.numeric %>% is.na) break}
  #Warning message:
  #  In function_list[[i]](value) : NAs introduced by coercion
  df <- df[1:i,]
  
  #### Corrigindo as dados da MCM
  for (i in 2:ncol(df)){
    df[which(df[,i] == "-"),i] <- 0;    df[which(df[,i] == "nd"),i] <- 0
    df[which(df[,i] == "<NA>"),i] <- 0; df[is.na(df[,i]),i] <- 0
    df[,i] <- as.numeric(df[,i])}
  
  #### Uniformizando a coluna de datas, ordenando e coletando apenas as datas de interesse
  df$datas <- df$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
  df       <- df[order(df$datas),]; rownames(df)     <- seq(nrow(df))
  df       <- df[which(df$datas >= initial_date), ]
  
  #### Chave que coleta informações de fim de trimestre apenas
  if (tri == TRUE){df <- df[which(month(df$datas) %in% c(3,6,9,12)), ]}

  return(df)}