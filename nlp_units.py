from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def classify_comment(text):
    results = classifier(text)
    result = results[0] 
    label= result['label']
    score=result['score']

    if label in ['POSITIVE', '5 stars', '4 stars']:
        return "Позитивно", score
    elif label in ['NEGATIVE', '1 star', '2 stars']:
        return "Негативно", score
    else:
        return "Нейтрально", score