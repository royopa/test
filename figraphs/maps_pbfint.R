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

# load data
base <- read.csv(file ="BASES/00_base.csv", header=TRUE, sep=",")
base <- base[c("cod_mun","ano","pop","pbf_ind")]

base00 <- base %>% group_by(cod_mun) %>% select(pbf_ind, pop) %>% 
                      summarise(ind_med=mean(pbf_ind/pop)) %>% as.data.frame
base <- merge(base, base00, by=c("cod_mun"))
base <- base[base$ano == 2010,]
base$d70 <- base$d60 <- base$d50 <- base$d40 <- 0
base$d70[which(base$ind_med > .7)] <- 1
base$d60[which(base$ind_med > .6)] <- 1
base$d50[which(base$ind_med > .5)] <- 1
base$d40[which(base$ind_med > .4)] <- 1

for (j in 6:ncol(base)){base[,j] <- as.factor(base[,j])}

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
map_d40 <- ggplot() +
    geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(d40)), color="white", size=0.01) +
    scale_fill_manual(name="", values=c("white", "red"),guide=FALSE) +
    coord_map() + 
    theme(plot.title = element_text(face="bold", size=15))
ggsave(map_d40, file = "FigGrafs/map_d40.png", type = "cairo-png")

map_d50 <- ggplot() +
  geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(d50)), color="white", size=0.01) +
  scale_fill_manual(name="", values=c("white", "red"),guide=FALSE) +
  coord_map() + 
  theme(plot.title = element_text(face="bold", size=15))
ggsave(map_d50, file = "FigGrafs/map_d50.png", type = "cairo-png")

map_d60 <- ggplot() +
  geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(d60)), color="white", size=0.01) +
  scale_fill_manual(name="", values=c("white", "red"),guide=FALSE) +
  coord_map() + 
  theme(plot.title = element_text(face="bold", size=15))
ggsave(map_d60, file = "FigGrafs/map_d60.png", type = "cairo-png")

map_d70 <- ggplot() +
  geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(d70)), color="white", size=0.01) +
  scale_fill_manual(name="", values=c("white", "red"),guide=FALSE) +
  coord_map() + 
  theme(plot.title = element_text(face="bold", size=15))
ggsave(map_d70, file = "FigGrafs/map_d70.png", type = "cairo-png")
