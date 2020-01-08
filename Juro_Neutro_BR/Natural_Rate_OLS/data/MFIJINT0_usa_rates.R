library(readxl)
library(dplyr)
library(lubridate)

#### Treasury 10yr (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
usa_rates <- as.data.frame(read_excel(paste0(path_data,"MCM/MFIJINT0.xls"), sheet="EUA", skip=2))
usa_rates <- usa_rates[1:(which(usa_rates[,1]=="Nome da Série: Taxas de juros dos EUA")-2), ]

nms <- c("datas", "fed_funds_eff", "fed_funds_targ_med", "libor_1m", "libor_3m", "libor_6m", "libor_12m", 
         "prime_rate", "ty2yr", "ty5yr", "ty10yr", "ty30yr", "fed_funds_targ_end")

names(usa_rates) <- nms

for (i in 2:dim(usa_rates)[2]){
  usa_rates[which(usa_rates[,i] == "-"),i] <- 0;    usa_rates[which(usa_rates[,i] == "nd"),i] <- 0
  usa_rates[which(usa_rates[,i] == "<NA>"),i] <- 0; usa_rates[is.na(usa_rates[,i]),i] <- 0
  usa_rates[,i] <- as.numeric(usa_rates[,i])}

usa_rates$datas <- usa_rates$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
