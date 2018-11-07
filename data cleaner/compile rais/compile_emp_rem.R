rm(list=ls())
setwd("F:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- 13
# Rem1 - ate ,5 r$ p/ hora        Rem2 - de ,51 a 1 r$ p/h     Rem3 - de 1,01 a 1,50 r$ p/h 
# Rem4 - de 1,51 a 2 r$ p/h       Rem5 - de 2,01 a 3 r$ p/h    Rem6 - de 3,01 a 4 r$ p/h 
# Rem7 - de 4,01 a 5 r$ p/h       Rem8 - de 5,01 a 7 r$ p/h    Rem9 - de 7,01 a 10 r$ p/h 
# Rem10 - de 10,01 a 15 r$ p/h    Rem11 - de 15,01 a 20 r$ p/h Rem12 - de 20,01 ou mais r$ p/h 
# Rem13 - {ñ class}               + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_rem_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =1, header=TRUE, sep=";", dec = ",")
    emp <- emp[1:(which(emp[,1] == "Total")-1),(1:(n_class+1))]
    names(emp) <- c("nome",paste0("emp_",c("rem1","rem2","rem3","rem4","rem5",
                                           "rem6","rem7","rem8","rem9","rem10",
                                           "rem11","rem12","rem13")))
    emp$ano <- as.numeric(substring(datafiles[i], 9, 12))
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas e elimino a classe rem13 - {ñ class}
    emp <- emp[, c((n_class+3),(n_class+2),2:n_class)]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

### Forçando as variáveis para o formato numérico
for (j in 1:(n_class-1)){base[,j+2] <- as.numeric(as.character(base[,j+2]))}
write.csv(base, "base_emp_rem.csv",row.names=FALSE)