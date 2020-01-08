library(knitr)
library(kableExtra)
library(webshot)
#webshot::install_phantomjs()
library(tools)

source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/AUX_metricas.R", echo=TRUE)

tabela_resumo <- function(df, cls=2, path, path_end, table_name, indent_line=1, vheight = 744){

  ### Montando a Tabela
  rws <- nrow(df)
  dts <- df$datas[rws]
  r18 <- which(df[,1] == "2018-12-01"); r17 <- which(df[,1] == "2017-12-01")
  r16 <- which(df[,1] == "2016-12-01"); r15 <- which(df[,1] == "2015-12-01")
  r14 <- which(df[,1] == "2014-12-01"); r13 <- which(df[,1] == "2013-12-01")

  mom <- MoM(df, yoy=FALSE)
  qoq <- QoQ(df, yoy=FALSE) 
  yoy <- MoM(df, yoy=TRUE)
  mm12myoy <- MoM(MM(df, periods=12), yoy=TRUE)
  ytd <- ytd_ave(AnAve(df))

  tabela <- data.frame(names(df)[cls], 
                       t(mom[nrow(mom),cls]), 
                       t(mom[nrow(mom)-1,cls]), 
                       t(mom[nrow(mom)-2,cls]), 
                       t(qoq[nrow(qoq),cls]), 
                       t(yoy[nrow(yoy),cls]), 
                       t(mm12myoy[nrow(mm12myoy),cls]), 
                       t(ytd[rws,cls]), 
                       t(ytd[r18,cls]), 
                       t(ytd[r17,cls]), 
                       t(ytd[r16,cls]), 
                       t(ytd[r15,cls]), row.names=NULL)
  tabela[,-1] <- round(tabela[,-1]*100,1)
  names(tabela) <- c(dts,"MoM","(-1)","(-2)","QoQ","YoY","12m","YtD",2018:2015)

  ### Exportando a tabela em formate HTML
  kable(tabela, format="html") %>% 
    kable_styling(bootstrap_options=c("striped","hover","responsive", "condensed"), 
                  full_width = F, font_size = 20) %>% 
    row_spec(0, bold = T, align="center", background="navy", color="white") %>% 
    row_spec(indent_line, bold = T, background="royalblue", color="white") %>% 
    add_indent(indent_line) %>% 
    save_kable(file=paste0(path, path_end, table_name,".html"))

  ### Salvando a tabela em formato de imagem
  setwd(paste0(path, path_end))
  webshot(paste0(table_name, ".html"), paste0(table_name, ".png"), vheight=350)}