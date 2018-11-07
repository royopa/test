#install.packages("lfe")
#install.packages("stargazer")
#install.packages("dplyr")
#install.packages("devtools")
devtools::install_github("ChandlerLutz/starpolishr")
library(starpolishr)
library(lfe)
library(stargazer)
library(dplyr)
rm(list=ls())
setwd("E:/Dissertacao/")
tables.dest <- "Tabelas de Resultados/temp/" 
source('E:/Dissertacao/tex_write.R', echo=TRUE)

base <- read.csv(file ="BASES/00_base.csv", header=TRUE, sep=",")
#base <- base[base$ano > 2005 & base$ano < 2015,]
facs <- c("cod_mun","ano","re","uf","meso","micro","cod_ibge")
base[,facs] <- lapply(base[,facs],as.factor)

### Seleciona as variáveis a serem Utilizadas nas regressões
base$ID                   <- base$cod_mun
base$TEND <- base$CLUS    <- base$micro
base$ANO                  <- as.factor(base$ano)    #opções: (1) as.factor()  ou  (2) as.numeric()

base$Y <- log(1 + base$emp_tot)
base$X <- log(1 + base$pbf_fam)
base$Y_quint <- exp(base$Y) -1
base$X_quint <- exp(base$X) -1

controls_tab <- "+ log(1 + pop)"
var.y_cap <- "Log(employ.)"

### Editores do STARGAZER
stat.omit <- c("rsq","adj.rsq","ser")
var.omit <- c("pop","D2","D3","D4")
edit.rep <- c("vc*s") # report t stat instead of std error
col.labels <- c("Region", "Qts. Benefic.", "Qts. Employ.", "Qts. Pers. Inc.", "Population")
vars.x_tab <- c("Log(ben. fam.)*D1(1= 1st fifth)","Log(ben. fam.)*D2(1= 2nd fifth)","Log(ben. fam.)*D3(1= 3rd fifth)",
                "Log(ben. fam.)*D4(1= 4th fifth)","Log(ben. fam.)*D5(1= 5th fifth)","Log(pop.)")
ord <- c(2,3,4,5,6,1)

####### Criando, a partir de X e Y, as variaveis para quebra em quintis 

base00 <- base %>% group_by(cod_mun) %>% select(X_quint,Y_quint,pop) %>% 
                    summarise(X_med = mean(X_quint / pop), Y_med = mean(Y_quint / pop), pop_med = mean(pop))
#### Adding missing grouping variables: `cod_mun`
base <- merge(base, base00, by=c("cod_mun"))

#######
# TABELA 3: Quebra por Q. PIB per capita
# Para categorias de: Setor, Tamanho, Remuneração, Escolaridade
#######

####### Regressões por Setor

vars.y <- names(base)[grep("tot",names(base))]
REGS_SET <- list(); REGS_TAM <- list(); REGS_REM <- list(); REGS_ESC <- list()

for (i in 1:5){

  if (i==1){####### Dummies para a quebra por Regiao
    var.quebra <- "Regiao"
    break.tag <- "R"
    base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
    base$D1[which(base$re==1)] <- 1;    base$D2[which(base$re==2)] <- 1;    base$D3[which(base$re==3)] <- 1
    base$D4[which(base$re==4)] <- 1;    base$D5[which(base$re==5)] <- 1
    
  } else if (i==2) {####### Dummies para a quebra por var X
    var.quebra <- "BF / pop"
    break.tag <- "X"
    base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
    base$D1[which(base$X_med<=quantile(base$X_med, .2))] <- 1
    base$D2[which(base$X_med>quantile(base$X_med, .2) & base$X_med<=quantile(base$X_med, .4))] <- 1
    base$D3[which(base$X_med>quantile(base$X_med, .4) & base$X_med<=quantile(base$X_med, .6))] <- 1
    base$D4[which(base$X_med>quantile(base$X_med, .6) & base$X_med<=quantile(base$X_med, .8))] <- 1
    base$D5[which(base$X_med>quantile(base$X_med, .8))] <- 1
    
  } else if (i==3) {####### Dummies para a quebra por var Y
    var.quebra <- "Emp. Form / pop"
    break.tag <- "Y"
    base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
    base$D1[which(base$Y_med<=quantile(base$Y_med, .2))] <- 1
    base$D2[which(base$Y_med>quantile(base$Y_med, .2) & base$Y_med<=quantile(base$Y_med, .4))] <- 1
    base$D3[which(base$Y_med>quantile(base$Y_med, .4) & base$Y_med<=quantile(base$Y_med, .6))] <- 1
    base$D4[which(base$Y_med>quantile(base$Y_med, .6) & base$Y_med<=quantile(base$Y_med, .8))] <- 1
    base$D5[which(base$Y_med>quantile(base$Y_med, .8))] <- 1
    
  } else if (i==4) {####### Dummies para a quebra por pib per capita
    var.quebra <- "PIB per capita"
    break.tag <- "P"
    base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
    base$D1[which(base$pibpc2010<=quantile(base$pibpc2010, .2))] <- 1
    base$D2[which(base$pibpc2010>quantile(base$pibpc2010, .2) & base$pibpc2010<=quantile(base$pibpc2010, .4))] <- 1
    base$D3[which(base$pibpc2010>quantile(base$pibpc2010, .4) & base$pibpc2010<=quantile(base$pibpc2010, .6))] <- 1
    base$D4[which(base$pibpc2010>quantile(base$pibpc2010, .6) & base$pibpc2010<=quantile(base$pibpc2010, .8))] <- 1
    base$D5[which(base$pibpc2010>quantile(base$pibpc2010, .8))] <- 1
  } else if (i==5) {####### Dummies para a quebra por população
   var.quebra <- "População"
   break.tag <- "Pp"
   base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
   base$D1[which(base$pop_med<=quantile(base$pop_med, .2))] <- 1
   base$D2[which(base$pop_med>quantile(base$pop_med, .2) & base$pop_med<=quantile(base$pop_med, .4))] <- 1
   base$D3[which(base$pop_med>quantile(base$pop_med, .4) & base$pop_med<=quantile(base$pop_med, .6))] <- 1
   base$D4[which(base$pop_med>quantile(base$pop_med, .6) & base$pop_med<=quantile(base$pop_med, .8))] <- 1
   base$D5[which(base$pop_med>quantile(base$pop_med, .8))] <- 1}
  
        
  sep <- "set"
  vars <- c(1,grep(sep,vars.y))
  REGS_SET[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })
  
  sep <- "tam"
  vars <- c(1,grep(sep,vars.y))
  REGS_TAM[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })
  
  sep <- "rem"
  vars <- c(1,grep(sep,vars.y))
  REGS_REM[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })
  
  sep <- "esc"
  vars <- c(1,grep(sep,vars.y))
  REGS_ESC[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })  
}

star.table <- function(regs, var.omit=c("pop", "D3", "D4", "D5"), 
                       col.labels, cov.labels = vars.x_tab[-unlist(lapply(var.omit, function(x){grep(x,vars.x_tab)}))]){LREG <- regs

#var.omit <- c("pop","D2","D3","D4")
#col.labels <- c("Overall", "Group 1", "Group 2", "Group 3", "Group 4")
#vars.x_tab <- vars.x_tab[-unlist(lapply(var.omit, function(x){grep(x,vars.x_tab)}))]

stargazer(LREG,
          #notes= tit.name,
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',31),diag),sqrt),
          omit = var.omit, omit.stat = stat.omit,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.caption = var.y_cap,
          dep.var.labels.include = FALSE,
          covariate.labels = cov.labels, #order = ord,
          column.labels = col.labels, model.numbers = FALSE,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE)
}


cov <- c("Log(ben. fam.)*D1(1= North)","Log(ben. fam.)*D2(1= Northeast)")

col <- c("Overall", "1st Sector", "2nd Sector", "3rd Sector", "Public Sector")
panel.set.out <- star_panel(star.table(REGS_SET[[1]], col.labels=col, cov.labels = cov), 
                            star.table(REGS_SET[[2]],
                                       var.omit=c("pop", "D1", "D2", "D3"), col.labels=col),
                            star.table(REGS_SET[[3]], col.labels=col), 
                            star.table(REGS_SET[[4]], col.labels=col),
                            star.table(REGS_SET[[5]], 
                                       var.omit=c("pop", "D1", "D2", "D5"), col.labels=col),
                            panel.names = c("Heterogeneity by region", 
                                            "Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration", 
                                            "Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_set01234.tex", headers = FALSE)


col <- c("Overall", "Size 1", "Size 2", "Size 3", "Size 4")
panel.tam.out <- star_panel(star.table(REGS_TAM[[1]], col.labels=col, cov.labels = cov), 
                            star.table(REGS_TAM[[2]], 
                                       var.omit=c("pop", "D1", "D2", "D3"), col.labels=col),
                            star.table(REGS_TAM[[3]], col.labels=col), 
                            star.table(REGS_TAM[[4]], col.labels=col),
                            star.table(REGS_TAM[[5]], 
                                       var.omit=c("pop", "D1", "D2", "D5"), col.labels=col),
                            panel.names = c("Heterogeneity by region", 
                                            "Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration", 
                                            "Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.tam.out, file = "Tabelas de Resultados/temp/pan5_tam01234.tex", headers = FALSE)


col <- c("Overall", "Range 1", "Range 2", "Range 3", "Range 4")
panel.rem.out <- star_panel(star.table(REGS_REM[[1]], col.labels=col, cov.labels = cov), 
                            star.table(REGS_REM[[2]], 
                                       var.omit=c("pop", "D1", "D2", "D3"), col.labels=col),
                            star.table(REGS_REM[[3]], col.labels=col), 
                            star.table(REGS_REM[[4]], col.labels=col),
                            star.table(REGS_REM[[5]],
                                       var.omit=c("pop", "D1", "D2", "D5"), col.labels=col),
                            panel.names = c("Heterogeneity by region", 
                                            "Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration", 
                                            "Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.rem.out, file = "Tabelas de Resultados/temp/pan5_rem01234.tex", headers = FALSE)


col <- c("Overall", "Level 1", "Level 2", "Level 3", "Level 4")
panel.esc.out <- star_panel(star.table(REGS_ESC[[1]], col.labels=col, cov.labels = cov), 
                            star.table(REGS_ESC[[2]], 
                                       var.omit=c("pop", "D1", "D2", "D3"), col.labels=col),
                            star.table(REGS_ESC[[3]], col.labels=col), 
                            star.table(REGS_ESC[[4]], col.labels=col),
                            star.table(REGS_ESC[[5]], 
                                       var.omit=c("pop", "D1", "D2", "D5"), col.labels=col),
                            panel.names = c("Heterogeneity by region", 
                                            "Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration", 
                                            "Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.esc.out, file = "Tabelas de Resultados/temp/pan5_esc01234.tex", headers = FALSE)







#### PAINEIS 2 x 2
cov <- c("Log(ben. fam.)*D1(1= North)","Log(ben. fam.)*D2(1= Northeast)","Log(ben. fam.)*D3(1= South)",
         "Log(ben. fam.)*D4(1= Southeast)","Log(ben. fam.)*D5(1= Center-West)")

col <- c("Overall", "1st Sector", "2nd Sector", "3rd Sector", "Public Sector")
panel.set.out <- star_panel(star.table(REGS_SET[[1]], var.omit=c("pop"), col.labels=col, cov.labels = cov), 
                            panel.names = c("Heterogeneity by region"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_set_reg.tex", headers = FALSE)

                            
panel.set.out <- star_panel(star.table(REGS_SET[[2]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_SET[[3]], var.omit=c("pop"), col.labels=col), 
                            panel.names = c("Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_set_xy.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_SET[[4]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_SET[[5]], var.omit=c("pop"), col.labels=col),
                            panel.names = c("Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_set_pibpop.tex", headers = FALSE)




col <- c("Overall", "Size 1", "Size 2", "Size 3", "Size 4")
panel.set.out <- star_panel(star.table(REGS_TAM[[1]], var.omit=c("pop"), col.labels=col, cov.labels = cov), 
                            panel.names = c("Heterogeneity by region"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_tam_reg.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_TAM[[2]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_TAM[[3]], var.omit=c("pop"), col.labels=col), 
                            panel.names = c("Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_tam_xy.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_TAM[[4]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_TAM[[5]], var.omit=c("pop"), col.labels=col),
                            panel.names = c("Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_tam_pibpop.tex", headers = FALSE)




col <- c("Overall", "Range 1", "Range 2", "Range 3", "Range 4")
panel.set.out <- star_panel(star.table(REGS_REM[[1]], var.omit=c("pop"), col.labels=col, cov.labels = cov), 
                            panel.names = c("Heterogeneity by region"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_rem_reg.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_REM[[2]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_REM[[3]], var.omit=c("pop"), col.labels=col), 
                            panel.names = c("Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_rem_xy.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_REM[[4]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_REM[[5]], var.omit=c("pop"), col.labels=col),
                            panel.names = c("Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_rem_pibpop.tex", headers = FALSE)


col <- c("Overall", "Level 1", "Level 2", "Level 3", "Level 4")
panel.set.out <- star_panel(star.table(REGS_ESC[[1]], var.omit=c("pop"), col.labels=col, cov.labels = cov), 
                            panel.names = c("Heterogeneity by region"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_esc_reg.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_ESC[[2]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_ESC[[3]], var.omit=c("pop"), col.labels=col), 
                            panel.names = c("Heterogeneity by beneficiaries concentration", 
                                            "Heterogeneity by formal employment concentration"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_esc_xy.tex", headers = FALSE)


panel.set.out <- star_panel(star.table(REGS_ESC[[4]], var.omit=c("pop"), col.labels=col),
                            star.table(REGS_ESC[[5]], var.omit=c("pop"), col.labels=col),
                            panel.names = c("Heterogeneity by per capita income",
                                            "Heterogeneity by population"))
tex_write(panel.set.out, file = "Tabelas de Resultados/temp/pan5_esc_pibpop.tex", headers = FALSE)

