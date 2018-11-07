setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1946/7/1"), as.Date("2018/9/1"), by = "quarter")
#### Índice de Preços de Commodities Internacional (Índice CRB)
crb_oil <- as.data.frame(read_excel("SETCOM0.xls", sheet = "Petroleo e Derivados", skip = 2))
names(crb_oil) <- c("date", "brent_oil_dol", "brent_oil_brl", "wt_int_dol", "wt_int_brl", "gc_gas_dol", 
                "gc_gas_brl", "diesel_dol", "diesel_brl", "nafta_oil_dol", "nafta_oil_brl",
                "gnv_dol", "gnv_brl", "oil_comb_dol", "oil_comb_brl")
crb_oil <- crb_oil[1:(which(crb_oil[,1] == "MÉDIAS ANUAIS")-1),]
for (i in 1:dim(crb_oil)[2]){
  crb_oil[which(crb_oil[,i] == "nd"),i] <- 0
  crb_oil[,i] <- as.numeric(crb_oil[,i])}
crb_oil$date <- seq(as.Date("1946/1/1"), as.Date("2018/9/1"), by = "month")
crb_oil <- crb_oil[which(crb_oil$date %in% t), ]