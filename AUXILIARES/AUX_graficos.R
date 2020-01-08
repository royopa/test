library(lubridate)
library(ggplot2)
library(reshape2)
library(dplyr)
library(chemometrics)

source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/AUX_metricas.R", echo=TRUE)

color1 <- "steelblue4";  color2 <- "darkorange1";  color3 <- "red4"
color4 <- "olivedrab";   color5 <- "red1";         color6 <- "skyblue"
colorbar <- "darkkhaki"

### Month over month: mes, mm3m e serie dessazonalizada em nivel
graph1_mom <- function(series, axis.wider=2, initial.date="2012-01-01"){
  dts <- core_dsz$datas %>% tail(1) %>% as.Date(format="%Y-%m-%d") %>% format("%b/%y")
  
  mom_dsz     <- core_dsz %>% MoM
  mm3mmom_dsz <- core_dsz %>% mm3mMoM

  core_dsz$datas     <- core_dsz$datas %>% as.Date
  mom_dsz$datas      <- mom_dsz$datas %>% as.Date       
  mm3mmom_dsz$datas  <- mm3mmom_dsz$datas %>% as.Date
  
  plot_data <- merge(core_dsz[,c("datas", series)], mom_dsz[,c("datas", series)], by="datas")
  plot_data <- merge(plot_data, mm3mmom_dsz[,c("datas", series)], by="datas")
  
  names(plot_data) <- c("datas", "core_dsz", "mom_dsz", "mm3mmom_dsz")
  plot_data$datas  <- plot_data$datas %>% as.Date
  plot_data <- plot_data[which(plot_data$datas >= initial.date), ]
  
  ### ADJUST
  factor <- (sd(plot_data$mom_dsz)^2/sd_trim(plot_data$mom_dsz, trim=.3))/sd_trim(plot_data$core_dsz, trim=.1)
  level  <- mean(plot_data$core_dsz)
  plot_data$core_dsz <- (plot_data$core_dsz - level) * factor
  
  g <- ggplot(plot_data) + 
    geom_bar(aes(x=datas, y=mom_dsz, color=colorbar), stat = "identity", fill="white", width = 18) + 
    geom_line(aes(x=datas, y=core_dsz, color=color1), group = 1, size=1) + 
    geom_line(aes(x=datas, y=mm3mmom_dsz, color=color2), group = 1, size=1) + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1), 
                       sec.axis = sec_axis(~. *factor^(-1) + level)) + 
    scale_x_date(date_breaks = "years" , date_labels = "%Y") + 
    scale_color_identity(name = "", guide = "legend",
                         labels = c("MoM", "MM3mMoM", "Series Dessaz (dir.)"),
                         breaks = c(colorbar, color2, color1)) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$mom_dsz), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position = "bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - ", nms[which(vars_select == series)], " (", dts,")"),
         caption=fonte)  
  return(g)}


### Quarter over Quarter: tri
graph2_qoq <- function(series, axis.wider=2, initial.date="2012-01-01"){
  dts <- core_dsz$datas %>% tail(1) %>% as.Date(format="%Y-%m-%d") %>% format("%b/%y")
  
  qoq_dsz        <- core_dsz %>% QoQ
  qoq_dsz$datas  <- qoq_dsz$datas %>% as.Date

  id_dts         <- which(month(qoq_dsz$datas) %in% c(3,6,9,12))
  plot_data      <- qoq_dsz[,c("datas", series)]
  plot_data      <- plot_data[id_dts, ]
  plot_data      <- plot_data[which(plot_data$datas >= initial.date), ]
  
  names(plot_data) <- c("datas", "qoq_dsz")
  
  g <- ggplot(plot_data) + 
    geom_bar(aes(x=datas, y=qoq_dsz, color=color1), position="dodge", stat="identity", fill=color1, width = 32) + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    scale_color_identity(name = "", guide = "legend",
                         labels = c("QoQ Dessaz."),
                         breaks = c(color1)) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$qoq_dsz), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - Variação Trimestral Dessaz (", dts,")"), caption=fonte)
  return(g)}


#### Year over year: mes, mm3m e mm12m
graph3_yoy <- function(series, axis.wider=2, initial.date="2012-01-01"){
  dts <- core$datas %>% tail(1) %>% as.Date(format="%Y-%m-%d") %>% format("%b/%y")
  
  yoy      <- core %>% YoY
  mm12myoy <- core %>% mm12mYoY
  mm3myoy  <- core %>% mm3mYoY
  
  yoy$datas      <- yoy$datas %>% as.Date       
  mm12myoy$datas <- mm12myoy$datas %>% as.Date
  mm3myoy$datas  <- mm3myoy$datas %>% as.Date
  
  plot_data <- merge(yoy[,c("datas", series)], mm12myoy[,c("datas", series)], by="datas")
  plot_data <- merge(plot_data, mm3myoy[,c("datas", series)], by="datas")
  
  names(plot_data) <- c("datas", "yoy", "mm12myoy", "mm3myoy")
  plot_data$datas <- plot_data$datas %>% as.Date
  plot_data <- plot_data[which(plot_data$datas >= initial.date), ]
  
  g <- ggplot(plot_data) + 
    geom_bar(aes(x=datas, y=yoy, color=colorbar), stat = "identity", fill="white", width = 18) + 
    geom_line(aes(x=datas, y=mm12myoy, color=color1), group = 1, size=1) + 
    geom_line(aes(x=datas, y=mm3myoy, color=color2), group = 1, size=1) + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1), sec.axis = waiver()) + 
    scale_x_date(date_breaks = "years" , date_labels = "%Y") + 
    scale_color_identity(name = "", guide = "legend",
                         labels = c("YoY", "MM3mYoY", "MM12mYoY"),
                         breaks = c(colorbar, color2, color1)) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$yoy), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - ", nms[which(vars_select == series)], " (", dts,")"),
         caption=fonte)  
  return(g)}


### Series dessazonalizadas: em nivel e media movel 3 meses
graph4_mm3mniv <- function(series, axis.wider=2, initial.date="2012-01-01"){
  dts <- core_dsz$datas %>% tail(1) %>% as.Date(format="%Y-%m-%d") %>% format("%b/%y")
  
  mm3m_dsz <- core_dsz %>% MM3m
  
  core_dsz$datas  <- core_dsz$datas %>% as.Date
  mm3m_dsz$datas  <- mm3m_dsz$datas %>% as.Date       
  
  plot_data <- merge(core_dsz[,c("datas", series)], mm3m_dsz[,c("datas", series)], by="datas")
  
  names(plot_data) <- c("datas", "core_dsz", "mm3m_dsz")
  plot_data$datas <- plot_data$datas %>% as.Date
  plot_data <- plot_data[which(plot_data$datas >= initial.date), ]
  plot_data <- melt(plot_data, id="datas")
  
  names <- nms[which(vars_select == series)]
  
  g <- ggplot(plot_data) + geom_line(aes(x=datas, y=value, color=variable), size=1) +
    scale_x_date(date_breaks = "years" , date_labels = "%Y") + 
    scale_color_manual(name="", values=c(color1, color2), labels=c("Series Dessaz", "MM3m")) +
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$value), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - ", nms[which(vars_select == series)], " (", dts,")"), caption=fonte)  
  return(g)}


### Quebra setorial: series dessazonalizadas em nivel
graph5_mseries <- function(vars, axis.wider=2, initial.date="2012-01-01"){
  #vars_pim <- c("bens_capital", "bens_inter", "bens_cons_dur", "bens_cons_semi")
  dts <- core_dsz$datas %>% tail(1) %>% as.Date(format="%Y-%m-%d") %>% format("%b/%y")
  
  core_dsz$datas <- core_dsz$datas %>% as.Date
  plot_data <- core_dsz[which(core_dsz$datas >= initial.date), ]
  
  plot_data <- plot_data[,c("datas", vars)]
  plot_data <- melt(plot_data, id="datas")
  
  names <- nms[which(vars_select %in% vars)]
  
  g <- ggplot(plot_data) + geom_line(aes(x=datas, y=value, color=variable), size=1) +
    scale_x_date(date_breaks = "years" , date_labels = "%Y") +
    scale_color_manual(name="", values=c(color1, color2, color3, color4, 
                                         color5, color6), labels=names) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$value), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema," - Setorial (", dts,")"), caption=fonte)  
  return(g)}


### Year to Date: última observação disponível
graph6_ytd <- function(vars, initial.date="2012-01-01"){
  #vars_pmc <- c("combst", "hiper_sup", "tecidos", "mov_eletro_tot", "farmaceuticos", "livros_jornais", 
  #              "mat_escrit", "outros_art_dom", "veiculos", "mat_construcao")
  
  ytd   <- core %>% YTD_lvl
  
  date  <- ytd$datas %>%  tail(1) %>% as.Date
  names <- factor(nms[which(vars_select %in% vars)], levels = rev(nms[which(vars_select %in% vars)] ))
  
  plot_data <- ytd[,vars] %>% tail(1);  plot_data <- data.frame(names, t(plot_data))
  names(plot_data) <- c("names", "values")
  
  g <- ggplot(plot_data, aes(x=names, y=values)) + 
    geom_bar(position="dodge",stat="identity", width=.6, fill=color1) + coord_flip() + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) + theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position = "bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - Variação real acumulada no ano até ", 
                                  format(date, "%b/%Y")), caption=fonte)
  return(g)}
