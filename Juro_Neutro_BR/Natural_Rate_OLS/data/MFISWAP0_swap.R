library(readxl)
library(lubridate)
library(dplyr)

#### Swap Pre Di
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

swap <- as.data.frame(read_excel(paste0(path_data,"MCM/MFISWAP0.xls"), 
                                 sheet = "Swap Pré-DI", skip = 2))
names <- c("datas", "swap30_med", "swap30_end", "swap60_med", "swap60_end", 
               "swap90_med", "swap90_end", "swap180_med", "swap180_end", 
               "swap360_med", "swap360_end")

names(swap) <- names

swap <- swap[2:(which(swap[,1] == "ANO")-1),]

for (i in 2:ncol(swap)){
  swap[which(swap[,i] == "-"),i] <- 0;    swap[which(swap[,i] == "nd"),i] <- 0
  swap[which(swap[,i] == "<NA>"),i] <- 0; swap[is.na(swap[,i]),i] <- 0
  swap[,i] <- as.numeric(swap[,i])}

swap$datas <- swap$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
