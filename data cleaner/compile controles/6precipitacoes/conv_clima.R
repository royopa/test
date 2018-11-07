#install.packages("readstata13")
library(readstata13)

rm(list=ls())
setwd("E:/Dissertacao/DADOS/")

rain <- read.dta13("Controles/Clima/base_clima_datasus2010.dta")
rain <- rain[rain$ano > 2003 & rain$mes == 12, 1:13]
rain <- rain[,c(2,5,11,12,13)]
names(rain) <- c("cod_mun","ano","last12","mean","sd")

rain$v_rain <- log(1 + rain$last12) - log(1 + rain$mean)
if (rain$last12 < rain$mean - rain$sd) {rain$d_rain <- 1} else {rain$d_rain <- 0}

rain <- rain[,c(1,2,6,7)]

write.csv(rain, "base_rain.csv", row.names=FALSE)
