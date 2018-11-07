library(readxl)
library(dplyr)

rm(list=ls())
setwd("E:/Dissertacao/DADOS/04.Controles/")

data <- read.csv("06.Precipitacoes(00-14)/base_prp_anual.csv")
data$coord <- round(data$long, digits=2)*1000000 + data$lat
data <- data[,c("coord","ano","precip_yr")]

muns <- as.data.frame(read_xls("06.Precipitacoes(00-14)/anexo_16261_Coordenadas_Sedes.xls", 
                               skip=0, sheet=1))[,c(1,3,4)]
names(muns)  <- c("cod_mun","long","lat")
muns$cod_mun <- trunc(as.numeric(muns$cod_mun)/10)

##### Definindo o quadrante ao redor do município
muns$lat1 <- muns$lat_1 <- muns$long1 <- muns$long_1 <- 1000
muns$long_s <- ceiling(muns$long) - muns$long
muns$lat_s  <- ceiling(muns$lat)  - muns$lat
muns$long_1[muns$long_s <=.25]                       <- floor(muns$long[muns$long_s <=.25]) + .75
muns$long_1[muns$long_s >.25   & muns$long_s <=.75]  <- floor(muns$long[muns$long_s >.25   & muns$long_s <=.75]) + .25
muns$long_1[muns$long_s >.75]                        <- floor(muns$long[muns$long_s >.75]) - .25
muns$long1[muns$long_s <=.25]                        <- floor(muns$long[muns$long_s <=.25]) + 1.25
muns$long1[muns$long_s >.25    & muns$long_s <=.75]  <- floor(muns$long[muns$long_s >.25    & muns$long_s <=.75]) + .75
muns$long1[muns$long_s >.75]                         <- floor(muns$long[muns$long_s >.75]) + .25
muns$lat_1[muns$lat_s <=.25]                         <- floor(muns$lat[muns$lat_s <=.25])  + .75
muns$lat_1[muns$lat_s >.25     & muns$lat_s <=.75]   <- floor(muns$lat[muns$lat_s >.25     & muns$lat_s <=.75])  + .25
muns$lat_1[muns$lat_s >.75]                          <- floor(muns$lat[muns$lat_s >.75])  - .25
muns$lat1[muns$lat_s <=.25]                          <- floor(muns$lat[muns$lat_s <=.25])  + 1.25
muns$lat1[muns$lat_s >.25      & muns$lat_s <=.75]   <- floor(muns$lat[muns$lat_s >.25      & muns$lat_s <=.75])  + .75
muns$lat1[muns$lat_s >.75]                           <- floor(muns$lat[muns$lat_s >.75])  + .25

##### Ajustando o quadrante ao redor dos municípios q fazem fronteira com o mar
##### A base não tem info de precipitação no mar
lats <- unique(muns$lat_1)
lats <- lats[order(lats)]
L <- max(muns$lat[muns$long == max(muns$long)])
for (i in 1:length(lats)){
      max_long <- max(muns$long1[muns$lat_1 == lats[i]])
      id <- which(muns$lat_1 == lats[i] & muns$long1 == max_long)
      if (lats[i]>L){muns$long1[id] <- muns$long_1[id]
                     muns$lat1[id]  <- muns$lat_1[id]
      } else if (lats[i]<L){muns$long1[id] <- muns$long_1[id]
                            muns$lat_1[id] <- muns$lat1[id]}}

##### Reduzindo a dimensão do identificador de coordenadas e calculando a distância de cada município ao vértice do quadrante
muns$coord1 <- muns$long1 *10^6 + muns$lat1; muns$d1 <- sqrt((muns$long - muns$long1)^2  + (muns$lat - muns$lat1)^2)
muns$coord2 <- muns$long_1*10^6 + muns$lat1; muns$d2 <- sqrt((muns$long - muns$long_1)^2 + (muns$lat - muns$lat1)^2)
muns$coord3 <- muns$long_1*10^6 + muns$lat_1; muns$d3 <- sqrt((muns$long - muns$long_1)^2 + (muns$lat - muns$lat_1)^2)
muns$coord4 <- muns$long1 *10^6 + muns$lat_1; muns$d4 <- sqrt((muns$long - muns$long1)^2  + (muns$lat - muns$lat_1)^2)

##### Coletando a info de precipitação para cada vértice do quadrante de cada município
muns1 <- muns[,c("cod_mun","coord1","d1")]; muns1 <- merge(muns1, data, by.x=c("coord1"), by.y=c("coord"))
muns1 <- muns1[,2:5]; names(muns1) <- c("cod_mun","d1","ano","precip_d1")
muns2 <- muns[,c("cod_mun","coord2","d2")]; muns2 <- merge(muns2, data, by.x=c("coord2"), by.y=c("coord"))
muns2 <- muns2[,2:5]; names(muns2) <- c("cod_mun","d2","ano","precip_d2")
muns3 <- muns[,c("cod_mun","coord3","d3")]; muns3 <- merge(muns3, data, by.x=c("coord3"), by.y=c("coord"))
muns3 <- muns3[,2:5]; names(muns3) <- c("cod_mun","d3","ano","precip_d3")
muns4 <- muns[,c("cod_mun","coord4","d4")]; muns4 <- merge(muns4, data, by.x=c("coord4"), by.y=c("coord"))
muns4 <- muns4[,2:5]; names(muns4) <- c("cod_mun","d4","ano","precip_d4")

base <- merge(muns1, muns2, by=c("cod_mun","ano"))
base <- merge(base, muns3, by=c("cod_mun","ano"))
base <- merge(base, muns4, by=c("cod_mun","ano"))

base$precip <- (base$precip_d1*base$d1 + base$precip_d2*base$d2 + base$precip_d3*base$d3 + base$precip_d4*base$d4/(base$d1 + base$d2 + base$d3 + base$d4))
base <- base[ ,c("cod_mun","ano","precip")]

base_res <- base %>% group_by(cod_mun) %>% select(precip) %>% summarise(m_pr = mean(precip), dp_pr = sd(precip)) %>% as.data.frame
base <- merge(base, base_res , by=("cod_mun"))
base$d_precip <- 0
base$d_precip[base$precip < (base$m_pr - base$dp_pr)] <- 1

base <- base[,c("cod_mun","ano","precip","d_precip")]
 
write.csv(base, "base_rain.csv", row.names=FALSE)
