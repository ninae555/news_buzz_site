#!/usr/bin/env python
# coding: latin1

# In[7]:


# screenshot of website 
# decrease the level to 0 cap at 5 
# limit to 1 article per url 

# 1 news feed comprised of arts below credibility and news above threshold 

# no interaction for pilot study; don't learn the preference 

# 2 weeks complete site 

# In[14]:


import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')

import calendar
from datetime import datetime
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import datetime
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

#%%
