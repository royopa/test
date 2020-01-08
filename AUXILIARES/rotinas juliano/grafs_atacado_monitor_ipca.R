source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_CEAGESP.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_CEPEA.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_IPCA.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_MonitorFGV.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/estimadores/EST_reg_allY_multX.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/AUX_merge_list.R", echo=TRUE)

source("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/4.CEAGESP/rotinas/atualiza_CEAGESP.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/5.CEPEA/rotinas/downloader_CEPEA.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/5.CEPEA/rotinas/compiler_CEPEA.R", echo=TRUE)

library(ggplot2); library(writexl)
  
save_path <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/rotinas juliano/"

#titles <- c("Batata", "Tomate", "Cebola", "Cenoura")
#itens_atac <- c("BATATA_BENEFCOMUM_ESPECIAL", "TOMATE_MADURO_EXTRAAA",
#                "CEBOLA_STACATARINA_GRAUDA", "CENOURA__EXTRAAA")
#itens_ipca <- c(1103003, 1103028, 1103043, 1103044)
#lags_ipca  <- c(7, 7, 7, 7)

titles <- c("Arroz", "Batata", "Tomate", "Cebola", "Cenoura", "Abacaxi", "Banana",
            "Laranja", "Mamao", "Uva", "Carne de Porco", "Contrafile", "Chã", "Alcatra", "Patinho",
            "Músculo", "Pã", "Acém", "Costela", "Frango Inteiro", "Frango Pedaço", 
            "Ovo", "Leite")
itens_atac <- c("arroz_brl", "BATATA_BENEFCOMUM_ESPECIAL", "TOMATE_MADURO_EXTRAAA",
                "CEBOLA_STACATARINA_GRAUDA", "CENOURA__EXTRAAA", "ABACAXI_PEROLA_AGRAUDO",
                "BANANA_PRATAMG", "LARANJA_LIMA_A1013DZ", "MAMAO_FORMOSA_B", "UVA_BRASIL_EXTRAA",
                "suinos_rs", "boi_brl", "boi_brl", "boi_brl", "boi_brl", "boi_brl", "boi_brl", 
                "boi_brl", "boi_brl", "frango_resfriado_sp_brl", "frango_resfriado_sp_brl", 
                "OVOS_BRANCO_EXTRA", "leite_pbruto_go")
itens_ipca <- c(1101002, 1103003, 1103028, 1103043, 1103044, 1106003, 1106008, 1106039, 
                1106018, 1106028, 1107018, 1107084, 1107087, 1107088, 1107089, 
                1107093, 1107094, 1107095, 1107099, 1110009, 1110010, 1110044, 1111004)
itens_cepea <- c("arroz_brl", "suinos_rs", "boi_brl", "frango_resfriado_sp_brl", "frango_resfriado_sp_brl", 
               "leite_pbruto_go")
lags_ipca  <- c(23, 7, 7, 7, 7, 7, 7, 16, 7, 7, 7, 10, 11, 7, 19, 22, 26, 17, 14, 13, 12, 7, 7)

#titles <- "Carne"
#itens_atac  <- c("boi_brl")
#itens_ipca  <- 1107
#itens_cepea <- c("boi_brl")
#lags_ipca <- 45

initial.date.graph <- "2019-01-01"
initial.date="2012-01-01"

color1 <- "steelblue4";  color2 <- "darkorange1";  color3 <- "red4"
color4 <- "olivedrab";   color5 <- "red1";         color6 <- "skyblue"

for (i in 1:length(itens_atac)){
  nm_it <- itens_atac[i];  cod_it <- itens_ipca[i]
  item <- titles[i]
  
  if (nm_it %in% itens_cepea){ 
    atac <- readbase_cepea(prods=nm_it, initial.date = initial.date, 
                           carrego=TRUE, mm.days=30, varp30=TRUE)[,1:2]
  } else {atac <- readbase_ceagesp(prods=nm_it, initial.date = initial.date, 
                                   carrego=TRUE, mm.days=30, varp30=TRUE)[,1:2]}
  ipca <- readbase_ipca(itens=cod_it, day="all", var=TRUE, initial.date = initial.date)  
  peso <- readbase_ipca(itens=cod_it, day="all", var=FALSE, initial.date = initial.date)[,2] %>% tail(1)  
  mon_med <- readbase_monitor(itens=cod_it, media=TRUE, initial.date = initial.date)
  mon_pta <- readbase_monitor(itens=cod_it, media=FALSE, initial.date = initial.date)  
  
  names(atac)[2] <- "Atacado"; names(ipca)[2] <- "IPCA"  
  names(mon_med)[2] <- "mediaFGV"; names(mon_pta)[2] <- "pontaFGV"

  atac$datas <- atac$datas %>% as.Date
  atac$datas <- atac$datas + lags_ipca[i]
  atac$datas <- atac$datas %>% as.character  

  alt <- reg_all_mult(dfY=mon_med, dfX=atac, lag=0, initial.date = "2012-01-31")
  rsq  <- alt[grep("rsq",  names(alt))] %>% as.numeric()
  coef <- alt[grep("coef", names(alt))] %>% as.numeric()
  std  <- alt[grep("std",  names(alt))] %>% as.numeric()

  atac$Proj    <- atac$Atacado*coef

  plot_data <- merge_list(list(atac, ipca, mon_med, mon_pta))
  plot_data <- plot_data[plot_data$data > initial.date.graph, ]
  plot_data$datas <- plot_data$datas %>% as.Date
  
  if (i == 1){ 
    AGG <- cbind(tail(plot_data[plot_data$data < today() +30,1],240), 
                 tail(plot_data[plot_data$data < today() +30,-1],240) * peso)
    p_AGG <- peso
  } else { 
    AGG[,-1] <- AGG[,-1] + tail(plot_data[plot_data$data < today() +30,-1], 240) * peso 
    p_AGG <- p_AGG + peso }

  windows()
  ggplot(plot_data) + 
    geom_point(aes(x=datas, y=IPCA)) + 
    geom_line(aes(x=datas, y=mediaFGV, color=color2), group=1, size=1) + 
    geom_line(aes(x=datas, y=pontaFGV, color=color5), group=1) + 
    geom_line(aes(x=datas, y=Proj, color=color1), group=1, size=1) +  
    scale_color_identity(name = "", guide = "legend",
                         labels = c("MediaFGV", "PontaFGV", "Proj.")) +
    labs(title=paste0("Projeção - ", item))
  ggsave(paste0(save_path,"graphs/", item, ".png"))
  
  rm(atac, ipca, mon_med, mon_pta, plot_data)}

AGG[,-1] <- AGG[,-1] / p_AGG 
names(AGG)[1] <- "datas"

windows()
ggplot(AGG) + 
  geom_point(aes(x=datas, y=IPCA)) + 
  geom_line(aes(x=datas, y=mediaFGV, color=color2), group=1, size=1) + 
  geom_line(aes(x=datas, y=pontaFGV, color=color5), group=1) + 
  geom_line(aes(x=datas, y=Proj, color=color1), group=1, size=1) +  
  scale_color_identity(name = "", guide = "legend",
                       labels = c("MediaFGV", "PontaFGV", "Proj.")) +
  labs(title=paste0("Projeção - Agregado"))
ggsave(paste0(save_path,"graphs/Agregado.png"))

graphics.off()

write_xlsx(AGG, "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/3.MonitorFGV/proj_atacado.xlsx")