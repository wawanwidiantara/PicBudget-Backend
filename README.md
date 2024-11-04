# PicBudget

**PicBudget** is a Django-based & Flutter application designed to deploy an AI model that extracts key information from receipts, making personal finance management and expense tracking seamless. The app processes receipt images to extract essential details like merchant name, date, and total amount, then organizes this information for easy budget management and analysis.

## Features

- **AI-driven Data Extraction**: Leverages an AI model to read and extract data from receipt images automatically.
- **Money Tracking**: Allows users to track their expenses by storing receipt data and categorizing expenditures.
- **Expense Analysis**: Provides visual analytics and insights into spending habits, helping users make informed financial decisions.
- **Wallets Feature**: Users can create multiple wallets (e.g., for personal, business, or shared expenses) to organize and track spending across categories.
- **Login Integration (Google & Apple)**: Offers secure login options through Google and Apple for a streamlined authentication experience.

## Prerequisites

- **Python** 3.10+
- **Django** 5.1+
- **Docker** & **Docker Compose** (for containerized deployment)
- Other dependencies listed in `requirements.txt`

## Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/PicBudget.git
   cd PicBudget

2. **Install Dependencies**
   ```bash
   make install
   
3. **Apply Migrations**
   ```bash
   make migrate

4. **Run the Development Server**
   ```bash
   make run-server

## Version Information
Version 1 of PicBudget's backend is available at [GitHub Repository: PicBudget v1](https://github.com/WawanWidiantara/PicBudget-Backend/tree/picbudget-be-v1).

## License
This project is licensed under the MIT License.




