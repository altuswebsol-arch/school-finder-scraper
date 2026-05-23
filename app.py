from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        location = request.form['location']
        
        # 1. Setup Driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        url = f"https://www.google.co.uk/maps/search/schools+in+{location}"
        driver.get(url)
        time.sleep(5)  # Wait for page to load
        
        # 2. Scroll Logic
        # We find the sidebar container first
        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[aria-label^="Results for"]')
        
        for _ in range(3): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2) # Give it time to load new results

        # 3. Extraction Logic
        school_names = driver.find_elements(By.CLASS_NAME, "qBF1Pd")
        results = []
        for name in school_names:
            if name.text: # Only add if the name is not empty
                results.append({'Name': name.text})
            
        # 4. Save to Excel
        df = pd.DataFrame(results)
        df.to_excel("schools_output.xlsx", index=False)
        
        driver.quit()
        return send_file("schools_output.xlsx", as_attachment=True)
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)