```markdown
# Crediflow

This repository contains the solution to the assignment provided as part of an interview process for a full-stack position at Crediflow.

---

## Project Setup

### Step 1: Create a Virtual Environment
Set up a virtual environment using the following command:
```bash
python -m venv env
```

### Step 2: Activate the Virtual Environment
- **On Windows**:
  ```bash
  env\Scripts\activate
  ```

- **On macOS/Linux**:
  ```bash
  source env/bin/activate
  ```

### Step 3: Run the Server
Run the script to start the server on port `8080`:
```bash
python3 main.py
```

---

## Dependencies Management

- To update the `requirements.txt` file whenever a new dependency is added:
  ```bash
  pip freeze > requirements.txt
  ```

- To install all required dependencies from the `requirements.txt` file:
  ```bash
  pip install -r requirements.txt
  ```

---

## Features

### API Endpoint
- **Endpoint**: `/products`
- **Functionality**: Returns a list of products based on a price range and a limit.
- **Pydantic Model**:
  ```python
  class ProductModel(BaseModel):
      name: str
      price: float
      description: str
  ```
- **Parameters**:
  - `price_range`: A range of prices, e.g., `100-500`.
  - `limit`: The number of items to return, e.g., `6`.
- **Response Example**:
  ```json
  [
    {
      "name": "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
      "price": 109.95,
      "description": "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday"
    },
    {
      "name": "Solid Gold Petite Micropave",
      "price": 168,
      "description": "Satisfaction Guaranteed. Return or exchange any order within 30 days. Designed and sold by Hafeez Center in the United States."
    }
  ]
  ```
- **Slack Notification**:
  Whenever the endpoint is accessed, the product with the lowest price in the specified range is sent to a Slack channel in the following format:
  ```
  - Name: Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops
  - Price: 109.95
  - Description: Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday
  This is the cheapest product within this price range.
  ```

---

### Slack Integration
- Users can interact with the application via Slack.
- **Input Format**:
  ```
  query - range (e.g., 100-200) - number (e.g., 5)
  ```
  Example: `query - 100-200 - 5` will return 5 products within the price range of 100 to 200.
- The following data is stored in a database:
  - Slack user ID who made the query.
  - Query details.

--- 

## Author
Solution designed and implemented as part of an assignment for Crediflow's full-stack position by ```Gibril Idrisu Issaka```

## Swagger Docs
You can play with the endpoints [here](https://crediflow.onrender.com/docs). 
```

