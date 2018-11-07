setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("2001/1/1"), as.Date("2018/9/1"), by = "quarter")
#### ÍNDICES de CONFIANÇA do PRODUTOR (FGV)
conf <- as.data.frame(read_excel("ATVFGV13.xls", sheet="Indústria", skip = 2))
conf <- conf[1:(which(conf[,1] == "Nome da Série: Sondagem da Indústria - FGV")-2),]
names(conf) <- c("date", "ind_conf_dsz", "ind_atual_dsz", "ind_expec_dsz",
                 "ind_conf_saz", "ind_atual_saz", "ind_expec_saz", 
                 "nuci_dsz", "nuci_saz")
conf$date <- seq(as.Date("2001/1/1"), as.Date("2018/10/1"), by = "month")
conf <- conf[which(conf$date %in% t), ]