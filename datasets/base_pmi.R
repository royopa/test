setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1998/1/1"), as.Date("2018/9/1"), by = "quarter")
#### PMI Manufacturing (MCM)
pmi <- as.data.frame(read_excel("INTPMI0.xls", sheet = "Indústria", skip = 9))
names(pmi) <- c("date", "pmi_global", "pmi_euro", "pmi_brasil", "pmi_china", "pmi_franca", 
                "pmi_alemanha", "pmi_italia", "pmi_japao", "pmi_uk", "pmi_us")
for (i in 2:dim(pmi)[2]){
  pmi[which(pmi[,i] == "<NA>"),i] <- 0
  pmi[,i] <- as.numeric(pmi[,i])}
pmi$date <- seq(as.Date("1998/1/1"), as.Date("2018/10/1"), by = "month")
pmi <- pmi[which(pmi$date %in% t), ]