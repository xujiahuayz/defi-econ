library(data.table)
library(ggplot2)
library(stringr)
library(bit64)
library(reshape2)
library(lubridate)
library(stargazer)
library(lfe)
library(Hmisc)


output_folder <- "/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/4_tables/v2/"



### Load in the data ###
########################

df <- fread("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/3_cleaned_data/defi_data_v2_20220829.csv")


## Checking Missings ##

#x <- df[,.(avve_missing = sum(is.na(avve_borrow)), 
#           compound_missing = sum(is.na(compound_total_supply)),
#           price_missing = sum(is.na(price))),
#        by = .(token)]

#write.csv(x, "/Users/yuantian/123 Dropbox/Yuan Tian/defi/3_cleaned_data/missing_summary.csv")


## Table 1 Dependent Variable Summary Stats

stargazer(df[,c("eigencentrality_in","eigencentrality_out","trading_volume_total","total_tvl")],
          title = 'Dependent Variable Summary Statistics',
          out = paste0(output_folder,'y_var_stats.tex'))

## Table 1A Dependent Variable Summary Stats by 4 coins

tmp <- df
tmp[stable == 1,group :=1]
tmp[token == "WETH",group := 2]
tmp[is.na(group), group := 3]
tmp <- tmp[,c("eigencentrality_in","eigencentrality_out","trading_volume_total","total_tvl","group")]

stargazer(tmp[group ==1,])
stargazer(tmp[group ==2,])
stargazer(tmp[group ==3,])

## Table 1B Summary Stats by TOP 5 Eigenvector_centrality


### Confirm the top 5: WETH,USDC,USDT,DAI,FEI

tmp <- df[,.( o=mean(eigencentrality_out+eigencentrality_in)),by =.(token)]

tmp <- df[,c('token',"eigencentrality_in","eigencentrality_out","trading_volume_total","total_tvl")]

stargazer(tmp[token == 'USDC',])
stargazer(tmp[token == 'USDT',])
stargazer(tmp[token == 'DAI',])
stargazer(tmp[token == 'FEI',])
stargazer(tmp[!(token %in% c('FEI','USDC','USDT','DAI','WETH')),])

## Table 2 Dependent Variable Correlation

correlation.matrix <- cor(df[,c("eigencentrality_in","eigencentrality_out",
                                "trading_volume_total","total_tvl")])

stargazer(correlation.matrix, header=FALSE, type="latex", 
          title="Correlation of Dependent Variables",
          out = paste0(output_folder,'y_var_cor.tex'))

rcorr(as.matrix(df[,c("eigencentrality_in","eigencentrality_out",
                      "trading_volume_total","total_tvl")]),type="pearson")

## Table 3 Independent Variable Summary Stats

stargazer(df[,c('gas_price','gas_price_volatility','price','price_volatility','mcap',
                'borrow_compound','lend_compound','borrow_aave','lend_aave')],
          title = 'Independent Variable Summary Statistics',
          out = paste0(output_folder,'x_var_stats.tex'))

## Table 4 Independent Variable Correlation Matrix
correlation.matrix <- cor(df[,c('gas_price','gas_price_volatility','price','price_volatility','mcap',
                                'borrow_compound','lend_compound','borrow_aave','lend_aave')],use="complete.obs")


rcorr(as.matrix(df[,c('gas_price','gas_price_volatility','price','price_volatility','mcap',
                      'borrow_compound','lend_compound','borrow_aave','lend_aave')]),type="pearson")

stargazer(correlation.matrix, header=FALSE, type="latex", 
          title="Correlation of Independent Variables",
          out = paste0(output_folder,'x_var_cor.tex'))


### Time series graphs ###

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = eigencentrality_in)) + 
 geom_line(aes(color = token), size = 0.5) +
 theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/eigen_in.png",h = 3.5, w = 6, units = "in")

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = eigencentrality_out)) + 
  geom_line(aes(color = token), size = 0.5) +
  theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/eigen_out.png",h = 3.5, w = 6, units = "in")

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = total_tvl)) + 
  geom_line(aes(color = token), size = 0.5) +
  theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/total_tvl.png",h = 3.5, w = 6, units = "in")

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = trading_volume_total)) + 
  geom_line(aes(color = token), size = 0.5) +
  theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/trading_volume_total.png",h = 3.5, w = 6, units = "in")

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = mcap)) + 
  geom_line(aes(color = token), size = 0.5) +
  theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/mcap.png",h = 3.5, w = 6, units = "in")

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = borrow_total)) + 
  geom_line(aes(color = token), size = 0.5) +
  theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/defi_borrow.png",h = 3.5, w = 6, units = "in")

ggplot(df[token %in% c('FEI','USDC','USDT','DAI','WETH'),], aes(x = date, y = lend_total)) + 
  geom_line(aes(color = token), size = 0.5) +
  theme_classic()

ggsave("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/1_graph/defi_lend.png",h = 3.5, w = 6, units = "in")


