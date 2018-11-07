setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1953/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Taxa de Câmbio Nominal
camb <- as.data.frame(read_excel("MFIPTAX0.xls", sheet = "Câmbio - Mensal (val. corrente)", skip = 2))
#### Warning messages:
#### 1: In read_fun(path = path, sheet_i = sheet, limits = limits, shim = shim,  :
####                  Expecting numeric in C862 / R862C3: got a date
names(camb) <- c("date", "camb_comp_end", "camb_vend_end", "camb_comp_med", "camb_comp_med")
camb <- camb[1:(which(camb[,1] == "ANO")-1),]
for (i in 2:dim(camb)[2]){
  camb[,i] <- as.numeric(camb[,i])}
camb$date <- seq(as.Date("1953/1/1"), as.Date("2018/9/1"), by = "month")
camb <- camb[which(camb$date %in% t), ]