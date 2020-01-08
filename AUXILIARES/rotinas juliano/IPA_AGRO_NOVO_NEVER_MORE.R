library(writexl)

source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_CEAGESP.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_CEPEA.R", echo=TRUE)


arroz <- readbase_cepea(prods="arroz_brl", initial.date="2019-01-01")
df <- arroz
milho <- readbase_cepea(prods="milho_sp_brl", initial.date="2019-01-01")
df <- merge(df, milho, by="datas")
trigo <- readbase_cepea(prods="trigo_pr_brl", initial.date="2019-01-01")
df <- merge(df, trigo, by="datas")
algodao <- readbase_cepea(prods="algodao_brl", initial.date="2019-01-01")
df <- merge(df, algodao, by="datas")

df$cana_acucar <- NA
df$fumo <- NA

soja <- readbase_cepea(prods="soja_pr_brl", initial.date="2019-01-01")
df <- merge(df, soja, by="datas")

abacaxi <- readbase_ceagesp(prods="ABACAXI_HAVAI_AGRAUDO", initial.date="2019-01-01")
df <- merge(df, abacaxi, by="datas")
batata <- readbase_ceagesp(prods="BATATA_COMUM_ESPECIAL", initial.date="2019-01-01")
df <- merge(df, batata, by="datas")

df$feijao <- NA

mandioca <- readbase_cepea(prods="mandioca_farinha_fina_avista_nop", initial.date="2019-01-01")
df <- merge(df, mandioca, by="datas")

tomate <- readbase_ceagesp(prods="TOMATE_CAQUI_EXTRAAA", initial.date="2019-01-01")
df <- merge(df, tomate, by="datas")
laranja <- readbase_ceagesp(prods="LARANJA_LIMA_C1821DZ", initial.date="2019-01-01")
df <- merge(df, laranja, by="datas")

uva <- readbase_ceagesp(prods="UVA_BRASIL_EXTRAA", initial.date="2012-01-01")
df <- merge(df, uva, by="datas")
banana <- readbase_ceagesp(prods="BANANA_MACA_", initial.date="2019-01-01")
df <- merge(df, banana, by="datas")

df$coco <- NA

maca <- readbase_ceagesp(prods="MACANACIONAL_GALA_80150FRUTOS", initial.date="2019-01-01")
df <- merge(df, maca, by="datas")
mamao <- readbase_ceagesp(prods="MAMAO_FORMOSA_A", initial.date="2019-01-01")
df <- merge(df, mamao, by="datas")

cafe <- readbase_cepea(prods="cafe_robusta_brl", initial.date="2019-01-01")
df <- merge(df, cafe, by="datas")

df$cacau <- NA

boi <- readbase_cepea(prods="boi", initial.date="2019-01-01")
df <- merge(df, boi, by="datas")
leite <- readbase_cepea(prods="leite", initial.date="2019-01-01")
df <- merge(df, leite, by="datas")
suinos <- readbase_cepea(prods="suino", initial.date="2019-01-01")
df <- merge(df, suinos, by="datas")
aves <- readbase_cepea(prods="frango", initial.date="2019-01-01")
df <- merge(df, aves, by="datas")

ovos <- readbase_ceagesp(prods="OVOS_BRANCO_GRANDEEMBALADO", initial.date="2019-01-01")
df <- merge(df, ovos, by="datas")

write_xlsx(df, "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/rotinas juliano/IPA_AGRO_NOVO_BASE.xlsx")