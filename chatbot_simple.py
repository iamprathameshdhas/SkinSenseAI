import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import re

# Download NLTK resources (run this once)
nltk.download('punkt')
nltk.download('stopwords')

# Function to preprocess text
def preprocess_text(text):
    # Tokenize into words
    tokens = word_tokenize(text)
    
    # Convert to lowercase
    tokens = [token.lower() for token in tokens]
    
    # Remove punctuation
    tokens = [token for token in tokens if re.match(r'\w', token)]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    return tokens

# Sample text about melanoma (replace with actual extracted text)
sample_text = """
Melanoma is a type of skin cancer that develops from melanocytes, the pigment-producing cells in the skin.
Exposure to ultraviolet (UV) radiation from sunlight is the primary cause of melanoma.
Other risk factors include a family history of melanoma, having fair skin, and having many moles.
Symptoms of melanoma include changes in the size, shape, or color of moles, as well as the development of new moles.
If detected early, melanoma can be treated effectively with surgery, but advanced melanoma may require additional treatments such as chemotherapy or immunotherapy.
"""

# Preprocess the sample text
preprocessed_text = preprocess_text(sample_text)

# Define keywords related to melanoma, causes, and effects
melanoma_keywords = ["melanoma", "skin cancer", "uv radiation", "melanocytes", "moles", "symptoms", "treatment"]
causes_keywords = ["causes", "risk factors", "exposure to sunlight", "family history", "fair skin"]
effects_keywords = ["symptoms", "treatment", "surgery", "chemotherapy", "immunotherapy"]

# Function to classify user question
def classify_question(question):
    if any(word in question.lower() for word in melanoma_keywords):
        return "melanoma"
    elif any(word in question.lower() for word in causes_keywords):
        return "causes"
    elif any(word in question.lower() for word in effects_keywords):
        return "effects"
    else:
        return "other"

# Function to retrieve answers based on question category
def retrieve_answer(question, preprocessed_text):
    sentences = sent_tokenize(sample_text)
    relevant_sentences = []
    for sentence in sentences:
        if any(word in sentence.lower() for word in preprocess_text(question)):
            relevant_sentences.append(sentence)
    return relevant_sentences

# Function to generate an answer from retrieved sentences
def generate_answer(relevant_sentences):
    if relevant_sentences:
        answer = " ".join(relevant_sentences)
    else:
        answer = "I'm sorry, I couldn't find an answer to that question."
    return answer

# Chatbot function
def chat():
    print("Welcome to the Melanoma Chatbot!")
    print("Ask me anything about melanoma, its causes, or effects. Type 'exit' to end the chat.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Exiting the chat.")
            break
        question_category = classify_question(user_input)
        relevant_sentences = retrieve_answer(user_input, preprocessed_text)
        answer = generate_answer(relevant_sentences)
        print("Chatbot:", answer)

# Run the chatbot
if __name__ == "__main__":
    chat()
