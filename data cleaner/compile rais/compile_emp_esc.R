rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- 9
# Esc1 - analfabeto      Esc2 - 4.a ser incomp   Esc3 - 4.a ser comp 
# Esc4 - 8.a ser incomp  Esc5 - 8.a ser comp     Esc6 - 2.o grau incomp
# Esc7 - 2.o grau comp   Esc8 - mestrado         Esc8 - doutorado + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_esc_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =1, header=TRUE, sep=";", dec = ",")
    emp <- emp[1:(which(emp[,1] == "Total")-1),(1:(n_class+1))]
    names(emp) <- c("nome",paste0("emp_",c("esc1","esc2","esc3","esc4", 
                                  "esc5","esc6","esc7","esc8","esc9")))
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
write.csv(base, "base_emp_esc.csv", row.names=FALSE)