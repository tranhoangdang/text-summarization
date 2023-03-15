import requests
from bs4 import BeautifulSoup
import re
import underthesea
import pandas as pd

def get_title_from_VNE(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text,'html.parser')
    titles = soup.find_all("h1",attrs={'class':'title-detail'})
    raw_content = ''
    for title in titles:
        raw_content += title.text
    return raw_content

def get_content_from_VNE(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text,'html.parser')
    contents = soup.find_all("p",attrs={'class':'Normal'})
    contents = list(contents)
    contents = re.sub("<.*?>", "\n", str(contents))
    contents = re.sub(",", "", str(contents))
    return contents

def getStop_words(filePath_stop_word):
    with open (filePath_stop_word, encoding = 'utf-8') as f:
        stop_words = f.read()
    stop_words = stop_words.split('\n')
    return list(stop_words)

def text_summarization(url):
    raw_content = get_content_from_VNE(url)
    filePath_stop_word = 'vietnamese-stopwords.txt'
    stop_words = getStop_words(filePath_stop_word)
    sentences = underthesea.sent_tokenize(raw_content)
    for sent in sentences:
        words = underthesea.word_tokenize(raw_content)

    word_freq = {}
    for word in words:
        if word not in stop_words:
            if word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] += 1

    max_word_freq = max(word_freq.values())
    for key in word_freq.keys():
        word_freq[key] /= max_word_freq

    sentences_score = []
    for sent in sentences:
        curr_words = underthesea.word_tokenize(sent)
        curr_score = 0
        for word in curr_words:
            if word in word_freq:
                curr_score += word_freq[word]
        sentences_score.append(curr_score)

    sentences_data = pd.DataFrame({"sent":sentences, "score":sentences_score})
    sorted_data = sentences_data.sort_values(by = "score", ascending = False).reset_index()
    summary = sorted_data.iloc[0:7,:]
    return " ".join(list(summary["sent"]))