library(readxl)
library(lubridate)
#### Selic
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

selic <- as.data.frame(read_excel(paste0(path_data,"MCM/MFIJURO0.xls"), 
                                  sheet = "Selic", skip = 2))

names <- c("datas", "selic_var_mes", "selic_aa", "dus", "selic_copom")
names(selic) <- names

selic <- selic[1:(which(selic[,1] == "ANO")-1),]

for (i in 1:dim(selic)[2]){
  selic[which(selic[,i] == "-"),i] <- 0;    selic[which(selic[,i] == "nd"),i] <- 0
  selic[which(selic[,i] == "<NA>"),i] <- 0; selic[is.na(selic[,i]),i] <- 0
  selic[,i] <- as.numeric(selic[,i])}

selic$datas <- as.Date(selic$datas, origin="1899-12-30")