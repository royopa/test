rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- 9
# Tam1 - 1 a 4 empregadoS   Tam2 - 5 a 9 emps        Tam3 - 10 a 19 emps
# Tam4 - 20 a 49 emps       Tam5 - 50 a 99 emps      Tam6 - 100 a 249 emps
# Tam7 - 250 a 499 emps     Tam8 - 500 a 999 emps    Tam9 - 1000 ou mais emps + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_tam_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =1, header=TRUE, sep=";", dec = ",")
    emp <- emp[1:(which(emp[,1] == "Total")-1),(1:(n_class+1))]
    names(emp) <- c("nome",paste0("emp_",c("tam1", "tam2", "tam3", "tam4", 
                                  "tam5", "tam6", "tam7", "tam8", "tam9")))
    emp$ano <- as.numeric(substring(datafiles[i], 9, 12))
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas
    emp <- emp[, c((n_class + 3),(n_class + 2),2:(n_class+1))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

### Forçando as variáveis para o formato numérico
for (j in 1:n_class){base[,j+2] <- as.numeric(as.character(base[,j+2]))}
write.csv(base, "base_emp_tam.csv",row.names=FALSE)