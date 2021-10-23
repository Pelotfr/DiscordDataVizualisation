from pandas.tseries import frequencies
from wordcloud import WordCloud
from PIL import Image

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import multidict
import math
import re
import json

# Function creating frequency dict from string
def getFrequencyDict(sentence):
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}
    for text in sentence.split(' '):
        text = text.strip()
        text = re.sub(r'[0-9]+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        if re.match("un|le|nan|la|de|du|p|play|fs|np|skip|resume|clear|lyrics|queue", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        # affiche nombre d'occurence
        #if key == 'oui':
        #    tmpDict[key]
        fullTermsDict.add(key, tmpDict[key])
    return fullTermsDict

# Generating frequency wordcloud from the messages
def wordcloud(df_messages):
    if len(df_messages) > 1000 :
        n = (int)(len(df_messages)/1000)
    else:
        n = 1
    for i in range (0 ,n) :
        text = ''.join(str(df_messages['Contents'].values[i*1000:(i+1)*1000]))
        frequencyDict = getFrequencyDict(text)
        wc1 = WordCloud(background_color="white", contour_width=3, contour_color='steelblue')
        wc1.generate_from_frequencies(getFrequencyDict(text))
        fig, ax = plt.subplots()
        ax.imshow(wc1, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

# cleans the dataframe
def clean_df(df):
    df = df.drop(columns=['ID'])
    df['Contents'].dropna(inplace=True)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    return df

# loads data
@st.cache
def get_troupal_channels():
    with open("D:\DataVizualisationPersonalData\discord\messages\index.json") as json_file:
        channels_index = json.load(json_file)
    path = "D:\DataVizualisationPersonalData\discord\messages\c"
    troupal_dict = {}
    for key in channels_index.keys():
        with open(path + key + "\channel.json") as json_file:
            channel_json = json.load(json_file)
        if "guild" in channel_json.keys():
            if channel_json["guild"]["name"] == "Le Troupal" :
                df_temp = pd.read_csv(path + key + "\messages.csv")
                troupal_dict[channel_json["name"]] = df_temp
    return troupal_dict

"""
# My Discord data visualization app
"""
st.sidebar.write("# Paul Meignan")
st.sidebar.write("## October 2021")
st.sidebar.write("[Github](https://github.com/Pelotfr)  [LinkedIn](https://www.linkedin.com/in/paul-meignan/)")
analysis = st.sidebar.selectbox('Menu', ('Global analysis', 'In depth analysis on a server'))

if analysis == 'Global analysis':
    """
    ## Discord is a social media essentially using text and vocal chat
    ## We will see how I use Discord with the text messages I send
    """
    with open("D:\DataVizualisationPersonalData\discord\servers\index.json") as json_file:
        servers_index = json.load(json_file)
    keys = len(servers_index.keys())
    """### Number of servers:"""
    st.write("I am currently in " + str(keys) + " servers")
    with open("D:\DataVizualisationPersonalData\discord\messages\index.json") as json_file:
        dm_index = json.load(json_file)
    keys = len(dm_index.keys())
    """### Number of private messages/groups:"""
    st.write("I wrote private messages to " + str(keys) + " people/groups")
else:
# loading data from channels in Le Troupal server
    troupal_channels = get_troupal_channels()

    df_total = pd.DataFrame()
    for key,value in troupal_channels.items():
        df_total = df_total.append(value)
    choice_list = list(troupal_channels.keys())
    choice_list.append('All channels')
    choice = st.sidebar.selectbox('Select the channel:', choice_list)

    if choice in troupal_channels.keys():
        df_messages = troupal_channels[choice]
    else:
        df_messages = df_total

    df_messages = clean_df(df_messages)


    st.header('Analysis on ' + choice)

    # GLOBAL INFORMATION
    if st.checkbox("Show global information"):
        st.subheader('Global information')
        st.write("Total number of messages: " + str(len(df_messages.index)))
        st.write("Date of first message: " + str(df_messages['Timestamp'].dt.date.iloc[-1]))
        st.write("Date of last message: " + str(df_messages['Timestamp'].dt.date.iloc[0]))

    # WORDCLOUDS
    if st.checkbox("Show wordclouds"):
        st.subheader('Wordcloud(s)')
        wordcloud(df_messages)
        if (choice == 'tftade'):
            if st.checkbox("Show image"):
                image = Image.open(r"C:\Users\paulm\OneDrive\Bureau\Ecole\S7\Data Visualization\projet\TFT.jpg")
                st.image(image, caption='TFT in game picture')
        elif (choice == 'les-vestiaires'):
            if st.checkbox("Show image"):
                image = Image.open(r"C:\Users\paulm\OneDrive\Bureau\Ecole\S7\Data Visualization\projet\fifa.jpg")
                st.image(image, caption='Fifa 21 in game picture')
        elif (choice == 'amon-us'):
           if st.checkbox("Show image"):
                image = Image.open(r"C:\Users\paulm\OneDrive\Bureau\Ecole\S7\Data Visualization\projet\among-us.jpg")
                st.image(image, caption='Among us in game picture')
    # USING TIMESTAMPS 
    if st.checkbox("Show plots using timestamps"):
        st.header('Exploring timestamps')

        # HOUR
        st.subheader('Number of messages by hour')
        hist_values = np.histogram(df_messages['Timestamp'].dt.hour, bins=24, range=(0,24))[0]
        st.bar_chart(hist_values)

        #st.subheader('Number of messages by hour in total server')
        #hist_values = np.histogram(df_total['Timestamp'].dt.hour, bins=24, range=(0,24))[0]
        #st.bar_chart(hist_values)

        # MONTH
        st.subheader('Number of messages by month')
        fig, ax = plt.subplots()
        bins = np.arange(1,14)
        ax.hist(df_messages['Timestamp'].dt.month, bins=bins, align='left', rwidth=.5)
        ax.set_xticks(bins[:-1])
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
        'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax.spines['left'].set_color('w')
        ax.set_xlabel("Months")
        ax.set_ylabel("Count")
        ax.yaxis.label.set_color('w')
        ax.xaxis.label.set_color('w')
        ax.spines['bottom'].set_color('w')
        ax.tick_params(colors='white')
        ax.set_facecolor('k')
        fig.set_facecolor('k')
        st.pyplot(fig)

        # YEAR
        st.subheader('Number of messages by year')
        fig, ax = plt.subplots()
        bins = np.arange(2019,2023)
        ax.hist(df_messages['Timestamp'].dt.year, bins=bins, align='left', rwidth=.5)
        ax.set_xticks(bins[:-1])
        ax.set_xticklabels(['2019', '2020', '2021'])
        ax.spines['left'].set_color('w')
        ax.spines['bottom'].set_color('w')
        ax.set_xlabel("Years")
        ax.set_ylabel("Count")
        ax.yaxis.label.set_color('w')
        ax.xaxis.label.set_color('w')
        ax.tick_params(colors='white')
        ax.set_facecolor('k')
        fig.set_facecolor('k')
        st.pyplot(fig)