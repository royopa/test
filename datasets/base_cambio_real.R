setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1994/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Taxa de Câmbio Nominal
camb_real <- as.data.frame(read_excel("SEXCBRE0.xls", sheet = "Câmbio Real-cesta 19 paises", skip = 1))
names(camb_real) <- c("date", "cambr_ipca", "cambr_ipc", "cambr_ipa")
camb_real <- camb_real[1:(which(camb_real[,1] == "MÉDIA NO ANO (BASE: JUN/94 = 100)")-1),]
for (i in 2:dim(camb_real)[2]){
            camb_real[,i] <- as.numeric(camb_real[,i])}
camb_real$date <- seq(as.Date("1994/1/1"), as.Date("2018/9/1"), by = "month")
camb_real <- camb_real[which(camb_real$date %in% t), ]
