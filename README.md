# <span style="color:#4CAF50;">ChatBot NLP - Online Ordering System</span>

A conversational chatbot built with Dialogflow, FastAPI, and SQL to assist users in placing and managing orders online. This chatbot allows users to interact with the system, place orders, and track them with ease.

---

## <span style="color:#2196F3;">Technologies Used</span>

- **Dialogflow**: A Google cloud service used to create and manage conversational intents, providing natural language understanding (NLU) and processing for the chatbot.
- **FastAPI**: A fast, modern Python web framework for building APIs, used to create the backend service for the chatbot.
- **uvicorn**: A lightning-fast ASGI server to run the FastAPI application.
- **SQL**: Used for storing user data, order details, and tracking order progress in the backend.
- **ngrok**: A tool to expose your local FastAPI server to the internet, useful for testing and demonstrating the chatbot in real-time.
- **PyCharm**: An integrated development environment (IDE) used for developing the chatbot.
- **Python**: The primary programming language for backend logic and API development.
- **NLP**: Natural Language Processing techniques for understanding and responding to user queries.

---

## <span style="color:#2196F3;">Features Implemented</span>

### Dialogflow Intents:
The chatbot is built using Dialogflow, which contains the following **Nine Intents**:

1. **Default Welcome Intent**: Greets the user when they first interact with the chatbot.
2. **new.order**: Initiates a new order.
3. **order.add** - *Context: ongoing-order*: Adds items to the user's ongoing order.
4. **order.complete** - *Context: ongoing-order*: Completes the ongoing order and finalizes it.
5. **order.remove** - *Context: ongoing-order*: Removes items from the ongoing order.
6. **store.timings**: Provides the store's working hours.
7. **track.order**: Allows the user to track the status of their order.
8. **track.order** - *Context: ongoing-tracking*: Provides more specific tracking information for ongoing orders.
9. **Default Fallback Intent**: Handles any unrecognized queries or responses, providing an error message or a helpful suggestion.

---

### <span style="color:#2196F3;">Entity</span>:

- **food-item**: Defines the different food items that users can order, allowing the chatbot to process and recognize items dynamically.

---

### <span style="color:#2196F3;">Backend</span>:
The backend is powered by **SQL**, where orders and user data are stored and managed to ensure smooth order processing and tracking. The SQL database interacts with the chatbot's logic to help users easily place and track their orders.

---

## <span style="color:#2196F3;">Requirements</span>

To run this project, you need to install the following Python packages:

- **mysql-connector-python**: A Python library for connecting to MySQL databases.
- **fastapi**: The Python web framework used to create the backend of the chatbot.

You can install these requirements using the following command:

```bash
pip install mysql-connector-python fastapi
