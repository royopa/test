library(lubridate)
library(ggplot2)
library(reshape2)

library(chemometrics) #sd_trim

source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/AUX_metricas.R", echo=TRUE) #MoM, QoQ, MM, YTD
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/AUX_merge_list.R", echo=TRUE) 

color1 <- "steelblue4";  color2 <- "darkorange1";  color3 <- "red4"
color4 <- "olivedrab";   color5 <- "red1";         color6 <- "skyblue"
colorbar <- "darkkhaki"

### Month over month: mes, mm3m e serie dessazonalizada em nivel
graph1_mom <- function(df, axis.wider=2, tema="", fonte="", initial.date="2012-01-01"){
  
  #### Verificando se os dados tem o n.o de colunas correto  
  if (ncol(df) != 2) 
    stop("inputed data.frame must have two columns: one for dates and one for the variable of interest")

  df$datas  <- as.Date(df$datas, format="%Y-%m-%d")
  dts       <- format(tail(df$datas,1), "%b/%y")

  mom       <- MoM(df, yoy=FALSE)
  mm3mmom   <- MM(MoM(df, yoy=FALSE),periods=3)
  
  plot_data <- merge_list(list(df, mom, mm3mmom))

  names(plot_data) <- c("datas", "core", "mom", "mm3mmom")
  plot_data        <- plot_data[which(plot_data$datas >= initial.date), ]
  
  ### ADJUST
  factor <- (sd(plot_data$mom)^2/sd_trim(plot_data$mom, trim=.3))/sd_trim(plot_data$core, trim=.1)
  level  <- mean(plot_data$core)
  plot_data$core <- (plot_data$core - level) * factor
  
  g <- ggplot(plot_data) + 
    geom_bar(aes(x=datas, y=mom, color=colorbar), stat = "identity", fill="white", width = 18) + 
    geom_line(aes(x=datas, y=core, color=color1), group = 1, size=1) + 
    geom_line(aes(x=datas, y=mm3mmom, color=color2), group = 1, size=1) + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1), 
                       sec.axis = sec_axis(~. *factor^(-1) + level)) + 
    scale_x_date(date_breaks = "years" , date_labels = "%Y") + 
    scale_color_identity(name = "", guide = "legend",
                         labels = c("MoM", "MM3mMoM", "Series (dir.)"),
                         breaks = c(colorbar, color2, color1)) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$mom), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position = "bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - ", names(df)[2], " (", dts,")"),
         caption=paste0("Fonte: ", fonte, " e Safra Asset Management"))  
  return(g)}



### Quarter over Quarter: tri
graph2_qoq <- function(df, axis.wider=2, tema="", fonte="", initial.date="2012-01-01"){
  
  #### Verificando se os dados tem o n.o de colunas correto  
  if (ncol(df) != 2) 
    stop("inputed data.frame must have two columns: one for dates and one for the variable of interest")

  df$datas  <- as.Date(df$datas, format="%Y-%m-%d") 
  dts       <- format(tail(df$datas, 1), "%b/%y")
  
  qoq       <- QoQ(df, yoy=FALSE)

  plot_data <- qoq[which(qoq$datas >= initial.date), ]
  
  names(plot_data) <- c("datas", "qoq")
  
  # diferenciando a ultima informação quando a variacao trimestral e parcial
  plot_data$class <- 0
  if (tail(month(plot_data$datas),1) %in% c(1,2,4,5,7,8,10,11)){plot_data$class[nrow(plot_data)] <- 1}
  
  g <- ggplot(plot_data) + 
    geom_bar(aes(x=datas, y=qoq, color="black"), 
             position="dodge", stat="identity", fill=color1, width = 32) + 
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    scale_fill_manual(values=c(color1,color2)) + 
    scale_color_identity(name = "", guide = "legend",
                         labels = c("QoQ"),
                         breaks = c(color1)) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$qoq), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - ", names(df)[2], " (", dts,")"), 
         caption=paste0("Fonte: ", fonte, " e Safra Asset Management"))
  return(g)}



#### Year over year: mes, mm3m e mm12m
graph3_yoy <- function(df, axis.wider=2, tema="", fonte="", initial.date="2012-01-01"){
  
  #### Verificando se os dados tem o n.o de colunas correto  
  if (ncol(df) != 2) 
    stop("inputed data.frame must have two columns: one for dates and one for the variable of interest")

  df$datas <- as.Date(df$datas, format="%Y-%m-%d")
  dts      <- format(tail(df$datas, 1), "%b/%y")
 
  yoy      <- MoM(df, yoy=TRUE)
  mm12myoy <- MoM(MM(df, periods=12), yoy=TRUE)
  mm3myoy  <- MoM(MM(df, periods=3), yoy=TRUE)
  
  plot_data <- merge_list(list(yoy, mm12myoy, mm3myoy))

  names(plot_data) <- c("datas", "yoy", "mm12myoy", "mm3myoy")
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
    labs(x="", y="", title=paste0(tema, " - ", names(df)[2], " (", dts,")"),
         caption=paste0("Fonte: ", fonte, " e Safra Asset Management")) 
  return(g)}



### Series dessazonalizadas: em nivel e media movel 3 meses
graph4_mm3mniv <- function(df, axis.wider=2, tema="", fonte="", initial.date="2012-01-01"){
  
  #### Verificando se os dados tem o n.o de colunas correto  
  if (ncol(df) != 2) 
    stop("inputed data.frame must have two columns: one for dates and one for the variable of interest")
  
  df$datas <- as.Date(df$datas, format="%Y-%m-%d")
  dts      <- format(tail(df$datas, 1), "%b/%y")
  
  mm3m     <- MM(df, periods=3)

  plot_data <- merge_list(list(df, mm3m))
  
  names(plot_data) <- c("datas", "core", "mm3m")
  plot_data <- plot_data[which(plot_data$datas >= initial.date), ]
  plot_data <- melt(plot_data, id="datas")

  g <- ggplot(plot_data) + geom_line(aes(x=datas, y=value, color=variable), size=1) +
    scale_x_date(date_breaks = "years" , date_labels = "%Y") + 
    scale_color_manual(name="", values=c(color1, color2), labels=c("Series", "MM3m")) +
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$value), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "horizontal") +
    labs(x="", y="", title=paste0(tema, " - ", names(df)[2], " (", dts,")"), 
         caption=paste0("Fonte: ", fonte, " e Safra Asset Management"))  
  return(g)}



### Quebra setorial: series dessazonalizadas em nivel
graph5_mseries <- function(df, axis.wider=2, tema="", fonte="", initial.date="2012-01-01"){

  #### Verificando se os dados tem o n.o de colunas correto  
  if (ncol(df) > 7) 
    stop("inputed data.frame must have at most 7 columns: one for dates and six for the variables of interest")
  
  df$datas <- as.Date(df$datas, format="%Y-%m-%d")
  dts      <- format(tail(df$datas, 1), "%b/%y")
  
  plot_data <- df[which(df$datas >= initial.date), ]
  
  plot_data <- melt(plot_data, id="datas")

  g <- ggplot(plot_data) + 
    geom_line(aes(x=datas, y=value, color=variable), size=1) +
    scale_x_date(date_breaks = "years" , date_labels = "%Y") +
    scale_color_manual(name="", values=c(color1, color2, color3, color4, 
                                         color5, color6), labels=names(df)[-1]) + 
    coord_fixed(ratio = max(abs(year(plot_data$datas)), na.rm = TRUE)/
                  (axis.wider*max(abs(plot_data$value), na.rm = TRUE))) + 
    theme_bw() +
    theme(panel.background = element_blank(), 
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(), 
          panel.grid.minor = element_blank(), 
          panel.grid.major = element_line(color="grey", linetype="dashed"),
          legend.position="bottom", legend.direction = "vertical") +
    labs(x="", y="", title=paste0(tema," - Setorial (", dts,")"), 
         caption=paste0("Fonte: ", fonte, " e Safra Asset Management"))  
  return(g)}



### Year to Date: última observação disponível
graph6_ytd <- function(df, tema="", fonte="", initial.date="2012-01-01"){

  df$datas <- as.Date(df$datas, format="%Y-%m-%d")
  dts      <- format(tail(df$datas, 1), "%b/%y")
  ytd      <- YTD(df, rate=FALSE)
  
  names <- names(df)[-1]
  
  plot_data <- data.frame(names, t(tail(ytd[,-1])))
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
    labs(x="", y="", title=paste0(tema, " - Variação real acumulada no ano até ", dts),
         caption=paste0("Fonte: ", fonte, " e Safra Asset Management"))
  return(g)}
