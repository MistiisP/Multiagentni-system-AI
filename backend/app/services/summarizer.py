import yake

kw_extractor = yake.KeywordExtractor(
    lan="en",          
    n=3,               #max tokens
    dedupLim=0.9,      
    top=1,             #min tokens
    features=None
)

def get_name_summary(text: str) -> str:
    if not text:
        return "Nová konverzace"
    
    keywords = kw_extractor.extract_keywords(text)
    keyword_texts = [kw[0] for kw in keywords]
    
    full_title = " ".join(keyword_texts)
    short_title = " ".join(full_title.split()[:5])

    final_title = short_title.capitalize()
    
    return final_title[:49]

