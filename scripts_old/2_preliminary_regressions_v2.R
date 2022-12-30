library(data.table)
library(ggplot2)
library(stringr)
library(bit64)
library(reshape2)
library(lubridate)
library(stargazer)
library(lfe)
library(xtable)
library(Hmisc)
## Directory ##

output_folder <- "/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/4_tables/v2/"


## Functions ##

SE <- function(x){
  summary(x)$coefficients[,2]
}

resizebox <- function(st){
  table <- capture.output({st})
  table <- gsub("\\begin{tabular}","\\resizebox{textwidth}{!}{\\begin{tabular}", table,fixed=T)
  table <- gsub("\\end{tabular}","\\end{tabular}}", table,fixed=T)
  st <- cat(table)
}

## Load in the Data ##
df <- fread("/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/3_cleaned_data/defi_data_v2_20220829.csv")

## Pre-regression adjustment and standardization
names(df)[4] <- "Dummy_Stable"
names(df)[23] <- "SnP"
  
df[token == "WETH",Dummy_WETH := 1]
df[token != "WETH",Dummy_WETH := 0]
df[,Dummy_WETH:= as.factor(Dummy_WETH)]

df[,price_ETH_lag := shift(price_ETH), by =.(token)]
df[,price_USD_lag := shift(price_USD), by =.(token)]

df[,log_return_usd := log(price_USD) - log(price_USD_lag)]
df[,log_return_eth := log(price_ETH) - log(price_ETH_lag)]

df[!is.finite(borrow_total_relative), borrow_total_relative := NA]
df[!is.finite(lend_total_relative), lend_total_relative := NA]

### Windsorise

df[eigencentrality_in >= quantile(eigencentrality_in,0.995, na.rm = T)|
    eigencentrality_in <= quantile(eigencentrality_in,0.005, na.rm = T),eigencentrality_in := NA]

df[eigencentrality_out >= quantile(eigencentrality_out,0.995, na.rm = T)|
     eigencentrality_out <= quantile(eigencentrality_out,0.005, na.rm = T),eigencentrality_out := NA]

df[trading_volume_total >= quantile(trading_volume_total,0.995, na.rm = T)|
     trading_volume_total <= quantile(trading_volume_total,0.005, na.rm = T),trading_volume_total := NA]

df[total_tvl >= quantile(total_tvl,0.995, na.rm = T)|
     total_tvl <= quantile(total_tvl,0.005, na.rm = T),total_tvl := NA]

df[log_return_usd >= quantile(log_return_usd,0.995, na.rm = T)|
     log_return_usd <= quantile(log_return_usd,0.005, na.rm = T),log_return_usd:= NA]

df[log_return_eth >= quantile(log_return_eth,0.995, na.rm = T)|
     log_return_eth <= quantile(log_return_eth,0.005, na.rm = T),log_return_eth:= NA]

df[price_ETH >= quantile(price_ETH,0.995, na.rm = T)|
     price_ETH <= quantile(price_ETH,0.005, na.rm = T),price_ETH := NA]

df[price_volatility_ETH >= quantile(price_volatility_ETH,0.995, na.rm = T)|
     price_volatility_ETH <= quantile(price_volatility_ETH,0.005, na.rm = T),price_volatility_ETH := NA]

df[price_volatility_USD >= quantile(price_volatility_USD,0.995, na.rm = T)|
     price_volatility_USD <= quantile(price_volatility_USD,0.005, na.rm = T),price_volatility_USD := NA]

df[gas_price_usd >= quantile(gas_price_usd,0.995, na.rm = T)|
     gas_price_usd <= quantile(gas_price_usd,0.005, na.rm = T),gas_price_usd := NA]

df[gas_price_eth >= quantile(gas_price_eth,0.995, na.rm = T)|
     gas_price_eth <= quantile(gas_price_eth,0.005, na.rm = T),gas_price_eth := NA]

df[gas_price_volatility_usd >= quantile(gas_price_volatility_usd,0.995, na.rm = T)|
     gas_price_volatility_usd <= quantile(gas_price_volatility_usd,0.005, na.rm = T),gas_price_volatility_usd := NA]

df[gas_price_volatility_eth >= quantile(gas_price_volatility_eth,0.995, na.rm = T)|
     gas_price_volatility_eth <= quantile(gas_price_volatility_eth,0.005, na.rm = T),gas_price_volatility_eth := NA]

df[mcap >= quantile(mcap,0.995, na.rm = T)|
     mcap <= quantile(mcap,0.005, na.rm = T),mcap := NA]

### Normalization
#df[,eigencentrality_in := scale(eigencentrality_in)]
#df[,eigencentrality_out := scale(eigencentrality_out)]
#df[,trading_volume_total:= scale(trading_volume_total)]
#df[,total_tvl := scale(total_tvl)]

df[,borrow_total_relative := scale(borrow_total_relative)]
df[,lend_total_relative := scale(lend_total_relative)]

df[,log_return_usd := scale(log_return_usd)]
df[,log_return_eth := scale(log_return_eth)]

df[,price_volatility_ETH := scale(price_volatility_ETH)]
df[,price_volatility_USD := scale(price_volatility_USD)]

names(df)[names(df) == 'price_volatility_ETH'] <- 'log_return_eth_volatility'
names(df)[names(df) == 'price_volatility_USD'] <- 'log_return_usd_volatility'


df[,mcap := scale(mcap)]

df[,gas_price_usd := scale(gas_price_usd)]
df[,gas_price_eth := scale(gas_price_eth)]

df[,gas_price_volatility_usd := scale(gas_price_volatility_usd)]
df[,gas_price_volatility_eth := scale(gas_price_volatility_eth)]

df[,eigencentrality_average := (eigencentrality_in + eigencentrality_out)/2]

df[,constant := 1]
################################
## Eigenvalue Centrality average
################################
## Eigenvalue Centrality average -  Pooled OLS

lm0 <- felm(eigencentrality_average ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_usd +
              Dummy_WETH * gas_price_volatility_usd + Dummy_Stable + SnP
              , data = df)

lm1 <- felm(eigencentrality_average ~  log_return_usd + log_return_usd_volatility + 
            mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_eth +
              Dummy_WETH * gas_price_volatility_eth + Dummy_Stable + SnP
            , data = df)


lm2 <- felm(eigencentrality_average ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
               + Dummy_Stable + SnP
            , data = df)

lm3 <- felm(eigencentrality_average ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP
            , data = df)

lmlist1 <- list(lm0,lm1,lm2,lm3)
SElist1 <- list(SE(lm0),SE(lm1), SE(lm2), SE(lm3))

stargazer(lmlist1, digits =3 , type = "latex", se = SElist1, no.space = T, 
          title = "Regression Result - Pooled OLS",
          add.lines=list(c('Crypto Index Control', 'Yes','Yes','Yes','Yes'),
                         c('Fixed effects', '-','-','-','-')), 
          out = paste0(output_folder,'regression_in_centra.tex'))

fe <- getfe(lm3)

write.table(fe, file = paste0(output_folder,'fe_incentrality.csv'), 
row.names = F, sep =",")

## Eigenvalue Centrality average -  Panel Fixed Effect OLS

lm0 <- felm(eigencentrality_average ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_usd +
              Dummy_WETH * gas_price_volatility_usd + Dummy_Stable + SnP + constant|token|0|token
            , data = df)

lm1 <- felm(eigencentrality_average ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_eth +
              Dummy_WETH * gas_price_volatility_eth + Dummy_Stable + SnP + constant|token|0|token
            , data = df)


lm2 <- felm(eigencentrality_average ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP + constant|token|0|token
            , data = df)

lm3 <- felm(eigencentrality_average ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP + constant|token|0|token
            , data = df)

lmlist1 <- list(lm0,lm1,lm2,lm3)
SElist1 <- list(SE(lm0),SE(lm1), SE(lm2), SE(lm3))

stargazer(lmlist1, digits =3 , type = "latex", se = SElist1, no.space = T, 
          title = "Regression Result - Fixed Effect",
          add.lines=list(c('Crypto Index Control', 'Yes','Yes','Yes','Yes'),
                         c('Fixed effects', 'Token','Token','Token','Token')), 
          out = paste0(output_folder,'regression_in_centra.tex'))

fe <- getfe(lm3)

write.table(fe, file = paste0(output_folder,'fe_incentrality.csv'), 
            row.names = F, sep =",")

################################
## total trading volume
################################
## total trading volume -  Pooled OLS

lm0 <- felm(trading_volume_total ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_usd +
              Dummy_WETH * gas_price_volatility_usd + Dummy_Stable + SnP
            , data = df)

lm1 <- felm(trading_volume_total ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_eth +
              Dummy_WETH * gas_price_volatility_eth + Dummy_Stable + SnP
            , data = df)


lm2 <- felm(trading_volume_total ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP
            , data = df)

lm3 <- felm(trading_volume_total ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP
            , data = df)

lmlist1 <- list(lm0,lm1,lm2,lm3)
SElist1 <- list(SE(lm0),SE(lm1), SE(lm2), SE(lm3))

stargazer(lmlist1, digits =3 , type = "latex", se = SElist1, no.space = T, 
          title = "Regression Result - Pooled OLS",
          add.lines=list(c('Crypto Index Control', 'Yes','Yes','Yes','Yes'),
                         c('Fixed effects', '-','-','-','-')), 
          out = paste0(output_folder,'regression_in_centra.tex'))

fe <- getfe(lm3)

write.table(fe, file = paste0(output_folder,'fe_incentrality.csv'), 
            row.names = F, sep =",")

## Eigenvalue Centrality average -  Panel Fixed Effect OLS

lm0 <- felm(trading_volume_total ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_usd +
              Dummy_WETH * gas_price_volatility_usd + Dummy_Stable + SnP + constant|token|0|token
            , data = df)

lm1 <- felm(trading_volume_total ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_eth +
              Dummy_WETH * gas_price_volatility_eth + Dummy_Stable + SnP + constant|token|0|token
            , data = df)


lm2 <- felm(trading_volume_total ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP + constant|token|0|token
            , data = df)

lm3 <- felm(trading_volume_total ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP + constant|token|0|token
            , data = df)

lmlist1 <- list(lm0,lm1,lm2,lm3)
SElist1 <- list(SE(lm0),SE(lm1), SE(lm2), SE(lm3))

stargazer(lmlist1, digits =3 , type = "latex", se = SElist1, no.space = T, 
          title = "Regression Result - Fixed Effect",
          add.lines=list(c('Crypto Index Control', 'Yes','Yes','Yes','Yes'),
                         c('Fixed effects', '-','-','-','-')), 
          out = paste0(output_folder,'regression_in_centra.tex'))

fe <- getfe(lm3)

write.table(fe, file = paste0(output_folder,'fe_incentrality.csv'), 
            row.names = F, sep =",")
################################
## total tvl
################################
## total tvl -  Pooled OLS

lm0 <- felm(total_tvl ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_usd +
              Dummy_WETH * gas_price_volatility_usd + Dummy_Stable + SnP
            , data = df)

lm1 <- felm(total_tvl ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_eth +
              Dummy_WETH * gas_price_volatility_eth + Dummy_Stable + SnP
            , data = df)


lm2 <- felm(total_tvl ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP
            , data = df)

lm3 <- felm(total_tvl ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP
            , data = df)

lmlist1 <- list(lm0,lm1,lm2,lm3)
SElist1 <- list(SE(lm0),SE(lm1), SE(lm2), SE(lm3))

stargazer(lmlist1, digits =3 , type = "latex", se = SElist1, no.space = T, 
          title = "Regression Result - Pooled OLS",
          add.lines=list(c('Crypto Index Control', 'Yes','Yes','Yes','Yes'),
                         c('Fixed effects', '-','-','-','-')), 
          out = paste0(output_folder,'regression_in_centra.tex'))

fe <- getfe(lm3)

write.table(fe, file = paste0(output_folder,'fe_incentrality.csv'), 
            row.names = F, sep =",")

## Eigenvalue Centrality average -  Panel Fixed Effect OLS

lm0 <- felm(total_tvl ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_usd +
              Dummy_WETH * gas_price_volatility_usd + Dummy_Stable + SnP|token|0|token
            , data = df)

lm1 <- felm(total_tvl ~  log_return_usd + log_return_usd_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              Dummy_WETH + Dummy_WETH * gas_price_eth +
              Dummy_WETH * gas_price_volatility_eth + Dummy_Stable + SnP|token|0|token
            , data = df)


lm2 <- felm(total_tvl ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_usd + gas_price_volatility_usd + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP|token|0|token
            , data = df)

lm3 <- felm(total_tvl ~  log_return_eth + log_return_eth_volatility + 
              mcap + gas_price_eth + gas_price_volatility_eth + 
              borrow_total_relative + lend_total_relative +
              + Dummy_Stable + SnP|token|0|token
            , data = df)

lmlist1 <- list(lm0,lm1,lm2,lm3)
SElist1 <- list(SE(lm0),SE(lm1), SE(lm2), SE(lm3))

stargazer(lmlist1, digits =3 , type = "latex", se = SElist1, no.space = T, 
          title = "Regression Result - Fixed Effect",
          add.lines=list(c('Crypto Index Control', 'Yes','Yes','Yes','Yes'),
                         c('Fixed effects', '-','-','-','-')), 
          out = paste0(output_folder,'regression_in_centra.tex'))

fe <- getfe(lm3)

write.table(fe, file = paste0(output_folder,'fe_incentrality.csv'), 
            row.names = F, sep =",")
