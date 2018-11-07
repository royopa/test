setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("2003/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Sondagem Industrial CNI
cni <- as.data.frame(read_excel("ATVCNI7.xls", sheet = "Dados Dessazonalizados", skip = 1))
names(cni) <- c("date", "fat_real", "emp", "horas_trab", "massa_sal", 
                "rend_med", "uci")
cni <- cni[1:(which(cni[,1] == "MÉDIAS")-1),]
for (i in 2:dim(cni)[2]){
            cni[which(cni[,i] == "-"),i] <- 0
            cni[,i] <- as.numeric(cni[,i])}
cni$date <- seq(as.Date("2003/1/1"), as.Date("2018/8/1"), by = "month")
cni <- cni[which(cni$date %in% t), ]