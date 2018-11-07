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
psf <- read.csv(file ="DADOS/04.Controles/base_PSF.csv", header=TRUE, sep=",")

### Merging datasets
base <- merge(pbf, emp, by=c("cod_mun","ano"))
base <- merge(base, psf, by=c("cod_mun","ano"))
base <- merge(base, pib, by=c("cod_mun"))
base <- merge(base, cods, by=c("cod_mun"))

### Reordering variables
facs <- c("cod_mun","ano","re","uf","meso","micro","cod_ibge","pop")
other <- names(base)[!(names(base) %in% facs)]
base <- base[, c(facs, other)]

base = base[order(base$cod_mun,base$ano),]
base <- base[!duplicated(base[,1:2]), ]

write.csv(base, "BASES/PSF_base.csv", row.names=FALSE)
#write.dta(base, "STATA/PSF_base.dta")