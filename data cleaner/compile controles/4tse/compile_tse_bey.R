#install.packages("foreign")
#install.packages("readstata13")
#install.packages("dplyr"")

library(dplyr)
library(reshape2)
rm(list=ls())
setwd("E:/Dissertacao/DADOS/04.Controles")

data <- read.csv(file ="04.RDEleitorais(05-18)/vote_mayor_bey.csv", header=TRUE, sep=",")
data <- data[data$round_description == "ELEITO", c(1,4,7)]
names(data) <- c("ano","cod_mun","part")
data$cod_mun <- floor(data$cod_mun/10)

data$mpart <- 0
data$mpart[which(data$part == "PT")] <- 1
data <- data[order(data$ano),]
base1 <- base2 <- base3 <- data
base1$ano <- base1$ano + 1
base2$ano <- base2$ano + 2
base3$ano <- base3$ano + 3

base <- rbind(data,base1,base2,base3)
base$ano <- base$ano +1

write.csv(base, "base_tse_bey.csv", row.names=FALSE)
