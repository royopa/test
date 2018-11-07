setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1974/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Selic
selic <- as.data.frame(read_excel("MFIJURO0.xls", sheet = "Selic", skip = 2))
names(selic) <- c("date", "selic_var_mes", "selic_aa", "dus", "selic_copom")
selic <- selic[1:(which(selic[,1] == "ANO")-1),]
for (i in 1:dim(selic)[2]){
  selic[which(selic[,i] == "-"),i] <- 0
  selic[,i] <- as.numeric(selic[,i])  }
selic$date <- seq(as.Date("1974/1/1"), as.Date("2018/9/1"), by = "month")
selic <- selic[which(selic$date %in% t), ]
