# SCRIPT QUE AGREGA DIVERSAS FORMAS DE CÁLCULO DO PIB POTENCIAL
# TOMA COMO BASE O BOX DO BC DE SET 1999 E IMF 2003

# PACOTES
library("readxl", lib.loc="~/R/win-library/3.4")
library("mFilter", lib.loc="~/R/win-library/3.4")
library("lubridate", lib.loc="~/R/win-library/3.4")
library("seasonal", lib.loc="~/R/win-library/3.4")

# LENDO BASE DE DADOS
setwd("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Atividade/PIB/PIB potencial") #DIRETÓRIO BASE DE DADOS
data_ = read_excel("POTENTIAL_GDP.xlsx",sheet="BASE")
setwd("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Atividade/PIB/PIB potencial/R") #TRABALHANDO NA PASTA R

#DADOS
E = 1 - data_$UNEMP
C = data_$NUCI
Y = data_$PIB
Pi = data_$CORE_IPCA
t = data_$DATES
y = log(matrix(data = na.omit(cbind(E,C,Y)), nrow = length(na.omit(E)),ncol = 3 )) # y para SCRIPT_AREOSA_2008

# DESSAZONALIZANDO A INFLAÇÃO
pi_ts = ts(Pi, start = c(1996,1), end = c(year(as.Date(t[length(t)])),quarter(as.Date(t[length(t)]))), frequency = 4 )
pi_sa = seas(pi_ts)$data[,"seasonaladj"]
pi_sa_pad = c(rep(NA,times = sum(is.na(pi_ts))),pi_sa ) # padronizando


# TENDÊNCIA LINEAR
linear.trend.model = lm(log(Y)~t)
Yn.trend = exp(linear.trend.model$fitted.values)

# FILTRO HP
gdp = ts(log(Y),start = c(1996,1), end = c(year(as.Date(t[length(t)])),quarter(as.Date(t[length(t)]))), frequency = 4)
hp.filter.model = hpfilter(gdp)
Yn.hp = exp(hp.filter.model$trend)





# FILTRO HP COM FÇ DE PRODUÇÃO (AREOSA)
source("SCRIPT_AREOSA_2008.R", local = TRUE) #já salva em output_areosa.xlsx as séries estimadas
# EXTENDIDO (INCLUI CURVA DE PHILLIPS)
source("SCRIPT_EXT_AREOSA.R", local = TRUE) #já salva em output_areosa_ext.xlsx as séries estimadas
# BLANCHARD E QUAH
source("SCRIPT_BLANCHARD_QUAH.R", local = TRUE) #já salva em output_BQi.xlsx as séries estimadas
# BEVERIDGE-NELSON DECOMPOSITION
source("SCRIPT_BEVERIDGE_NELSON.R", local = TRUE) #já salva em output_BN.xlsx a série estimada (somente PIB)

wb = write.xlsx(cbind(Yn.trend,Yn.hp),file = "output_simples.xlsx")

