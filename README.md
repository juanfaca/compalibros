**Compalibros** is a specialized web scraper and price aggregator designed to help readers in Lima, Peru, find the best deals for their favorite books. By simply using an **ISBN**, the app crawls major local bookstores to provide an instant price comparison.

### 🎯 Why Compalibros?
Finding the best price for a book in Lima often requires checking multiple websites (Crisol, SBS, El Virrey, etc.) manually. This application automates the search, saving time and money for the user.

### ✨ Key Features
* **🔍 ISBN-Driven Search:** Precise matching to avoid title confusion.
* **💰 Automated Scraping:** Real-time data retrieval from Lima’s main bookstores.
* **📖 Book Insights:** Integration with the **OpenLibrary API** to fetch book abstracts and metadata.
* **⚡ Clean UI:** Built with Streamlit for a fast, responsive experience.

### 🛠️ Tech Stack
* **Language:** Python 100%
* **Libraries:** Requests, Cloudscraper, BeautifulSoup4 (Scraping), Pandas.
* **Web Framework:** [Streamlit](https://streamlit.io/).
* **Data Sources:** Local bookstore websites + OpenLibrary API.

### 🚀 How to Use
1. **Access the App:** Visit [compalibros.streamlit.app](https://compalibros.streamlit.app/).
2. **Find an ISBN:** Locate the 13-digit code (e.g., *978-84-8393-355-8* for Joseph Roth's "Cuentos Completos").
3. **Search:** Enter the ISBN in the box and click **"Buscar"**.
4. **Compare:** View the price list and the book's abstract in seconds.

### ⚠️ Maintenance Logs
* **Jan 2026 Update:** *Communitas* scraping is currently restricted due to regional server requirements (Peru-only IP).
* **Oct 2025 Update:** *Buscalibre* implemented advanced CAPTCHA security, temporarily disabling automated extraction.
