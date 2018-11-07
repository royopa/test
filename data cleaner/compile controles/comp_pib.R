#install.packages("readxl")
library(readxl)

rm(list=ls())
setwd("E:/Dissertacao/DADOS/04.Controles/02.PIB(02-15)")

p1 <- read_xls("pib02_15.xls", sheet = 1)
p2 <- read_xls("pib02_15.xls", sheet = 2)

base <- as.data.frame(rbind(p1, p2))

base <- base[, c("cod_munic","ano","agro","ind","serv","apu","impostos","pib")]
names(base) <- c("cod_mun","ano","pib_agro","pib_ind","pib_serv","pib_ap","impostos","pib_tot")
base$cod_mun <- trunc(as.numeric(base$cod_mun)/10,0)
write.csv(base, "base_pib.csv", row.names= FALSE)
             