library(readxl)
library(lubridate)
library(dplyr)

path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

termos <- as.data.frame(read_excel(paste0(path_data,"MCM/SEXQTUM0.xls"), 
                                sheet = "Termos de troca", skip = 1))
nms <- c("datas", "ind_termos")
names(termos) <- nms

termos <- termos[1:(which(termos[,1] == "Nome da Série: Índices de Preços e Quantum de Exportação") -2),]

for (i in 2:ncol(termos)){
  termos[which(termos[,i] == "-"),i] <- 0;    termos[which(termos[,i] == "nd"),i] <- 0
  termos[which(termos[,i] == "<NA>"),i] <- 0; termos[is.na(termos[,i]),i] <- 0
  termos[,i] <- as.numeric(termos[,i])}

termos$datas <- termos$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
