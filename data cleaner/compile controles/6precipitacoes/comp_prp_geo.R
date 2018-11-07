rm(list=ls())
setwd("E:/Dissertacao/DADOS/04.Controles")

data.path = "06.Precipitacoes(00-14)/"

files <- list.files(path = data.path)
ys <- length(files)

for (i in 1:ys){
      file <- files[i]
      precip <- read.csv(paste0(data.path,file), sep=" ")
      blank <- data.frame(matrix(vector(), nrow(precip), 14, 
                          dimnames=list(c(),c("long","lat","jan","fev","mar","abr","mai",
                                          "jun","jul","ago","set","out","nov","dez"))), 
                          stringsAsFactors = FALSE)
      
      for (j in 1:nrow(precip)){blank[j,] <- precip[j,-which(is.na(precip[j,]))]}
      
      blank$ano <- as.numeric(substring(file, 8,11))
      if (i == 1){base <- data.frame(matrix(vector(), 0, 15), 
                                     stringsAsFactors = FALSE)}
      base <- rbind(base,blank)
}

write.csv(base, paste0(data.path,"base_prp_mensal.csv"), row.names = FALSE)

base1 <- base[,c(1,2,dim(base)[2])]
base1$precip_yr <- rowSums(base[, 3:(dim(base)[2]-1)])

#### Dando um subset na base para delimitar apenas o território brasileiro 
base1 <- base1[base1$long> -80 & base1$long< -30 & 
               base1$lat> -40 & base1$lat< 10, ]

write.csv(base1, paste0(data.path,"base_prp_anual.csv"), row.names = FALSE)