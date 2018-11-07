#install.packages("lfe")
#install.packages("stargazer")
#install.packages("sandwich")
#install.packages("dplyr")
#install.packages("reshape2")
#install.packages("readxl")
#install.packages("car")
library(lfe)
library(car)
library(stargazer)
library(dplyr)
library(ggplot2)
rm(list=ls())
setwd("E:/Dissertacao")
tables.dest <- "Tabelas de Resultados/temp/"

i=1;   if (i==1) {base <- read.csv(file ="BASES/BNDES_base.csv", header=TRUE, sep=",")
                  base$endog <- log(1 + base$ops_bndes)
                  endog.tag <- "e1"; endog.nam <- "Log(BNDES' transfers)"
} else if (i==2) {base <- read.csv(file ="BASES/TSE_base_bey.csv", header=TRUE, sep=",")
                  base$endog <- base$mpart
                  endog.tag <- "e2"; endog.nam <- "Mayor's Party"
} else if (i==3) {base <- read.csv(file ="BASES/PSF_base.csv", header=TRUE, sep=",")
                  base$endog <- base$d_eSF
                  endog.tag <- "e3"; endog.nam <- "PSF"
} else if (i==4) {base <- read.csv(file ="BASES/Rain_base.csv", header=TRUE, sep=",")
                  base$endog <- base$d_precip
                  endog.tag <- "e4"; endog.nam <- "Rain"
} else if (i==6) {base <- read.csv(file ="BASES/Edu_base.csv", header=TRUE, sep=",")
                  base$endog <- base$p_educ
                  endog.tag <- "e6"; endog.nam <- "Mother's Education"
} else if (i==7) {base <- read.csv(file ="BASES/Mort_base.csv", header=TRUE, sep=",")
                  base$endog <- base$p_mtinf
                  endog.tag <- "e7"; endog.nam <- "Child Mortality"}

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
base$d_endog <- base$endog
base$d_endog[-which(base$endog == 0)] <- 1

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$re==1)] <- 1; a <- which(base$D1==1)
base$D2[which(base$re==2)] <- 1; b <- which(base$D2==1)
base$D3[which(base$re==3)] <- 1; c <- which(base$D3==1)
base$D4[which(base$re==4)] <- 1; d <- which(base$D4==1)
base$D5[which(base$re==5)] <- 1; e <- which(base$D5==1)

base$endog.d1 <- base$D1 * base$X * base$d_endog
base$endog.d2 <- base$D2 * base$X * base$d_endog
base$endog.d3 <- base$D3 * base$X * base$d_endog
base$endog.d4 <- base$D4 * base$X * base$d_endog
base$endog.d5 <- base$D5 * base$X * base$d_endog

### Editores do STARGAZER
controls_tab <- "log(1 + pop) + endog + endog.d1 + endog.d2 + endog.d3 + endog.d4 + endog.d5"
controls_tab.base <- "log(1 + pop)"

#####as variaveis interagidas sempre são jogadas para o final da tabela...
var.y_cap <- "Log(employ.)"
var.omit <- NULL
edit.rep <- c("vc*s") # report t stat instead of std error

reg1 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
reg1b<- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab.base,  "|ID+ANO:TEND|0|CLUS")),   base)

#######

base00 <- base %>% group_by(cod_mun) %>% select(X_quint,Y_quint,pop) %>% 
                      summarise(X_med = mean(X_quint / pop), Y_med = mean(Y_quint / pop), pop_med = mean(pop))
####Adding missing grouping variables: `cod_mun`
base <- merge(base, base00, by=c("cod_mun"))

####### Dummies para a quebra por var X

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$X_med<=quantile(base$X_med, .2))] <- 1
base$D2[which(base$X_med>quantile(base$X_med, .2) & base$X_med<=quantile(base$X_med, .4))] <- 1
base$D3[which(base$X_med>quantile(base$X_med, .4) & base$X_med<=quantile(base$X_med, .6))] <- 1
base$D4[which(base$X_med>quantile(base$X_med, .6) & base$X_med<=quantile(base$X_med, .8))] <- 1
base$D5[which(base$X_med>quantile(base$X_med, .8))] <- 1

reg2 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
reg2b<- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab.base,  "|ID+ANO:TEND|0|CLUS")),   base)

####### Dummies para a quebra por var Y

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$Y_med<=quantile(base$Y_med, .2))] <- 1
base$D2[which(base$Y_med>quantile(base$Y_med, .2) & base$Y_med<=quantile(base$Y_med, .4))] <- 1
base$D3[which(base$Y_med>quantile(base$Y_med, .4) & base$Y_med<=quantile(base$Y_med, .6))] <- 1
base$D4[which(base$Y_med>quantile(base$Y_med, .6) & base$Y_med<=quantile(base$Y_med, .8))] <- 1
base$D5[which(base$Y_med>quantile(base$Y_med, .8))] <- 1

reg3 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
reg3b<- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab.base,  "|ID+ANO:TEND|0|CLUS")),   base)

####### Dummies para a quebra por pib per capita

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pibpc2010<=quantile(base$pibpc2010, .2))] <- 1
base$D2[which(base$pibpc2010>quantile(base$pibpc2010, .2) & base$pibpc2010<=quantile(base$pibpc2010, .4))] <- 1
base$D3[which(base$pibpc2010>quantile(base$pibpc2010, .4) & base$pibpc2010<=quantile(base$pibpc2010, .6))] <- 1
base$D4[which(base$pibpc2010>quantile(base$pibpc2010, .6) & base$pibpc2010<=quantile(base$pibpc2010, .8))] <- 1
base$D5[which(base$pibpc2010>quantile(base$pibpc2010, .8))] <- 1

reg4 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
reg4b<- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab.base,  "|ID+ANO:TEND|0|CLUS")),   base)

####### Dummies para a quebra por população

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pop_med<=quantile(base$pop_med, .2))] <- 1
base$D2[which(base$pop_med>quantile(base$pop_med, .2) & base$pop_med<=quantile(base$pop_med, .4))] <- 1
base$D3[which(base$pop_med>quantile(base$pop_med, .4) & base$pop_med<=quantile(base$pop_med, .6))] <- 1
base$D4[which(base$pop_med>quantile(base$pop_med, .6) & base$pop_med<=quantile(base$pop_med, .8))] <- 1
base$D5[which(base$pop_med>quantile(base$pop_med, .8))] <- 1

reg5 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
reg5b<- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X +",   controls_tab.base,  "|ID+ANO:TEND|0|CLUS")),   base)

#######
# TABELA 4: Canais de Endogeneidade e Quebras com Dummies
#######

LREG <- lregs_4 <- list(reg1,reg2,reg3,reg4,reg5)
LREGB<- list(reg1b,reg2b,reg3b,reg4b,reg5b)

FTEST <- lapply(LREG, function(x) linearHypothesis(x, 
                      c("endog=0", "endog.d1=0", "endog.d2=0", "endog.d3=0","endog.d4=0", "endog.d5=0")))
col.labels <- c("Region", "Qts. Benefic.", "Qts. Employ.", "Qts. Pers. Inc.", "Pop.")
tit.name <- paste0("Canal de Endogeneidade: ", endog.nam)
lab <- paste0("dRXYP:dt:", endog.tag)
#####as variaveis interagidas sempre são jogadas para o final da tabela...
vars.x_tab <- c("Log(ben. fam.)*D1","Log(ben. fam.)*D2","Log(ben. fam.)*D3","Log(ben. fam.)*D4","Log(ben. fam.)*D5", paste0("C = ",endog.nam),
                "Log(ben. fam.)*D1*C","Log(ben. fam.)*D2*C","Log(ben. fam.)*D3*C","Log(ben. fam.)*D4*C","Log(ben. fam.)*D5*C","Log(pop.)")
ord <- c(8,9,10,11,12,2,3,4,5,6,7,1)
out.path <- paste0(tables.dest,"tab4", endog.tag,"dt.tex")

stargazer(LREG,
          #notes = tit.name,
          #no.space = TRUE,
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          if (i==6 | i==7){se = lapply(lapply(lapply(LREG,'[[',31),diag),sqrt)}
          else{se = lapply(lapply(lapply(LREG,'[[',30),diag),sqrt)},
          omit = var.omit, omit.stat = NULL,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.labels.include = FALSE,
          dep.var.caption = var.y_cap, 
          covariate.labels = vars.x_tab, order = ord,
          column.labels = col.labels,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
          model.numbers = FALSE, single.row = FALSE, # compress table text
          ##### LABELS
          label = lab, out=out.path,
          ##### EXTRA INFO
          add.lines = list(c("Fixed effects",       "Y","Y","Y","Y","Y"),
                           c("Dummy: Year",         "N","N","N","N","N"),
                           c("State Linear Trend",  "N","N","N","N","N"),
                           c("Dummy: Year x State", "Y","Y","Y","Y","Y"),
                           c("F-test (controls)", round(unlist(lapply(lapply(FTEST,'[[',4),'[[',2)),3))))

#######
# Grafico Coeficientes 4
#######

#input: lista de regressões
#output: um data.frame com todos os coeficientes por quebra e por v. dependente
coef_matrix <- function(regs.list, 
                        x.axis=c("E0","E1","E2","E3","E4","E5","1st","2nd","3rd","4th","5th"),
                        cols=c("Region","Beneficiaries","Formal Employment","Personal Income","Population")){
        
        nc <- length(cols); nx <- length(x.axis); nd <- nx - nc
        coef <- unlist(lapply(regs.list,'[[',7))
        if (i==6 | i==7){se <- unlist(lapply(lapply(lapply(regs.list,'[[',31),diag),sqrt))}
        else{se <- unlist(lapply(lapply(lapply(regs.list,'[[',30),diag),sqrt))}
        se <- se[!se==0]
        
        id_pop <- (1+nx)*(1:nc)-nx; coef <- coef[-id_pop]; se <- se[-id_pop]
        vars <- rep(x.axis, times=nc)#; vars[nd:(nd+nc)] <- c("N","NE","SE","S","CW")
        cl <- rep(cols, each=nx)
        up = coef + 2 * se
        lo = coef - 2 * se
        
        data.frame(vars, cl, coef, se, up, lo)
}

#input: um data.frame com todos os coeficientes por quebra e por v. dependente
#output: um grafico de linhas com todos os coeficientes
graphs <- function(df){
        
        ggplot(df) + 
                geom_errorbar(aes(x = vars, ymax = up, ymin = lo, color=1)) +
                geom_point(aes(x = vars, y = coef, color=1), shape=3) +
                #geom_errorbar(aes(x = vars, ymax = up.x, ymin = lo.x)) +
                geom_point(aes(x = vars, y = coef.baseline), shape=18) +
                geom_hline(aes(yintercept=0), linetype="dashed") +
                facet_grid( ~cl, scales="free") + 
                #ylim(-0.1, 0.2) +
                labs(x = "Dep. Variable", y = "Coefficients") +
                theme(legend.position="none")
}

df_endog <- coef_matrix(LREG)
df_base <- coef_matrix(LREGB, x.axis=c("1st","2nd","3rd","4th","5th"))
df <- merge(df_endog, df_base, by=c("cl","vars"), all=FALSE, suffixes = c("",".baseline"))

levels(df$vars) <- c(levels(df$vars), c("N","NE","S","SE","CW"))
df$vars[df$cl == "Region"] <- as.factor(c("N","NE","SE","S","CW"))

df$cl = factor(df$cl,levels(df$cl)[c(5,1:4)])
df$vars = factor(df$vars,levels(df$vars)[c(1:13,16,15,14)])

ggsave(file =paste0("Tabelas de Resultados/temp/graph_control_", endog.tag,".png"), graphs(df), scale=1.3)
