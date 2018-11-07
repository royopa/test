rm(list=ls())
setwd("E:/Dissertacao/DADOS")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- 8
# Ativ1 - ext. mineral      Ativ2 - ind. transformaçao     Ativ3 - serv. industriais
# Ativ4 - const. civil      Ativ5 - comercio               Ativ6 - serviços
# Ativ7 - adm. publica      Ativ8 - agropecuaria           + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_set_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =1, header=TRUE, sep=";", dec = ",")
    emp <- emp[1:(which(emp[,1] == "Total")-1), (1:(n_class+1))]
    names(emp) <- c("nome",paste0("emp_",c("set1","set2","set3","set4", 
                                  "set5","set6","set7","set8")))
    emp$ano <- as.numeric(substring(datafiles[i], 9, 12))
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas
    emp <- emp[, c((n_class + 3),(n_class + 2),2:(n_class+1))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

base <- na.omit(base)

### Forçando as variáveis para o formato numérico
for (j in 1:n_class){base[,j+2] <- as.numeric(as.character(base[,j+2]))}
write.csv(base, "base_emp_set.csv",row.names=FALSE)