library(readxl)
library(lubridate)

#### Expectativa de Inflação do FOCUS suavizada (BCB)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/" 

ipca_exp_sm <- as.data.frame(
               read_excel(paste0(path_data,"Data/History Infl Expec (smoothed).xls"), 
                          sheet = "Sheet1"))
names <- c("data", "ipca_exp_sm")
names(ipca_exp_sm) <- names

ipca_exp_sm$ipca_exp_sm <- as.numeric(ipca_exp_sm$ipca_exp_sm)
ipca_exp_sm$ind         <- 0

per <- strsplit(as.character(ipca_exp_sm$data), "/")

ipca_exp_sm$dia <- 1
ipca_exp_sm$mes <- lapply(per,"[[",2) %>% unlist %>% as.numeric
ipca_exp_sm$ano <- lapply(per,"[[",3) %>% unlist %>% as.numeric

for (i in 2:nrow(ipca_exp_sm)){  if (ipca_exp_sm$mes[i] != ipca_exp_sm$mes[i-1]) {ipca_exp_sm$ind[i] <- 1}  }

ipca_exp_sm <- ipca_exp_sm[ipca_exp_sm$ind ==1, ]

ipca_exp_sm$datas <- as.Date(paste0(ipca_exp_sm$ano,"-",ipca_exp_sm$mes,"-",ipca_exp_sm$dia)) %>% as.character
