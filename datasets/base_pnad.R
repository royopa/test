setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1998/1/1"), as.Date("2018/9/1"), by = "quarter")
#### DESEMPREGO PNAD (Serie retroagida MCM)
pnad <- as.data.frame(read_excel("ATVMCM4.xls", sheet="pnad_dessaz", skip = 2))
pnad <- pnad[1:(which(pnad[,1] == "Nome da Série: Séries Retroagidas PNAD Contínua")-1),]
names(pnad) <- c("date", "pes_ocup", "pea", "tx_desemp", "pia", "massa_sal")
pnad$date <- seq(as.Date("1998/1/1"), as.Date("2018/9/1"), by = "month")
pnad <- pnad[which(pnad$date %in% t), ]