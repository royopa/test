#install.packages("lfe")
#install.packages("stargazer")
#install.packages("dplyr")
#install.packages("devtools")
#install.packages("gridExtra")
#install.packages("ggplot2")
devtools::install_github("ChandlerLutz/starpolishr")
library(starpolishr)
library(lfe)
library(stargazer)
library(dplyr)
library(gridExtra)
library(ggplot2)
rm(list=ls())
setwd("E:/Dissertacao/")
tables.dest <- "Tabelas de Resultados/temp/"

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
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   
                                 controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })
  
  sep <- "tam"
  vars <- c(1,grep(sep,vars.y))
  REGS_TAM[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   
                                 controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })
  
  sep <- "rem"
  vars <- c(1,grep(sep,vars.y))
  REGS_REM[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   
                                 controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })
  
  sep <- "esc"
  vars <- c(1,grep(sep,vars.y))
  REGS_ESC[[i]] <- lapply(vars, function (x) {
          felm(as.formula(paste0("log(1 + base[,vars.y[x]]) ~ D1:X + D2:X + D3:X + D4:X + D5:X",   
                                 controls_tab,  "|ID+ANO:TEND|0|CLUS")),   base)
  })  
}

#input: lista de regressões
#output: um data.frame com todos os coeficientes por quebra e por v. dependente
coef_matrix <- function(regs.list, x.axis=c("1st","2nd","3rd","4th","5th"),
                        cols=c("tot","class1","class2","class3","class4"), brk="break"){

nc <- length(cols); nx <- length(x.axis)
coef <- unlist(lapply(regs.list,'[[',7))
se <- unlist(lapply(lapply(lapply(regs.list,'[[',30),diag),sqrt))
se <- se[!se==0]

id_pop <- (1+nc)*(1:nx)-nc; coef <- coef[-id_pop]; se <- se[-id_pop]
vars <- rep(x.axis, times=nc); cl <- rep(cols, each=nx)
up = coef + 2.65 * se
lo = coef - 2.65 * se

data.frame(brk, vars, cl, coef, se, up, lo)
}


#input: um data.frame com todos os coeficientes por quebra e por v. dependente
#output: um grafico de linhas com todos os coeficientes
graphs <- function(df){
        
ggplot(df) + 
        geom_errorbar(aes(x = vars, ymax = up, ymin = lo, group=brk, color=cl)) +
        geom_point(aes(x = vars, y = coef, color=cl), shape=3) +
        geom_point(aes(x = vars, y = coef.over), shape=18) +
        geom_hline(aes(yintercept=0), linetype="dashed") +
        facet_grid(cl~brk, scales="free") + 
        #ylim(-0.2, 0.4) +
        labs(x = "Dep. Variable", y = "Coefficients", color = "Employment") +
        theme(legend.position="none")
}

dep <- c("N","NE","SE","S","CW")

cl <- c("Overall","1st Sector","2nd Sector","3rd Sector","Public Sector")
set_df <- rbind(coef_matrix(REGS_SET[[1]], cols=cl, x.axis=dep, brk="Region"), 
                coef_matrix(REGS_SET[[2]], cols=cl, brk="Beneficiaries"), 
                coef_matrix(REGS_SET[[3]], cols=cl, brk="Formal Employment"), 
                coef_matrix(REGS_SET[[4]], cols=cl, brk="Personal Income"), 
                coef_matrix(REGS_SET[[5]], cols=cl, brk="Population"))

set_df$cl = factor(set_df$cl, levels(set_df$cl)[c(1:3,5,4)])
set_df$vars = factor(set_df$vars, levels(set_df$vars)[c(2,3,1,5,4,6:10)])

cl <- c("Overall","Size 1","Size 2","Size 3","Size 4")
tam_df <- rbind(coef_matrix(REGS_TAM[[1]], cols=cl, x.axis=dep, brk="Region"),
                coef_matrix(REGS_TAM[[2]], cols=cl, brk="Beneficiaries"),
                coef_matrix(REGS_TAM[[3]], cols=cl, brk="Formal Employment"),
                coef_matrix(REGS_TAM[[4]], cols=cl, brk="Personal Income"),
                coef_matrix(REGS_TAM[[5]], cols=cl, brk="Population"))

tam_df$cl = factor(tam_df$cl,levels(tam_df$cl)[c(2:5,1)])
tam_df$vars = factor(tam_df$vars, levels(tam_df$vars)[c(2,3,1,5,4,6:10)])

cl <- c("Overall","Range 1","Range 2","Range 3","Range 4")
rem_df <- rbind(coef_matrix(REGS_REM[[1]], cols=cl, x.axis=dep, brk="Region"),
                coef_matrix(REGS_REM[[2]], cols=cl, brk="Beneficiaries"),
                coef_matrix(REGS_REM[[3]], cols=cl, brk="Formal Employment"),
                coef_matrix(REGS_REM[[4]], cols=cl, brk="Personal Income"),
                coef_matrix(REGS_REM[[5]], cols=cl, brk="Population"))

rem_df$cl = factor(rem_df$cl,levels(rem_df$cl)[c(2:5,1)])
rem_df$vars = factor(rem_df$vars, levels(rem_df$vars)[c(2,3,1,5,4,6:10)])

cl <- c("Overall","Level 1","Level 2","Level 3","Level 4")
esc_df <- rbind(coef_matrix(REGS_ESC[[1]], cols=cl, x.axis=dep, brk="Region"),
                coef_matrix(REGS_ESC[[2]], cols=cl, brk="Beneficiaries"),
                coef_matrix(REGS_ESC[[3]], cols=cl, brk="Formal Employment"),
                coef_matrix(REGS_ESC[[4]], cols=cl, brk="Personal Income"),
                coef_matrix(REGS_ESC[[5]], cols=cl, brk="Population"))

esc_df$vars = factor(esc_df$vars, levels(esc_df$vars)[c(2,3,1,5,4,6:10)])

ov_df <- set_df[set_df$cl == "Overall", ]
set_df <- set_df[!set_df$cl == "Overall", ]; set_df <- merge(set_df, ov_df, by=c("brk","vars"), suffixes = c("",".over"))
tam_df <- tam_df[!tam_df$cl == "Overall", ]; tam_df <- merge(tam_df, ov_df, by=c("brk","vars"), suffixes = c("",".over"))
rem_df <- rem_df[!rem_df$cl == "Overall", ]; rem_df <- merge(rem_df, ov_df, by=c("brk","vars"), suffixes = c("",".over"))
esc_df <- esc_df[!esc_df$cl == "Overall", ]; esc_df <- merge(esc_df, ov_df, by=c("brk","vars"), suffixes = c("",".over"))

#ggsave(file ="Tabelas de Resultados/temp/graph_set_5x5.png", graphs(set_df), scale=1.4)
#ggsave(file ="Tabelas de Resultados/temp/graph_tam_5x5.png", graphs(tam_df), scale=1.4)
#ggsave(file ="Tabelas de Resultados/temp/graph_rem_5x5.png", graphs(rem_df), scale=1.4)
#ggsave(file ="Tabelas de Resultados/temp/graph_esc_5x5.png", graphs(esc_df), scale=1.4)