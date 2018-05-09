from nltk.tag import pos_tag
from nltk.tokenize import TweetTokenizer

import enchant
import re
import emoji
import requests
import base64
import sys
from collections import Counter

tweets = []

if len(sys.argv) == 3:
    print(sys.argv)
    if sys.argv[1] == 'tweets':
        FROM_TWITTER = True
        FROM_FILE = False
        client_key = 'CAyOqosKb6fU86YC1a8zxV2l0'
        client_secret = 'PTCnPc4EmCx0vV9UNQxY5AVz07j2y3QXAkf4dweQfayoDmyqLp'

        key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
        b64_encoded_key = base64.b64encode(key_secret)
        b64_encoded_key = b64_encoded_key.decode('ascii')


        base_url = 'https://api.twitter.com/'
        auth_url = '{}oauth2/token'.format(base_url)

        auth_headers = {
            'Authorization': 'Basic {}'.format(b64_encoded_key),
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        auth_data = {
            'grant_type': 'client_credentials'
        }

        auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

        print(auth_resp.status_code)

        access_token = auth_resp.json()['access_token']


        search_headers = {
            'Authorization': 'Bearer {}'.format(access_token)
        }

        search_params = {
            'q': sys.argv[2],
            'result_type': 'popular',
            'count': 15,
            'lang': 'en',

        }

        search_url = '{}1.1/search/tweets.json'.format(base_url)

        search_resp = requests.get(search_url, headers=search_headers, params=search_params)


        tweet_data = search_resp.json()
        for x in tweet_data['statuses']:
            tweets.append(x['text'])
    else:
        print('hello')
        FROM_FILE = True
        FROM_TWITTER = False
        filename = sys.argv[2]
        file_data = []
        with open(filename) as f:
            for line in f:
                file_data.append(line.rstrip())


''' Set spellchecking default settings'''
d = enchant.Dict("en_US")

# Test for non-standard spelling
sample_tweet_nss_1 = "Toook a ride around townn 4eva."

# Test for informal abbreviations
sample_tweet_ia_1 = ""

# Test for phonetic substitutions
sample_tweet_ps_1 = ""

# Sample Tweets for preprocessing
sample1 = "My wife @theemrsmcafee has been wanting me to tweet this photo for many months. She just scraped the money together to pay for the tweet.  It's a lot of money for her. Go visit her. https://random-img-url.com"
sample2 = "oh wow... oH wOW #Boachella #Coachella #CardiB"
sample3 = "Anyone have a good contact at @GoDaddy or the @Google Cloud team? Need help taking down the latest phishing site targeting our community."
sample4 = "I wanna start fishing a lot this summer"

punctuations = ['!', '.', ',', '?']
abbreviations = {
                'tmrw': 'tomorrow',
                'lol': 'laughing out loud',
                'st': 'street',
                'aka': 'also known as',
                'aite': 'alright',
                'aight': 'alright',
                'TDLR': 'too long; didn\'t read',
                'icymi': 'in case you missed it',
                'tfti': 'thanks for the invite',
                'ily': 'i love you',
                'ty': 'thank you',
                'kk': 'okay',
                'lmao': 'laughing my ass off',
                'lmfao': 'laughing my fucking ass off',
                'rotfl': 'rolling on the floor laughing',
                'thx': 'thanks',
                'omg': 'oh my god',
                '2moro': 'tomorrow',
                '2morrow': 'tomorrow',
                '2nite': 'tonight',
                '2day': 'today',
                'gr8': 'great',
                'ik': 'I know',
                'ikr': 'I know right',
                'jk': 'just kidding',
                'tmi': 'too much information',
                'wtf': 'what the f*ck',
                'wth': 'what the hell',
                'imo': 'in my opinion',
                '4eva': 'forever',
                '4ever': 'forever',
                'ttyl': 'talk to you later',
                'prob': 'probably',
                'nite': 'night',
                'rly': 'really',
                'rt': 'retweet',
                'ru': 'are you',
                'smh': 'smh',
                'sry': 'sorry',
                'str8': 'straight',
                'tbh': 'to be honest',
                'w8': 'wait',
                'h8': 'hate',
                'wat': 'what',
                'wut': 'what',
                'wbu': 'what about you',
                'u': 'you',
                'yolo': 'you only live once',
                '&amp;': '&',
                }

def normalization_eligibility_check(word):

    # Check if word contains ANY letters (eliminate candidates containing ONLY numbers or symbols)
    if not re.search('[a-zA-Z]', word):
        return False

    # Check for mentions
    if '@' in word:
        return False

    # Check for hashtags
    if '#' in word:
        return False

    # Check for urls
    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', word)
    if len(urls) != 0:
        return False

    # Check for proper nouns
    tagged = pos_tag([word])
    if tagged[0][1] == 'NNP':
        return False

    return True

def remove_punctuation(word):
    cleaned_word = ""
    current_punctuations = []
    for char in word:
        if char not in punctuations:
            cleaned_word += char
        else:
            current_punctuations.append(char)

    return (cleaned_word, current_punctuations)

def remove_emojis(word):
    cleaned_word = ""
    for char in word:
        if char not in emoji.UNICODE_EMOJI:
            cleaned_word += char
    return (cleaned_word)

def insert_punctuation(word, removed_punctuations):
    if len(removed_punctuations) > 0:
        for punctuation in removed_punctuations:
            word += punctuation
    return word

def non_standard_check(word):
    # First check if word is already correctly spelled
    word_is_valid = d.check(word)
    if word_is_valid:
        return True
    else:
        return False

def generate_suggestions(word):
    suggestions = d.suggest(word)
    return suggestions

def remove_excess(word):
    reverse_word = word[::-1]
    buffer = []
    reduce = False
    for char in reverse_word:
        if len(buffer) == 0:
            buffer.append(char)
        else:
            if char == buffer[-1]:
                buffer.append(char)
            else:
                if len(buffer) >= 3:
                    reduce = True
                break
    if reduce:
        word = word[:-(len(buffer)-1)]
        print("REDUCED: " + word)
    return word

def pipeline(word):

    eligible = normalization_eligibility_check(word)

    if not eligible:
        print("Word: '" + word + "' is not eligible for normalization.")
        return word
    else:
        # Remove punctuations
        cleaned_word, removed_punctuations = remove_punctuation(word)
        # Remove emojis
        cleaned_word = remove_emojis(cleaned_word)
        # Remove excess
        cleaned_word = remove_excess(cleaned_word)

        # Check to see if word is already spelled correctly
        if non_standard_check(cleaned_word) == True:
            word = insert_punctuation(cleaned_word, removed_punctuations)
            print("Word: '" + cleaned_word + "' is already spelled correctly.")
            return word
        else:
            # Check to see if word is a known abbreviation
            if cleaned_word.lower() in abbreviations.keys():
                expanded_form = abbreviations[cleaned_word.lower()]
                print("Changed '" + cleaned_word + "' to " + expanded_form)
                word = insert_punctuation(expanded_form, removed_punctuations)
                return word

            else:
                suggestions = generate_suggestions(cleaned_word)
                if len(suggestions) > 0:
                    selected_suggestion = suggestions[0]
                    print("Changed '" + cleaned_word + "' to " + selected_suggestion)
                    word = insert_punctuation(selected_suggestion, removed_punctuations)
                    return word
                else:
                    print("UNFIXABLE WORD: " + cleaned_word)
                    word = insert_punctuation(cleaned_word, removed_punctuations)
                    return word

''' Testing Section '''

sample_tweet_nss_1_arr = sample_tweet_nss_1.split(' ')
'''
print('Test 1...')
for word in sample_tweet_nss_1_arr:
    eligible = normalization_eligibility_check(word)
    print(word + ", Eligibility: " + str(eligible))
print()
'''

if len(sys.argv) == 1:
    print('Normalizing Local...')
    original_sentence = sample_tweet_nss_1
    changed_sentence = []
    for word in sample_tweet_nss_1_arr:
        changed_word = pipeline(word)
        changed_sentence.append(changed_word)
    print('Original Sentence: ' + str(original_sentence))
    print('Changed Sentence: ' + ' '.join(changed_sentence))

if len(sys.argv) == 2:
    print('Normalizing user input...')
    original_input = sys.argv[1].split(' ')
    changed_input = []
    for word in original_input:
        changed_word = pipeline(word)
        changed_input.append(changed_word)
    print('Original Tweet: ' + str(original_input))
    print('Changed Tweet: ' + ' '.join(changed_input))


if len(sys.argv) == 3:
    if FROM_TWITTER:
        print('Normalizing tweets...')
        for tweet in tweets:
            changed_tweet = []
            for word in tweet.split(' '):
                changed_word = pipeline(word)
                changed_tweet.append(changed_word)
            print('--------------------------------')
            print('Original Tweet: ' + tweet)
            print('Changed Tweet: ' + ' '.join(changed_tweet))
            print('--------------------------------')
    elif FROM_FILE:
        print('Testing File Input...')
        changed_data = []
        for line in file_data:
            split_line = line.split(' ')
            changed_line = []
            for word in split_line:
                changed_word = pipeline(word)
                changed_line.append(changed_word)
            changed_line = ' '.join(changed_line)
            changed_data.append(changed_line + '\n')
        output = open("changed_" + filename, "w")
        for changed_line in changed_data:
            output.write(changed_line)
        output.close()
