import openai
from configparser import ConfigParser

class SEOOptimizer:
    def __init__(self, language, writing_rules,title_rules,description_rules):
        self.language = language
        self.writing_rules = writing_rules
        self.title_rules = title_rules
        self.description_rules = description_rules
        config = ConfigParser()
        config.read('config.ini')
        self.openai_api_key = config['DEFAULT']['openai_api_key']
    
    def optimize_text(self, text, type_text, keywords=None):
        type_text
        if type_text == 'title':
            min_len, max_len = 53, 62
        elif type_text == 'description':
            min_len, max_len = 135, 155
        prompt = f"Optimize this text (it is a {type_text}) for SEO in {self.language} following these rules: {self.writing_rules}. \
            Original text to be rewritten: '{text}'. \
            Just output the output text itself, without any introduction, additional punctuation or additional context. \
            I.e. if the input is TEXT your output should only be OPTIMIZEDTEXT."
        if keywords:
            prompt += f" Keywords: '{keywords}'."
        
        if type_text == 'title':
            prompt = prompt + f"REMEMBER, THIS IS IMPORTANT: Keep the total length of your output between {min_len} chars and {max_len} chars. \
                No more!! Remember also these rules for {type_text}: " + self.title_rules
        if type_text == 'description':
            prompt = prompt + f"REMEMBER, THIS IS IMPORTANT: Keep the total length of your output between {min_len} chars and {max_len} chars. \
                No more!! Remember also these rules for {type_text}: " + self.description_rules
        

        print("PROMPT: "+prompt)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a SEO expert."}, {"role": "user", "content": prompt}],
            api_key=self.openai_api_key
        )
        optimized_text= response.choices[0].message['content']
        optimized_text = optimized_text.strip('"\'')

        return optimized_text
    
    def check_length(self, text, min_len, max_len):
        return min_len <= len(text) <= max_len

    def optimize_for_length(self, text, type_text, keywords=None, attempts=0):
        optimized_text = self.optimize_text(text, type_text,keywords)
        if type_text == 'title':
            min_len, max_len = 53, 62
        elif type_text == 'description':
            min_len, max_len = 135, 155
        else:
            return optimized_text

        if self.check_length(optimized_text, min_len, max_len) or attempts >= 3:
            return optimized_text
        else:
            return self.optimize_for_length(text, type_text, keywords, attempts + 1)
