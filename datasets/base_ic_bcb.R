setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1998/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Índice de Commodities Brasil
ic_bcb <- as.data.frame(read_excel("SETICBR0.xls", sheet = "IC-Br (nova metodologia)", skip = 3))
names(ic_bcb) <- c("date", "icbr", "icbr_agro", "icbr_metal", "icbr_energia")
ic_bcb <- ic_bcb[1:(which(ic_bcb[,1] == "Cotações em R$ (média mensal)")-2),]
ic_bcb$date <- seq(as.Date("1998/1/1"), as.Date("2018/9/1"), by = "month")
ic_bcb <- ic_bcb[which(ic_bcb$date %in% t), ]