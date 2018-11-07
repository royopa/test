#install.packages("foreign")
library(foreign)
rm(list=ls())
setwd("E:/Dissertacao")

### Loding datasets
pbf <- read.csv(file ="DADOS/base_pbf.csv", header=TRUE, sep=",")
pib <- read.csv(file ="DADOS/pib10.csv", header=TRUE, sep=";", dec=",")
pib <- pib[,c("cod_mun","pibpc2010")]
emp <- read.csv(file="DADOS/base_RAIS.csv",header = TRUE, sep=",")
cods <- read.csv(file ="DADOS/base_cods.csv", header=TRUE, sep=";", dec=",")

bndes_auto <- read.csv(file ="DADOS/04.Controles/base_ops_auto.csv", header=TRUE, sep=",")
bndes_nauto <- read.csv(file ="DADOS/04.Controles/base_ops_nauto.csv", header=TRUE, sep=",")

### Rebalanceando base BNDES
ano <- 2004:2016
cod_mun <- rep(unique(cods$cod_mun), times =length(ano))
ano <- rep(ano, each =length(unique(cod_mun)))
bal <- data.frame(cod_mun, ano)
bndes <- merge(bal,bndes_auto, by= c("cod_mun","ano"), all.x=TRUE)
bndes <- merge(bndes,bndes_nauto, by= c("cod_mun","ano"), all.x=TRUE)
names(bndes) <- c("cod_mun","ano","ops_auto","ops_nauto")
bndes$ops_auto[is.na(bndes$ops_auto)] <- 0
bndes$ops_nauto[is.na(bndes$ops_nauto)] <- 0
bndes$ops_bndes <- bndes$ops_auto + bndes$ops_nauto
bndes <- bndes[,c("cod_mun","ano","ops_bndes")]

### Merging datasets
base <- merge(pbf, emp, by=c("cod_mun","ano"))
base <- merge(base, bndes, by=c("cod_mun","ano"))
base <- merge(base, pib, by=c("cod_mun"))
base <- merge(base, cods, by=c("cod_mun"))

### Reordering variables
facs <- c("cod_mun","ano","re","uf","meso","micro","cod_ibge","pop")
other <- names(base)[!(names(base) %in% facs)]
base <- base[, c(facs, other)]

base = base[order(base$cod_mun,base$ano),]
base <- base[!duplicated(base[,1:2]), ]

write.csv(base, "BASES/BNDES_base.csv", row.names=FALSE)
#write.dta(base, "STATA/BNDES_base.dta")