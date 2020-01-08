library(readxl)
library(dplyr)
library(lubridate)

#### ÍNDICES de CONFIANÇA do PRODUTOR (FGV)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

conf <- as.data.frame(read_excel(paste0(path_data,"MCM/ATVFGV13.xls"), 
                                 sheet="Indústria", skip = 2))

nms <- c("datas", "ind_conf_dsz", "ind_atual_dsz", "ind_expec_dsz", "ind_conf_saz", "ind_atual_saz", 
         "ind_expec_saz", "nuci_dsz", "nuci_saz")
names(conf) <- nms

conf <- conf[1:(which(conf[,1] == "Nome da Série: Sondagem da Indústria - FGV")-2),]

for (i in 2:ncol(conf)){
  conf[which(conf[,i] == "-"),i] <- 0;    conf[which(conf[,i] == "nd"),i] <- 0
  conf[which(conf[,i] == "<NA>"),i] <- 0; conf[is.na(conf[,i]),i] <- 0
  conf[,i] <- as.numeric(conf[,i])}

conf$datas  <- conf$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
