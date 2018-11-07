rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "01.RAIS/"
### Categorias a variável tem
# Ativ1 - ext. mineral      Ativ2 - ind. transformaçao     Ativ3 - serv. industriais
# Ativ4 - const. civil      Ativ5 - comercio               Ativ6 - serviços
# Ativ7 - adm. publica      Ativ8 - agropecuaria           + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_setsex_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =3, header=FALSE, sep=";", dec = ",")
    emp$ano <- as.numeric(as.character(emp[which(emp[,1] == "Ano"),3]))
    emp <- emp[1:(which(emp[,1] == "Total")-1),]
    names(emp) <- c("nome",paste0("emp_",paste0(rep(c("set1","set2","set3","set4", 
                                  "set5","set6","set7","set8","tot"),each=3),c("_masc","_fem","_tot"))),"ano")
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas
    n <- ncol(emp)
    emp <- emp[, c(n,n-1,2:(n-2))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

base <- na.omit(base)
base <- base[,-grep("tot",names(base))]

### Forçando as variáveis para o formato numérico
for (j in 3:ncol(base)){base[,j] <- as.numeric(as.character(base[,j]))}
write.csv(base, "base_emp_setsex.csv",row.names=FALSE)
