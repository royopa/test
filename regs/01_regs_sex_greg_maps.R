library(maptools)
library(RColorBrewer)
library(colorRamps)
library(ggmap)
library(rgdal)
library(scales)
library(dplyr)
library(Cairo)
library(rgeos)
library(gtools)

library(lfe)
library(stargazer)
library(dplyr)

rm(list=ls())
setwd("E:/Dissertacao")
tables.dest <- "Tabelas de Resultados/temp/" 

base <- read.csv(file ="BASES/00_base.csv", header=TRUE, sep=",")
#base <- base[base$ano > 2005 & base$ano < 2015,]
facs <- c("cod_mun","ano","re","uf","meso","micro","cod_ibge")
base[,facs] <- lapply(base[,facs],as.factor)

### Seleciona as variáveis a serem Utilizadas nas regressões
base$ID                   <- base$cod_mun
base$TEND <- base$CLUS    <- base$micro
base$ANO                  <- as.factor(base$ano)

base$Y <- log(1 + base$emp_tot)
base$X <- log(1 + base$pbf_fam)
base$Y_quint <- exp(base$Y) -1
base$X_quint <- exp(base$X) -1

controls_tab <- "+ log(1 + pop)"

#######
# TABELA 2: Quebras com dummies (Dummy Estado x Tempo)
#######

base$DR5 <- base$DR4 <- base$DR3 <- base$DR2 <- base$DR1 <- 0
base$DR1[which(base$re==1)] <- 1
base$DR2[which(base$re==2)] <- 1
base$DR3[which(base$re==3)] <- 1
base$DR4[which(base$re==4)] <- 1
base$DR5[which(base$re==5)] <- 1

#######

base00 <- base %>% group_by(cod_mun) %>% select(X_quint,Y_quint,pop) %>% 
  summarise(X_med = mean(X_quint / pop), Y_med = mean(Y_quint / pop), pop_med = mean(pop))
#### Adding missing grouping variables: `cod_mun`
base <- merge(base, base00, by=c("cod_mun"))

####### Dummies para a quebra por var X

base$DX5 <- base$DX4 <- base$DX3 <- base$DX2 <- base$DX1 <- 0
base$DX1[which(base$X_med<=quantile(base$X_med, .2))] <- 1
base$DX2[which(base$X_med>quantile(base$X_med, .2) & base$X_med<=quantile(base$X_med, .4))] <- 1
base$DX3[which(base$X_med>quantile(base$X_med, .4) & base$X_med<=quantile(base$X_med, .6))] <- 1
base$DX4[which(base$X_med>quantile(base$X_med, .6) & base$X_med<=quantile(base$X_med, .8))] <- 1
base$DX5[which(base$X_med>quantile(base$X_med, .8))] <- 1

####### Dummies para a quebra por var Y

base$DY5 <- base$DY4 <- base$DY3 <- base$DY2 <- base$DY1 <- 0
base$DY1[which(base$Y_med<=quantile(base$Y_med, .2))] <- 1
base$DY2[which(base$Y_med>quantile(base$Y_med, .2) & base$Y_med<=quantile(base$Y_med, .4))] <- 1
base$DY3[which(base$Y_med>quantile(base$Y_med, .4) & base$Y_med<=quantile(base$Y_med, .6))] <- 1
base$DY4[which(base$Y_med>quantile(base$Y_med, .6) & base$Y_med<=quantile(base$Y_med, .8))] <- 1
base$DY5[which(base$Y_med>quantile(base$Y_med, .8))] <- 1

####### Dummies para a quebra por pib per capita

base$DI5 <- base$DI4 <- base$DI3 <- base$DI2 <- base$DI1 <- 0
base$DI1[which(base$pibpc2010<=quantile(base$pibpc2010, .2))] <- 1
base$DI2[which(base$pibpc2010>quantile(base$pibpc2010, .2) & base$pibpc2010<=quantile(base$pibpc2010, .4))] <- 1
base$DI3[which(base$pibpc2010>quantile(base$pibpc2010, .4) & base$pibpc2010<=quantile(base$pibpc2010, .6))] <- 1
base$DI4[which(base$pibpc2010>quantile(base$pibpc2010, .6) & base$pibpc2010<=quantile(base$pibpc2010, .8))] <- 1
base$DI5[which(base$pibpc2010>quantile(base$pibpc2010, .8))] <- 1

####### Dummies para a quebra por população

base$DP5 <- base$DP4 <- base$DP3 <- base$DP2 <- base$DP1 <- 0
base$DP1[which(base$pop_med<=quantile(base$pop_med, .2))] <- 1
base$DP2[which(base$pop_med>quantile(base$pop_med, .2) & base$pop_med<=quantile(base$pop_med, .4))] <- 1
base$DP3[which(base$pop_med>quantile(base$pop_med, .4) & base$pop_med<=quantile(base$pop_med, .6))] <- 1
base$DP4[which(base$pop_med>quantile(base$pop_med, .6) & base$pop_med<=quantile(base$pop_med, .8))] <- 1
base$DP5[which(base$pop_med>quantile(base$pop_med, .8))] <- 1

vars <- c("DX","DY","DI","DP")
matches <- unique(grep(paste(vars,collapse="|"), names(base), value=TRUE))
matches <- matches[-c((1:length(vars))*5)]

reg <- felm(as.formula(paste0("Y ~ ",paste(matches, collapse=":X + "),":X", controls_tab, "|ID+ANO:TEND|0|CLUS")), base)
coef <- reg$coefficients[-1,]; coef[is.nan(coef)] <- 0

main <- base[base$ano == 2010, c("cod_mun", matches)]
coef_matrix <- matrix(0, nrow=dim(main)[1], ncol=(dim(main)[2]-1))
for (i in 1:dim(main)[1]){coef_matrix[i,] <- coef}
main[,-1] <- main[,-1] * coef_matrix
main$overall <- rowSums(main[,2:dim(main)[2]])

impact <- main[,c("cod_mun","overall")]
impact$cod_mun <- as.numeric(as.character(impact$cod_mun))

nbins <- 8
impact$quint <- cut(impact$overall, quantile(impact$overall, probs = seq(0, 1, (1/nbins))))

## load municipalities shapefile
shp <- readOGR(dsn="FigGrafs/ShapeFile/Municipios", layer="municipios_2010")
shpst <- readOGR(dsn="FigGrafs/ShapeFile/Estados", layer="estados_2010")

# convert to dataframe
munics <- fortify(shp, region="codigo_ibg")
states <- fortify(shpst, region="codigo_ibg")

# merge data
names(munics)[names(munics)=="id"] <- "cod_mun"
munics$cod_mun <- strtoi(as.character(munics$cod_mun)); munics$cod_mun <- trunc(munics$cod_mun/10)

plotData <- left_join(impact, munics); borders <- left_join(impact, munics)
rdbu <- brewer.pal(11, "RdBu")

graph <- ggplot() + geom_polygon(data=na.omit(plotData), aes(x=long, y=lat, group=group, fill=factor(quint)), size=0.01) +
         scale_fill_manual(name="Impact on employment", values=rdbu[-c(1,2,3)], guide=guide_legend(reverse = TRUE), 
                           labels=c("less than -0.28%","-0.28% ~ -0.10%","-0.10% ~ 0.05%","0.05% ~ 0.15%",
                                    "0.15% ~ 0.29%","0.29% ~ 0.50%","0.50% ~ 1.24%","more than 1.24%")) +
                           #labels=c("less than -0.39%","-0.39% ~ -0.02%","-0.02% ~ -0.007%","-0.007% ~ 0.008%",
                           #         "0.008% ~ 0.27%","0.27% ~ 0.56%","0.56% ~ 1.24%","more than 1.24%")) +
         coord_map() + theme(plot.title = element_text(face="bold", size=15))


freq <- ggplot(data=impact, aes(impact$overall)) + 
        geom_histogram(aes(y =..density..), 
                       breaks=seq(-.12, 0.24, by = .01), 
                       col="grey27", fill="#2166AC", alpha = .2) + 
        geom_vline(aes(xintercept = 0.01), linetype="dashed", color="red") + 
        geom_vline(aes(xintercept = mean(impact$overall)), linetype="dashed", color="black") + 
        labs(x="Predicted Impact (%) for a 10% program expansion", y="freq (%)") + theme(plot.title = element_text(face="bold", size=15))


ggsave(file ="Tabelas de Resultados/temp/graph_ctfact.png", graph, type = "cairo-png")
ggsave(file ="Tabelas de Resultados/temp/freq_ctfact.png", freq, width = 7, height = 2)




matrix <- base[base$ano == 2005, c(grep("DR", names(base)), grep("DX", names(base)),
                                   grep("DY", names(base)), grep("DI", names(base)), grep("DP", names(base)))]

cov_matrix <- cov(matrix)

#install.packages("gplots")
library(gplots)

#Build the matrix data to look like a correlation matrix
x <- cov_matrix
x <- (x - min(x))/(max(x) - min(x)) #Scale the data to be between 0 and 1
#for (i in 1:25) x[i, i] <- 1.0 #Make the diagonal all 1's

#Format the data for the plot
xval <- formatC(x, format="f", digits=2)
pal <- colorRampPalette(c(rgb(0.96,0.96,1), rgb(0.1,0.1,0.9)), space = "rgb")

#Plot the matrix
x_hm <- heatmap.2(x, Rowv=FALSE, Colv=FALSE, dendrogram="none", main="Dummies Covariance Matrix Using Heatmap.2", 
                  xlab="", ylab="", col=pal, tracecol="#303030", trace="none", cellnote=xval, 
                  notecol="black", notecex=0.8, keysize = 1.5, margins=c(5, 5))