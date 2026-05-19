import re
import unicodedata

class TextCleaner:
    """Class to clean and preprocess text for analysis"""
    def __init__(self):
        self.markdown_re = re.compile(r'[*_#~`>|-]')
        self.url_re = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_re= re.compile(r'[\w\.-]+@[\w\.-]+')
        self.special_char_re = re.compile(r'[^\w\s.,;:!?\'"()\[\]-]')
        self.multiple_spaces_re = re.compile(r'\s+')
    
    def normalize_unicode(self, text):
        """Normalize unicode characters to their closest ASCII representation"""
        text = unicodedata.normalize('NFKD', text)
        text= text.replace('"', '"').replace("'", "'").replace('“', '"').replace('”', '"')
        return text
    
    def remove_urls_emails(self, text):
        """Remove URLs and email addresses from the text"""
        text = self.url_re.sub('[URL]', text)
        text = self.email_re.sub('[EMAIL]', text)
        return text
       
    def clean(self, text):
        """Main method to clean text by applying various preprocessing steps"""
        if not text or len(text.strip())==0:
            return ""
        
        text = self.normalize_unicode(text)
        text = self.remove_urls_emails(text)
        text = self.markdown_re.sub('', text)
        text = self.special_char_re.sub('', text)
        text = self.multiple_spaces_re.sub(' ', text).strip()
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
