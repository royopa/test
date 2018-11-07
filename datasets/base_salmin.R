setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1940/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Salário Mínimo
salm <- as.data.frame(read_excel("ATVMTB1.xls", sheet = "Salário Mínimo", skip = 1))
names(salm) <- c("date", "unit", "sm_moeda_corrente", "sm_brl", "sm_usd", "tx_camb")
salm <- salm[1:(which(salm[,1] == "MÉDIAS ANUAIS")-1),]
for (i in 3:dim(salm)[2]){
            salm[which(salm[,i] == "-"),i] <- 0
            salm[,i] <- as.numeric(salm[,i])}
salm$date <- seq(as.Date("1940/1/1"), as.Date("2018/9/1"), by = "month")
salm <- salm[which(salm$date %in% t), ]