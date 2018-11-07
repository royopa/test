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
base <- base[c("cod_mun","ano","pop","pbf_fam","emp_tot","pibpc2010")]

base00 <- base %>% group_by(cod_mun) %>% select(pbf_fam,emp_tot,pop) %>% 
                   summarise(X_med=mean(pbf_fam/pop),Y_med=mean(emp_tot/pop),ind_med=mean(pbf_ind/pop))
base <- merge(base, base00, by=c("cod_mun"))
base$fac_X <- quantcut(base$X_med, q=5, na.rm=TRUE)
base$fac_Y <- quantcut(base$Y_med, q=5, na.rm=TRUE)
base$fac_pib <- quantcut(base$pibpc2010, q=5, na.rm=TRUE)

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
map_x <- ggplot() +
    geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(fac_X)), color="white", size=0.01) +
    scale_fill_manual(name="", values=c("blue4", "blue", "white", "red", "red4"),guide=FALSE, 
                      labels=c("5.o quintil","4.o quintil","3.o quintil","2.o quintil","1.o quintil")) +
    coord_map() + 
    theme(plot.title = element_text(face="bold", size=15)) +
    ggtitle("Bolsa Familia")
ggsave(map_x, file = "FigGrafs/SFronteira/map_x.png", type = "cairo-png")

map_y <- ggplot() +
    geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(fac_Y)), color="white", size=0.01) +
    scale_fill_manual(name="", values=c("red4", "red", "white", "blue", "blue4"),guide=FALSE, 
                      labels=c("5.o quintil","4.o quintil","3.o quintil","2.o quintil","1.o quintil")) +
    coord_map() +
    theme(plot.title = element_text(face="bold", size=15)) +
    ggtitle("Employment")
ggsave(map_y, file = "FigGrafs/SFronteira/map_y.png", type = "cairo-png")

map_pibpc <- ggplot() +
    geom_polygon(data=plotData, aes(x=long, y=lat, group=group, fill=factor(fac_pib)), color="white", size=0.01) +
    scale_fill_manual(name="", values=c("red4", "red", "white", "blue", "blue4"),guide=FALSE, 
                      labels=c("5.o quintil","4.o quintil","3.o quintil","2.o quintil","1.o quintil")) +
    coord_map() + 
    theme(plot.title = element_text(face="bold", size=15)) +
    ggtitle("PIB per capita")
ggsave(map_pibpc, file = "FigGrafs/SFronteira/map_pic.png", type = "cairo-png")