setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1981/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Índice de Preços de Commodities Internacional (Índice CRB)
crb <- as.data.frame(read_excel("SETCOM0.xls", sheet = "CRB Spot", skip = 2))
names(crb) <- c("date", "crb_dol", "crb_brl", "crb_oil_dol", "crb_oil_brl", "crb_food_dol", 
                "crb_food_brl", "crb_lstock_dol", "crb_lstock_brl", "crb_metals_dol", 
                "crb_metals_brl", "crb_ind_dol", "crb_ind_brl", "crb_text_dol", "crb_text_brl")
crb <- crb[1:(which(crb[,1] == "MÉDIAS ANUAIS")-1),]
for (i in 1:dim(crb)[2]){crb[,i] <- as.numeric(crb[,i])}
crb$date <- seq(as.Date("1981/5/1"), as.Date("2018/9/1"), by = "month")
crb <- crb[which(crb$date %in% t), ]