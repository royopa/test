library(readxl)
library(dplyr)
library(lubridate)

#### USA - Indicadores (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
usa_ind <- as.data.frame(read_excel(paste0(path_data,"MCM/INTEUA00.xls"), sheet="Inflação - mensal", skip=3))
usa_ind <- usa_ind[1:(which(usa_ind[,1]=="Nome da Série: EUA - Inflação")-2), ]

names <- c("datas", "cpi", "cpi_core", "ppi", "ppi_core", "pce_core", "pce_deflator")
names(usa_ind) <- names

for (i in 2:ncol(usa_ind)){
  usa_ind[which(usa_ind[,i] == "-"),i] <- 0;    usa_ind[which(usa_ind[,i] == "nd"),i] <- 0
  usa_ind[which(usa_ind[,i] == "<NA>"),i] <- 0; usa_ind[is.na(usa_ind[,i]),i] <- 0
  usa_ind[,i] <- as.numeric(usa_ind[,i])}

usa_ind$datas <- usa_ind$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character