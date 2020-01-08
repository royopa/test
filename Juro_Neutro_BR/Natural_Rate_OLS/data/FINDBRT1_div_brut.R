library(readxl)
library(dplyr)
library(lubridate)

#### Divida Bruta Bacen (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

div <- as.data.frame(read_excel(paste0(path_data,"MCM/FINDBRT1.xls"), sheet="Dívida líquida em % do PIB", skip=1))
dts <- names(div)[-1] %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
div <- div[10, ]# %>% as.vector

#div2 <- as.data.frame(read_excel(paste0(path,"Data/FINDBRT1.xls"), sheet="DBGG (antiga_%PIB)", skip=1))
#dts2 <- names(div2)[-1] %>% as.numeric %>% as.Date(origin="1899-12-31")
#div2 <- div2[which(div2[,1] == "Dívida bruta do governo geral (B)"), ]

div <- div[-1] %>% t %>% as.data.frame 
names(div) <- "div_brut"; div$datas <- dts
div$div_brut <- div$div_brut %>% as.character %>% as.numeric
div <- div[,c("datas", "div_brut")]