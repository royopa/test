setwd("C:/Users/PIETCON/Documents/Data")
#t <- seq(as.Date("1996/1/1"), as.Date("2018/9/1"), by = "quarter")
#### NÚCLEOS de IPCA (calculo da MCM)
ipca <- as.data.frame(read_excel("PRCCORE2.xls", sheet = "IPCA (Var)", skip = 3))
ipca <- ipca[2:(which(ipca[,1] == "Nome da Série: IPCA - Núcleos")-2),]
names(ipca) <- c("date", "ipca", "ipca_administ_tot", "ipca_livres_tot", 
                      "ipca_cat_n_dur", "ipca_cat_semi_dur", "ipca_cat_dur", 
                      "ipca_cat_serv", "ipca_com_trad", "ipca_com_ntrad", "ipca_bc_alim",
                      "ipca_bc_serv", "ipca_bc_ind", "ipca_bc_subj_ali", "ipca_bc_subj_serv",
                      "ipca_bc_subj_ind", "ipca_nuc_dp", "ipca_nuc_ms", "ipca_nuc_ma", "ipca_nuc_ex0", 
                      "ipca_nuc_ex1", "ipca_nuc_ex2", "ipca_nuc_ex3", "ipca_difusao", "ipca_serv_tot",
                      "ipca_serv_trab", "ipca_serv_div", "ipca_serv_ali", 
                      "ipca_serv_pass", "ipca_serv_subj", "ipca_difusao_serv")
for (i in 2:dim(ipca)[2]){
            ipca[which(ipca[,i] == "nd"),i] <- 0
            ipca[,i] <- as.numeric(ipca[,i])}
ipca$date <- seq(as.Date("1996/1/1"), as.Date("2018/9/1"), by = "month")
#ipca <- ipca[which(ipca$date %in% t), ]

#IPCA-DP - Núcleo de dupla ponderação: ajusta os pesos originais de cada item de acordo com a sua volatilidade relativa, procedimento que reduz a importância de componentes mais voláteis.
#IPCA-MS - Núcleo de médias aparadas com suavização: são suavizados nove itens com variações infrequentes. Segue a metodologia do IPCA-MA.
#IPCA-MA - Núcleo por médias aparadas: exclui os itens cuja variação mensal se situe, na distribuição, acima do percentil 80 ou abaixo do percentil 20. Os 60% restantes são utilizados para calcular a variação mensal do núcleo.
#IPCA-EX0 - exclui Alimentação no Domicílio e Preços Administrados.
#IPCA-EX1 - exclui 10 dos 16 itens do subgrupo Alimentação no Domicílio, além dos itens combustíveis domésticos e combustíveis de veículos.
#IPCA-EX2 - agrega as medidas subjacentes de Alimentação no Domicílio, Serviços e Bens Industriais.
#IPCA-EX3 - agrega as medidas subjacentes de  Serviços e Bens Industriais.