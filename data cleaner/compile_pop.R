#install.packages("reshape")
library(reshape)

rm(list=ls())
setwd("E:/Dissertacao/Dados")

pop1 <- read.csv(file="03.Populacao/pop92_17.csv", 
                 header=TRUE, sep=";", dec = ",")
pop1$X2007 <- trunc(rowMeans(pop1[,c("X2006","X2008")]))
pop1$X2010 <- trunc(rowMeans(pop1[,c("X2009","X2011")]))
pop1 <- pop1[,c("codigo","X2002","X2003","X2004","X2005","X2006","X2007",
                "X2008","X2009","X2010","X2011","X2012","X2013","X2014",
                "X2015","X2016","X2017")]
pop <- melt(pop1, id.vars = c("codigo"))
names(pop) <- c("cod_mun","ano","pop")
pop[,2] <- as.numeric(sub("X","",pop[,2]))
pop$cod_mun <- trunc(pop$cod_mun/10) 

pop <- pop[-which(is.na(pop[,3])=="TRUE"),]

write.csv(pop, "base_pop.csv", row.names=FALSE)