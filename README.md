# 📄🔍 Electric Invoice Information Extraction Challenge

Welcome to my electric invoice information extraction repository! 🚀

This project aims to develop a generic solution for extracting key information from electric invoices in PDF format, regardless of the design or layout of fields in different invoices. 🧠💡

## 📚 Project Steps

### 1. Resource Gathering

- ✅ Installing Python on my computer.
- ✅ Downloading the training dataset with PDF invoices and their corresponding JSON files.
- ✅ Selecting suitable Python libraries for text extraction, text processing, and machine learning.

### 2. Data Preprocessing

- 📥 Reading PDF and JSON files from the training dataset.
- 🧹 Cleaning the extracted text by removing irrelevant characters and normalizing the text.
- 📑 Structuring the data for easier processing.

### 3. Data Exploration and Analysis

- 🔍 Analyzing the structure and content of PDF and JSON invoices.
- 📊 Identifying patterns and common features, as well as variations in invoice formats.
- 🗂 Segmenting the data into different groups based on their characteristics.

### 4. Defining the Extraction Strategy

- 🛠 Deciding between a rule-based approach or a machine learning model.
  - **Rule-based approach:** Defining manual rules using regular expressions and natural language processing techniques.
  - **Machine learning approach:** Training a suitable model and evaluating its performance.

### 5. Implementing the Solution

- 💻 Implementing the information extraction algorithm.
- 🔄 Developing the logic to process each PDF invoice and store the information in a structured format.
- 🚨 Handling errors and exceptional cases.

### 6. Evaluation and Improvement

- 🧪 Evaluating performance using the provided script to obtain the Levenshtein score.
- 🔄 Refining the extraction strategy based on the obtained results.
- ♻ Repeating the evaluation and improvement process until a satisfactory score is achieved.

### 7. Additional Considerations

- 🌐 Ensuring the generalization of the extraction method for different invoice formats and structures.
- 🛠 Using natural language processing techniques to improve accuracy.
- 📋 Implementing mechanisms to handle errors and exceptional cases.
- 📝 Documenting the code and extraction strategy.

## 🛠 Technologies Used

- **Python** 🐍
- **PyPDF2 / Poppler / pdfminer.six** 📄
- **re / string / nltk** 🔍
- **scikit-learn / TensorFlow** 🤖

## 🚀 Getting Started

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/electric-invoice-extraction.git
    ```
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the extraction script:
The invoice you want to process must be in the same directory as the "executable" script located in the ./dist folder
    ```bash
    ./executable.exe invoice_name.pdf
    ```
    or
    ```bash
    ./executable.exe invoice_path
    ```

## 📞 Contact

Have questions or suggestions? Feel free to contact me on [LinkedIn](https://www.linkedin.com/in/ana-zubieta) 💬

Thank you for visiting my repository! I hope you find this project interesting and useful. 🙌

---

⭐ **If you liked this project, please give it a star and follow me on LinkedIn for more similar content.** ⭐
