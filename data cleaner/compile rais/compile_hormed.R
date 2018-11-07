rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- 8

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
              header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "hor_setrem_")
i<-1
for (i in 1: length(datafiles)){
  hor <- read.csv(file=paste0(dataplace,datafiles[i]), 
                  skip =2, header=TRUE, sep=";", dec = ",")
  hor <- hor[,c(1, grep("Total",names(hor)))]
  hor <- hor[1:(which(hor[,1] == "Total")-1), (1:(n_class+1))]
  names(hor) <- c("nome",
                  paste0(c("set1","set2","set3","set4","set5","set6","set7","set8")))
  hor$ano <- as.numeric(substring(datafiles[i], 12, 15))
  hor <- merge(hor, cod, by=c("nome"))
  ### Reorganizando as colunas
  hor <- hor[,c((n_class+3),(n_class+2),2:(n_class+1))]
  if (i==1){base <- data.frame(matrix(vector(), 0, length(names(hor)),
                              dimnames=list(c(), names(hor))), stringsAsFactors=F)}
  base <- rbind(base, hor)
}

emp <- read.csv(file ="base_emp_set.csv", header=TRUE, sep=",")
base <- merge(base, emp, by=c("cod_mun", "ano"))

base0 <- base

base <- base[,1:2]
base[,3:10] <- base0[,3:10]/base0[,11:18]
base[base == "NaN"] = 0

write.csv(base, "base_hormed.csv", row.names=FALSE)