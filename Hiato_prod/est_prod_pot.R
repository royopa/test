library(readxl,    lib.loc="~/R/win-library/3.5")
library(mFilter,   lib.loc="~/R/win-library/3.5")
library(lubridate, lib.loc="~/R/win-library/3.5")
library(seasonal,  lib.loc="~/R/win-library/3.5")
rm(list=ls())

path <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Hiato_prod/"

source(paste0(path,"compile_df.R"), local = TRUE)


# y para SCRIPT_AREOSA_2008
y = matrix(log(data), nrow = nrow(data), ncol = 3)
data <- as.data.frame(data)


# TENDÊNCIA LINEAR
linear.trend.model = lm(log(data$Y)~t)
Yn.lin.trend = ts(exp(linear.trend.model$fitted.values), start = head(t,1), frequency = 4)


# FILTRO HP
gdp = ts(log(data$Y), start = head(t,1), frequency = 4)
hp.filter.model = hpfilter(gdp)
Yn.hp = exp(hp.filter.model$trend)


# FILTRO HP COM FÇ DE PRODUÇÃO (AREOSA)
source(paste0(path,"SCRIPT_AREOSA_2008.R"), local = TRUE)
est.prod.fn <- cbind(En,Cn,Yn)
Yn.prod.fn <- ts(Yn[-1], start = head(t,1),  frequency = 4)


# EXTENDIDO (INCLUI CURVA DE PHILLIPS)
# essa estimacao nao funciona com inflacao em nivel, apenas com nucleo de inflacao
source(paste0(path,"SCRIPT_EXT_AREOSA.R"), local = TRUE)
est.areosa <- cbind(En.ext,Cn.ext,Yn.ext)
Yn.areosa <- ts(c(NA, Yn.ext), start = head(t,1), frequency = 4)


# BLANCHARD E QUAH
#source(paste0(path,"SCRIPT_BLANCHARD_QUAH.R"), local = TRUE)
#Os output desta rotina são dem_tot_sh0, dem_tot_sh1 e dem_tot_sh2


# BEVERIDGE-NELSON DECOMPOSITION
#source(paste0(path,"SCRIPT_BEVERIDGE_NELSON.R"), local = TRUE)
#Yn.bevnel <- ts(Yn.BN, start = head(t,1), frequency = 4)

Y <- ts(Y, start = head(t,1), frequency = 4)
Yn.areosa[1] <- mean(Yn.lin.trend[1], Yn.hp[1], Yn.prod.fn[1], Yn.bevnel[1])
hiato <- as.data.frame(cbind(t, Y, Yn.lin.trend, Yn.hp, Yn.prod.fn, Yn.areosa))#, Yn.bevnel))
hiato$t <- as.Date(hiato$t, origin="1970-01-01")
Yn <- (Yn.lin.trend + Yn.hp + Yn.prod.fn + Yn.areosa)/5# + Yn.bevnel)/5

t <- t %>% as.character
write.csv(cbind(t, Yn, Y), file=paste0(path,"EST_prod_pot.csv"), row.names = FALSE)
write.csv(hiato, file=paste0(path,"all_EST_prod_pot.csv"), row.names = FALSE)
