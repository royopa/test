# -------------------------------------------------
# Government advertising spending maps
# Author: Bernardo Ribeiro
# Info: Draw maps to analyze govt ads spending
#       spatially
# Last update: 15sep2016
# -------------------------------------------------

#install.packages("maptools")
#install.packages("RColorBrewer")
#install.packages("ggmap")
#install.packages("rgdal")
#install.packages("scales")
#install.packages("dplyr")
#install.packages("Cairo")
#install.packages("rgeos")
#install.packages("gtools")

library(maptools)
library(RColorBrewer)
library(ggmap)
library(rgdal)
library(scales)
library(dplyr)
library(Cairo)
library(rgeos)
library(gtools)

setwd("E:/Dissertacao")
rm(list=ls())

data.path <- "DADOS/04.Controles/"
# load data
base <- read.csv(file =paste0(data.path,"base_rain.csv"), header=TRUE, sep=",")
base <- base[,c("cod_mun","ano","precip")]

base00 <- base %>% group_by(cod_mun) %>% select(precip) %>% 
                   summarise(P_med=mean(precip))
base <- merge(base, base00, by=c("cod_mun"))
base$fac_X <- quantcut(base$P_med, q=5, na.rm=TRUE)

# load municipalities shapefile
shp <- readOGR(dsn="FigGrafs/ShapeFile/Municipios", layer="municipios_2010")
shpst <- readOGR(dsn="FigGrafs/ShapeFile/Estados", layer="estados_2010")

# convert to dataframe
munics <- fortify(shp, region="codigo_ibg")
states <- fortify(shpst, region="codigo_ibg")

# merge data
names(munics)[names(munics)=="id"] <- "cod_mun"
munics$cod_mun <- strtoi(as.character(munics$cod_mun))
munics$cod_mun <- trunc(munics$cod_mun/10)

plotData <- left_join(base, munics)
borders <- left_join(base, munics)

# plots
map <- ggplot() +
    geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(fac_X)), color="white", size=0.01) +
    scale_fill_manual(name="", values=c("white", "cadetblue1", "cadetblue3", "deepskyblue4", "blue4"),guide=FALSE) +
    coord_map() + 
    theme(plot.title = element_text(face="bold", size=15)) +
    ggtitle("Precipitação")
ggsave(map, file = paste0(data.path,"map_rain.png"), type = "cairo-png")