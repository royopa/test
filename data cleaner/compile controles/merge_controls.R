#install.packages("foreign")
library(foreign)
rm(list=ls())
setwd("E:/Dissertacao/Dados/")

### Loding datasets
psf <- read.csv(file ="04.Controles/base_PSF.csv", header=TRUE, sep=",")
tse <- read.csv(file ="04.Controles/base_tse.csv", header=TRUE, sep=",")

bndes_auto <- read.csv(file ="04.Controles/base_ops_auto.csv", header=TRUE, sep=",")
bndes_nauto <- read.csv(file ="04.Controles/base_ops_nauto.csv", header=TRUE, sep=",")

ano <- 2004:2016
cod_mun <- rep(unique(psf$cod_mun), times =length(ano))
ano <- rep(ano, each =length(unique(cod_mun)))
bal <- data.frame(cod_mun, ano)

base <- merge(bal,bndes_auto, by= c("cod_mun","ano"), all.x=TRUE)
base <- merge(base,bndes_nauto, by= c("cod_mun","ano"), all.x=TRUE)
names(base) <- c("cod_mun","ano","ops_auto","ops_nauto")
base$ops_auto[is.na(base$ops_auto)] <- 0
base$ops_nauto[is.na(base$ops_nauto)] <- 0

base <- merge(base,psf, by= c("cod_mun","ano"))
base <- merge(base,tse, by= c("cod_mun","ano"), all.x=TRUE)

base <- base[!duplicated(base), ]

write.csv(base, "base_controls.csv", row.names=FALSE)
