"""https://github.com/Leci37/LecTrade LecTrade is a tool created by github user @Leci37. instagram @luis__leci Shared on 2022/11/12 .   . No warranty, rights reserved """
import logging
import re
from threading import Thread
import threading
from random import randint
from datetime import datetime
import pandas as pd
import time

import traceback

import Model_predictions_handle_Nrows
import Model_predictions_handle_Multi_Nrows
import ztelegram_send_message
from LogRoot.Logging import Logger
import yhoo_history_stock
from Utils.Utils_QueueMap import QueueMap
from _KEYS_DICT import Op_buy_sell, Option_Historical, DICT_WEBULL_ID, DICT_COMPANYS
# from api_twitter import twi_
from predict_POOL_handle_hkex import get_tech_data_hkex, get_df_webull_realTime, df_yhoo_, merge_dataframes_bull_yhoo
from ztelegram_send_message import send_alert_and_register, send_exception
LOGGER = logging.getLogger()
LOGGER.disabled = False

df_result = pd.read_csv("Models/TF_multi/_RESULTS_profit_multi_all.csv", index_col=0,sep='\t')
list_pos = [x for x in df_result.columns if  "_" + Op_buy_sell.POS.value + "_" in x and  not x.endswith("_per") ]
list_neg = [x for x in df_result.columns if  "_" + Op_buy_sell.NEG.value + "_" in x and  not x.endswith("_per") ]
list_stocks_models = set(list_pos +list_neg)
print("Models loaded: "+ ", ".join(list_stocks_models))

# regex_S = "TFm_([A-Z]{1,5}|[A-Z]{1,5}-USD)_(pos|neg)_"
regex_S = r"TFm_([A-Z0-9.\-]+)_(pos|neg)_"
list_stocks = [re.search(regex_S, x, re.IGNORECASE).group(1) for x in list_stocks_models]
list_stocks = set(list_stocks)
print("Stoscks loaded: "+ ", ".join(list_stocks))
NUM_LAST_REGISTERS_PER_STOCK = 64 # Number of records to be used for prediction
#CONSUMER MANAGE
def scaler_and_send_predit(S, df_S, df_nasq, is_multidimension = False ):
    df_S = get_tech_data_hkex(S, df_S, df_nasq)
    df_tech = df_S[-NUM_LAST_REGISTERS_PER_STOCK:]
    print("df_tech", df_tech)
    if df_tech.empty:
        Logger.logr.warning("No data to predict for stock: " + S)
        return
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
            send_alert_and_register(S, df_vender, Op_buy_sell.NEG)

TIME_OUT_PRODUCER = 5 * 60   # [seconds]

def producer():
    global queue
    Logger.logr.info(' Producer: Running Start '+ datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    while True:
        Logger.logr.debug(' Producer: Running Start ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        timeout_start = time.time()
        while time.time() < timeout_start + TIME_OUT_PRODUCER:
            list_pro = list_stocks.copy()
            INTERVAL = "d5"  # ""d1" #
            for S in list_stocks:
                try:
                    time.sleep(randint(1, 7))#esperar en 1 y 10s , por miedo a baneo
                    #df_S_raw, df_primeros = get_df_webull_realTime(INTERVAL, S,None)# path= "d_price/weBull/weBull_"+S+"_"+INTERVAL+".csv")
                    #Logger.logr.info(" DF Stock: " + S + " Shape_DF: " + str(df_S_raw.shape) + " RealTime: " + str(df_S_raw.iloc[-1]['Date']) + " Volume: "+ str(df_S_raw.iloc[1]['Volume']) )
                    #retiramos las primeras 40 para que no se solapen
                    df_yhoo = df_yhoo_(S, "15m")[1:]#, path= "d_price/weBull/yhoo_"+S+"_15m.csv")[40:] #
                    Logger.logr.info(" DF yhoo Stock: " + S + " Shape_DF: " + str(df_yhoo.shape) + " RealTime: " + str(df_yhoo.iloc[-1]['Date']) + " Volume: "+ str(df_yhoo.iloc[1]['Volume']) )
                    #df = merge_dataframes_bull_yhoo(S, df_S_raw, df_primeros, df_yhoo)

                    df =df_yhoo
                    Logger.logr.info(df.head(2))
                    Logger.logr.info(" DF encolado Stock: " + S + " Shape_DF: " + str(df.shape) + " RealTime: " + str(df.iloc[-1]['Date']) + " Volume: "+ str(df.iloc[1]['Volume']) )
                    list_pro.remove(S)#para yhoo API
                    queue.pop(S)
                    queue.set(S, df)
                except Exception as ex:
                    Logger.logr.warning(" Exception Stock: " + S + "  Exception: " + traceback.format_exc())
                    send_exception(ex, "[PRO] Exception Stock: " + S +"\n"+traceback.format_exc())

            if not list_pro:
                Logger.logr.info(" sleep(60 * 2) List all stock download empty")
                # from XTB_api import xAPIConnector_trade
                # xAPIConnector_trade.updates_tp_sp()
                time.sleep( 60 * 2 )
                break
            else:
                Logger.logr.info(" Sleep(60) There are still values left in the Values queue list:  "+ " ".join(list_pro))
                time.sleep(20)

            if  "30:00" in  datetime.today().strftime('%Y-%m-%d %H:%M:%S') or "00:00" in  datetime.today().strftime('%Y-%m-%d %H:%M:%S'):
                ztelegram_send_message.send_mesage_all_people("<pre> RUNING it is alive: " + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + "</pre>")
        Logger.logr.info(' Producer: Running End ' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    Logger.logr.info(' Producer: Done')

def consumer(int_thread):
    global queue
    Logger.logr.info(" Consumer: Running Start " + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " Thread: " + str(int_thread))
    Logger.logr.debug("  Consumer: Running")
    list_pro = list_stocks.copy()
    while True:
        df_hkex = yhoo_history_stock.get_HKEX_data(exter_id_NQ = "^HSI", interval='15m' , opion=Option_Historical.DAY_6, remove_str_in_colum = "^")
        LOGGER = logging.getLogger()
        LOGGER.disabled = False
        for S in list_pro:
            # print("[CON] start " + S)
            df_S = queue.pop(S)
            if df_S is not None:
                Logger.logr.info("Stock: " + S + "  Volume unlast: " + str(df_S.iloc[-2]['Volume']) + " Volume last: " + str(df_S.iloc[-1]['Volume'])+ " Date: "+ datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
                try:
                    scaler_and_send_predit(S, df_S, df_hkex, is_multidimension = True)
                    # scaler_and_send_predit(S, df_S, df_nasq, is_multidimension = True)
                except Exception as ex:
                    if 'not in index' in str(ex) or 'No objects to concatenate' in str(ex)or 'inputs are all ' in str(ex): #No objects to concatenate
                        #Todo manage this exceptions
                        # raw_df[columns_selection] las columns_selection no han sido calculadas en el df_tech , o han desaparecido
                        Logger.logr.warning(" Exception raw_df = raw_df[columns_selection] the columns_selection have not been calculated in the df_tech , or have disappeared  " + str(ex))
                    else:
                        Logger.logr.warning(" Exception:  Stock: " + S +  traceback.format_exc())
                        #send_exception(ex, "[CON] [" + str(int_thread) * 4 + "]Exception Stock: " + S + "\n <pre>" + traceback.format_exc()+"</pre>")
        Logger.logr.info(" completed cycle    Date: "+ datetime.today().strftime('%Y-%m-%d %H:%M:%S') + " stoks: "+ " ".join(list_pro))
        time.sleep(int_thread *15)            
    Logger.logr.info(" Consumer: Done"+ " Date: "+ datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


# for S in list_stocks:
#     df_yhoo = df_yhoo_(S,"15m")[1:]
#     # print("df_yhoo", df_yhoo)
#     df =df_yhoo
#     queue.pop(S)
#     queue.set(S, df)

# df_yhoo = df_yhoo_("0020.HK","15m")[1:]
            
# list_pro = list_stocks.copy()
# df_hkex = yhoo_history_stock.get_HKEX_data(exter_id_NQ = "^HSI", interval='15m' , opion=Option_Historical.DAY_6, remove_str_in_colum = "^")
# #df_nasq = yhoo_history_stock.get_NASDAQ_data(exter_id_NQ = "NQ=F", interval='15m' , opion=Option_Historical.DAY_6, remove_str_in_colum = "=F")
# scaler_and_send_predit("0020.HK", df_yhoo, df_hkex, is_multidimension = True)


queue = QueueMap()
ztelegram_send_message.send_mesage_all_people("<pre> START: "+datetime.today().strftime('%Y-%m-%d %H:%M:%S') +" </pre>\nStocks to be monitored: \n"+" ".join(list_stocks)+" ")
producer_thr = Thread(target=producer, args=(), name='PROD')
producer_thr.start()
time.sleep(2)

# start the consumer
# Creating 3 threads that execute the same function with different parameters
consumer_thr_1 = threading.Thread(target=consumer, args=(1,), name='CONS_1')

consumer_thr_1.start()

        

