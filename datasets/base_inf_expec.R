setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("2001/1/1"), as.Date("2018/9/1"), by = "quarter")

#### Expectativa de Inflação do FOCUS suavizada (BCB)
ipca_exp_sm <- as.data.frame(read_excel("History Infl Expec (smoothed).xls", 
                                        sheet = "Sheet1"))
for (i in 2:dim(ipca_exp_sm)[2]){ipca_exp_sm[,i] <- as.numeric(ipca_exp_sm[,i])}
ipca_exp_sm$date <- as.Date(ipca_exp_sm$date)
ipca_exp_sm$ind <- 0
for (i in 2:dim(ipca_exp_sm)[1]){
  if (month(ipca_exp_sm$date)[i] != month(ipca_exp_sm$date)[i-1]){
    ipca_exp_sm$ind[i] <- 1}}
ipca_exp_sm <- ipca_exp_sm[ipca_exp_sm$ind ==1, ]
ipca_exp_sm$date <- seq(as.Date("2002/1/1"), as.Date("2018/10/1"), by = "month")
ipca_exp_sm <- ipca_exp_sm[which(ipca_exp_sm$date %in% t), c("date", "ipca_exp_sm")]

#### Expectativa de Inflação do FOCUS (BCB)
ipca_exp <- as.data.frame(read_excel("History Infl Expec (non smoothed).xls", 
                                     sheet = "Sheet1"))
for (i in 2:dim(ipca_exp)[2]){ipca_exp[,i] <- as.numeric(ipca_exp[,i])}
ipca_exp$date <- as.Date(ipca_exp$date)
ipca_exp$ind <- 0
for (i in 2:dim(ipca_exp)[1]){
  if (month(ipca_exp$date)[i] != month(ipca_exp$date)[i-1]){
    ipca_exp$ind[i] <- 1}}
ipca_exp <- ipca_exp[ipca_exp$ind ==1, ]
ipca_exp$date <- seq(as.Date("2001/12/1"), as.Date("2018/10/1"), by = "month")
ipca_exp <- ipca_exp[which(ipca_exp$date %in% t), c("date", "ipca_exp")]