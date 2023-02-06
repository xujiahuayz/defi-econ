library(data.table)
library(ggplot2)
library(stringr)
library(bit64)
library(reshape2)
library(lubridate)
library(stargazer)
library(lfe)
library(Hmisc)

# Set the output path

output_folder <- "../tables/"

### Summary Statistics for Inflow Eigenvector Centrality ###
############################################################
df <- fread("../data/data_network/eigen_in_merged.csv")
  
stargazer(df[,c("WETH", "USDT", "USDC", "DAI", "FEI", "WBTC", "MATIC")],
          title = 'Summary Statistics of Inflow Eigenvector Centrality',
          out = paste0(output_folder,'eigen_in_summary.tex'))


### Summary Statistics for Outflow Eigenvector Centrality ###
############################################################
df <- fread("../data/data_network/eigen_out_merged.csv")

stargazer(df[,c("WETH", "USDT", "USDC", "DAI", "FEI", "WBTC", "MATIC")],
          title = 'Summary Statistics of Outflow Eigenvector Centrality',
          out = paste0(output_folder,'eigen_out_summary.tex'))
