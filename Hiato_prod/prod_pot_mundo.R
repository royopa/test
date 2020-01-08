library(readxl,    lib.loc="~/R/win-library/3.5")
library(mFilter,   lib.loc="~/R/win-library/3.5")
library(lubridate, lib.loc="~/R/win-library/3.5")
library(seasonal,  lib.loc="~/R/win-library/3.5")
rm(list=ls())

source("C:/Users/PIETCON/Documents/Codes/Bases/base_pmi.R", local = TRUE)
source("C:/Users/PIETCON/Documents/Codes/Bases/base_icb.R", local = TRUE)

setwd("C:/Users/PIETCON/Documents")
initial_date <- 2001
end_date <- 2018.5

Y <- aggregate(ts(pmi$pmi_global, freq=12, start=c(1998,1)), nfrequency=4)/3
Y <- Y[time(Y) >= initial_date & time(Y) < end_date]
#C <- aggregate(ts(conf$nuci_dsz, freq=12, start=c(2001,1)),nfrequency=4)/3
#C <- C[time(C) >= initial_date & time(C) < end_date]
#E <- 1- aggregate(ts(unemp$tx_desemp, freq=12, start=c(1998,1)),nfrequency=4)/3
#E <- E[time(E) >= initial_date & time(E) < end_date]
Pi <- aggregate(ts(icbr$icbr, freq=12, start=c(1998,1)), nfrequency=4)
Pi <- Pi[time(Pi) >= (initial_date - .25) & time(Pi) <= end_date]

t <- seq(as.Date("2001/1/1"), as.Date("2018/6/1"), by = "quarter")
data <- Y
#data = na.omit(cbind(E,C,Y))

# y para SCRIPT_AREOSA_2008
y = matrix(log(data), nrow = length(na.omit(Y)), ncol = 3)
data <- as.data.frame(data)

# DESSAZONALIZANDO A INFLAÇÃO para SCRIPT_EXT_AREOSA
pi_ts = ts(Pi, start = c(2001,1), end = c(year(as.Date(t[length(t)])),quarter(as.Date(t[length(t)]))), frequency = 4)
pi_sa_pad = pi_ts

# TENDÊNCIA LINEAR
linear.trend.model = lm(log(Y)~t)
Yn.lin.trend = ts(exp(linear.trend.model$fitted.values), start = c(2001,1), frequency = 4)

# FILTRO HP
gdp = ts(log(Y),start = c(2001,1), end = c(year(as.Date(t[length(t)])),quarter(as.Date(t[length(t)]))), frequency = 4)
hp.filter.model = hpfilter(gdp)
Yn.hp = exp(hp.filter.model$trend)

# FILTRO HP COM FÇ DE PRODUÇÃO (AREOSA)
#source("Codes/Scripts Hiato/SCRIPT_AREOSA_2008.R", local = TRUE)
#est.prod.fn <- cbind(En,Cn,Yn)
#Yn.prod.fn <- ts(Yn[-1], start = c(2001,1), frequency = 4)

# EXTENDIDO (INCLUI CURVA DE PHILLIPS)
#source("Codes/Scripts Hiato/SCRIPT_EXT_AREOSA.R", local = TRUE)
#est.areosa <- cbind(En.ext,Cn.ext,Yn.ext)
#Yn.areosa <- ts(c(NA, Yn.ext), start = c(2001,1), frequency = 4)

# BLANCHARD E QUAH
#source("Codes/Scripts Hiato/SCRIPT_BLANCHARD_QUAH.R", local = TRUE)
#Os output desta rotina são dem_tot_sh0, dem_tot_sh1 e dem_tot_sh2

# BEVERIDGE-NELSON DECOMPOSITION
source("Codes/Scripts Hiato/SCRIPT_BEVERIDGE_NELSON.R", local = TRUE)
Yn.bevnel <- ts(Yn.BN, start = c(2001,1), frequency = 4)

#hiato <- as.data.frame(cbind(t, Yn.lin.trend, Yn.hp, Yn.prod.fn, Yn.areosa, Yn.bevnel))
#Yn.areosa[1] <- mean(Yn.lin.trend[1], Yn.hp[1], Yn.prod.fn[1], Yn.bevnel[1])
Yn <- (Yn.lin.trend + Yn.hp + Yn.bevnel)/3

write.csv(cbind(t, Yn), file="Data/EST_prod_pot_mundo.csv", row.names = FALSE)
