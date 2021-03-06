library(readxl)
#### Nome "Indice nacional de precos ao consumidor amplo (IPCA) - Regioes metropolitanas - Brasil - IBGE (DEZ/1993=100)"
#### Origem MCM
#### codigo: "PRCCORE2.xls"
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

nuc_ipca <- as.data.frame(read_excel(paste0(path_data,"MCM/PRCCORE2.xlsx"), 
                                 sheet = "IPCA (Var)", skip = 4))

names <- c("datas", "ipca", "ipca_administ_tot", "ipca_livres_tot", 
           "ipca_cat_n_dur", "ipca_cat_semi_dur", "ipca_cat_dur", 
           "ipca_cat_serv", "ipca_com_trad", "ipca_com_ntrad", "ipca_bc_alim",
           "ipca_bc_serv", "ipca_bc_ind", "ipca_bc_subj_ali", "ipca_bc_subj_serv",
           "ipca_bc_subj_ind", "ipca_nuc_dp", "ipca_nuc_ms", "ipca_nuc_ma", "ipca_nuc_ex0", 
           "ipca_nuc_ex1", "ipca_nuc_ex2", "ipca_nuc_ex3", "ipca_difusao", "ipca_serv_tot",
           "ipca_serv_trab", "ipca_serv_div", "ipca_serv_ali", 
           "ipca_serv_pass", "ipca_serv_subj", "ipca_difusao_serv")

names(nuc_ipca) <- names
nuc_ipca <- nuc_ipca[2:(which(nuc_ipca[,1] == "Nome da S�rie: IPCA - N�cleos")-2),]

for (i in 2:dim(nuc_ipca)[2]){
  nuc_ipca[which(nuc_ipca[,i] == "-"),i] <- 0;    nuc_ipca[which(nuc_ipca[,i] == "nd"),i] <- 0
  nuc_ipca[which(nuc_ipca[,i] == "<NA>"),i] <- 0; nuc_ipca[is.na(nuc_ipca[,i]),i] <- 0
  nuc_ipca[,i] <- as.numeric(nuc_ipca[,i])}

nuc_ipca$datas <- nuc_ipca$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character

#IPCA-DP - N�cleo de dupla pondera��o: ajusta os pesos originais de cada item de acordo com a sua volatilidade relativa, procedimento que reduz a import�ncia de componentes mais vol�teis.
#IPCA-MS - N�cleo de m�dias aparadas com suaviza��o: s�o suavizados nove itens com varia��es infrequentes. Segue a metodologia do IPCA-MA.
#IPCA-MA - N�cleo por m�dias aparadas: exclui os itens cuja varia��o mensal se situe, na distribui��o, acima do percentil 80 ou abaixo do percentil 20. Os 60% restantes s�o utilizados para calcular a varia��o mensal do n�cleo.
#IPCA-EX0 - exclui Alimenta��o no Domic�lio e Pre�os Administrados.
#IPCA-EX1 - exclui 10 dos 16 itens do subgrupo Alimenta��o no Domic�lio, al�m dos itens combust�veis dom�sticos e combust�veis de ve�culos.
#IPCA-EX2 - agrega as medidas subjacentes de Alimenta��o no Domic�lio, Servi�os e Bens Industriais.
#IPCA-EX3 - agrega as medidas subjacentes de  Servi�os e Bens Industriais.