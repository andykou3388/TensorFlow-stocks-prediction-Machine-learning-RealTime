"""https://github.com/Leci37/LecTrade LecTrade is a tool created by github user @Leci37. instagram @luis__leci Shared on 2022/11/12 .   . No warranty, rights reserved """
import logging
import re
from threading import Thread
import threading
from random import randint
from datetime import datetime
import pandas as pd
import time

""" import traceback

import Model_predictions_handle_Nrows
import Model_predictions_handle_Multi_Nrows
import ztelegram_send_message """
from LogRoot.Logging import Logger
import yhoo_history_stock
from Utils.Utils_QueueMap import QueueMap
from _KEYS_DICT import Op_buy_sell, Option_Historical, DICT_WEBULL_ID, DICT_COMPANYS
# from api_twitter import twi_
from predict_POOL_handle_hkex import get_tech_data_hkex, get_df_webull_realTime, df_yhoo_, merge_dataframes_bull_yhoo
from ztelegram_send_message import send_alert_and_register, send_exception
list_stocks = ["1088.HK"]
queue = QueueMap()

#CONSUMER MANAGE
def scaler_and_send_predit(S, df_S, df_nasq, is_multidimension = False ):
    df_S = get_tech_data_hkex(S, df_S, df_nasq)
    print("df_S", df_S)
"""    df_tech = df_S[-NUM_LAST_REGISTERS_PER_STOCK:]
    if is_multidimension:
        df_eval_multi = Model_predictions_handle_Multi_Nrows.get_df_Multi_comprar_vender_predictions(df_tech, S, path_result_eval=None)
        if df_eval_multi is not None:
            ztelegram_send_message.send_MULTI_alert_and_register(S, df_eval_multi)
    else:
        Logger.logr.info(" Scaler and send predict for stock: " + S+ " Shape: " + str(df_tech.shape)    )
        df_tech = Model_predictions_handle_Nrows.add_min_max_(df_S, S)
        df_compar, df_vender = Model_predictions_handle_Nrows.get_df_comprar_vender_predictions(df_tech, S)
        if df_compar is not None:
            send_alert_and_register(S, df_compar, Op_buy_sell.POS)
        if df_vender is not None:
            send_alert_and_register(S, df_vender, Op_buy_sell.NEG) """

# ztelegram_send_message.send_mesage_all_people("<pre> START: "+datetime.today().strftime('%Y-%m-%d %H:%M:%S') +" </pre>\nStocks to be monitored: \n"+" ".join(list_stocks)+" ")

# for S in list_stocks:
#     df_yhoo = df_yhoo_(S,"15m")[1:]
#     # print("df_yhoo", df_yhoo)
#     df =df_yhoo
#     queue.pop(S)
#     queue.set(S, df)

df_yhoo = df_yhoo_("1088.HK","15m")[1:]
            
list_pro = list_stocks.copy()
df_hkex = yhoo_history_stock.get_HKEX_data(exter_id_NQ = "^HSI", interval='15m' , opion=Option_Historical.DAY_6, remove_str_in_colum = "^")
#df_nasq = yhoo_history_stock.get_NASDAQ_data(exter_id_NQ = "NQ=F", interval='15m' , opion=Option_Historical.DAY_6, remove_str_in_colum = "=F")
print("df_nasq", df_hkex)
scaler_and_send_predit("1088.HK", df_yhoo, df_hkex, is_multidimension = True)




        

