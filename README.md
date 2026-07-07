# 🛒 AI E-commerce Shopping Assistant

An AI-powered FAQ Chatbot built using **Python**, **Natural Language Processing (NLP)**, **TF-IDF Vectorization**, **Cosine Similarity**, and **Streamlit**.

The chatbot answers frequently asked e-commerce questions such as order tracking, returns, refunds, shipping, payment methods, cancellations, coupons, and more through an interactive chat interface.

---

## ✨ Features

- 🤖 AI-powered FAQ chatbot
- 💬 ChatGPT-inspired chat interface
- 🧠 Intent detection for greetings, thanks, and small talk
- 🔍 TF-IDF Vectorization
- 📊 Cosine Similarity-based answer retrieval
- ⚡ Fast response using cached chatbot initialization
- 📝 Conversation history
- 🗂 Sidebar chat management
- 🌙 Modern dark UI built with Streamlit
- 📱 Responsive design

---

## 🛠 Technologies Used

- Python
- Streamlit
- Pandas
- NLTK
- Scikit-learn
- TF-IDF Vectorizer
- Cosine Similarity

---

## 📂 Project Structure

```text
AI-E-commerce-FAQ-Chatbot/
│
├── app.py
├── chatbot.py
├── preprocess.py
├── intent_handler.py
├── faq.csv
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│
└── screenshots/
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone git@github.com:Afzalkhan36/AI-E-commerce-FAQ-Chatbot.git
```

### 2. Move into the project

```bash
cd AI-E-commerce-FAQ-Chatbot
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

---

## 💬 Example Questions

- Where is my order?
- How do I return a product?
- What payment methods are accepted?
- How can I cancel my order?
- Do you provide free shipping?
- Tell me a joke
- Hi
- Thanks

---

## 📸 Screenshots

### Home Screen

![Home](screenshots/home.png)

### Chat Interface

![Chat](screenshots/chat.png)

### Sidebar

![Sidebar](screenshots/sidebar.png)

---

## 🔍 How It Works

1. User enters a question.
2. Text preprocessing is applied.
3. TF-IDF vectorization converts text into numerical vectors.
4. Cosine Similarity finds the closest matching FAQ.
5. The chatbot returns the most relevant answer.
6. Greetings and small talk are handled separately using intent detection.

---

## 🎯 Future Improvements

- Voice input
- Speech output
- Multi-language support
- LLM integration
- Product recommendation system
- User authentication
- Database integration
- Conversation memory

---

## 👨‍💻 Developer

**Afzal Khan**

GitHub: https://github.com/Afzalkhan36

---

## ⭐ If you like this project

Give this repository a ⭐ on GitHub.
