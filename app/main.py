from flask  import Flask,render_template,request, redirect, url_for, flash,session, jsonify
import pandas as pd
import joblib
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__)

app.config['SECRET_KEY'] = 'bibek_kumar_21'

DB_HOST="localhost"
DB_NAME="msedb"
DB_USER="postgres"
DB_PASS="bibek20"

conn=psycopg2.connect(dbname=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST)

# importing the datasets for create a dropdown list in "@app.route('/predict')"
data=pd.read_csv("Cleaned1.csv")

############################################################
##  Function for prediction  ##

# For the Model_1
def model_1(Country, Balance, Product, Month, Date):
    input_data = [[Country, Balance, Product, Month, Date]]
    
    # Load the encoders
    country_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\country_encoder.pkl')
    balance_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\balance_encoder.pkl')
    product_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\product_encoder.pkl')
    month_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\month_encoder.pkl')
    
    # Create a DataFrame for the input data
    input_df = pd.DataFrame(input_data, columns=['Country', 'Balance', 'Product', 'Month', 'Data'])
    
    # Encode the input data
    input_df['Country'] = country_encoder.transform(input_df['Country'])
    input_df['Balance'] = balance_encoder.transform(input_df['Balance'])
    input_df['Product'] = product_encoder.transform(input_df['Product'])
    input_df['Month'] = month_encoder.transform(input_df['Month'])
    
    # Extract the features
    input_features = input_df[['Country', 'Balance', 'Product', 'Month', 'Data']].values
    
    # Load the trained model
    model = joblib.load(r'C:\Users\bdala\Desktop\Project1\Model_1.pkl') 

    # Make a prediction
    predicted_price = model.predict(input_features)
    return str(predicted_price[0].round())
    

#For the model_2
def model_2(Country, Balance, Product, Month, Date):
    input_data = [[Country, Balance, Product, Month, Date]]
    # Load the encoders
    country_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\country_encoder.pkl')
    balance_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\balance_encoder.pkl')
    product_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\product_encoder.pkl')
    month_encoder = joblib.load(r'C:\Users\bdala\Desktop\Project1\month_encoder.pkl')

    
    # Create a DataFrame for the input data
    input_df = pd.DataFrame(input_data, columns=['Country', 'Balance', 'Product', 'Month', 'Data'])
    
    # Encode the input data
    input_df['Country'] = country_encoder.transform(input_df['Country'])
    input_df['Balance'] = balance_encoder.transform(input_df['Balance'])
    input_df['Product'] = product_encoder.transform(input_df['Product'])
    input_df['Month'] = month_encoder.transform(input_df['Month'])
    
    # Extract the features
    input_features = input_df[['Country', 'Balance', 'Product', 'Month', 'Data']].values
    
    # Load the trained model
    model = joblib.load(r'C:\Users\bdala\Desktop\Project1\Model_2.pkl')  # Use model_2.pkl if appropriate
    
    # Make a prediction
    predicted_price = model.predict(input_features)
    return str(predicted_price[0].round())
############################################################

#----------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html') 

# About section
@app.route('/about')
def home():
        return render_template('descrption.html')  

# Render the home page on successful login
@app.route('/demandforecasting')
def demandforecasting():
    return render_template('demandforecasting.html')

@app.route('/data_analysis')
def data_analysis():
    return render_template('data_analysis.html')

@app.route('/Customizable_Inputs')
def Customizable_Inputs():
    return render_template('Customizable_Inputs.html')

#contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        
        # Perform server-side validation (optional)
        if not name or not email or not message:
            flash('Please fill in all required fields (name, email, and message).', 'error')
            return render_template('contact.html')
        
        try:
            # Insert data into the database
            cursor.execute("INSERT INTO contact(name, email, phone, message) VALUES (%s, %s, %s, %s)", 
                           (name, email, phone, message))
            conn.commit()
            flash('Thanks for reaching out! We’ll get back to you soon.', 'success')
        except Exception as e:
            conn.rollback()  # Rollback the transaction on error
            flash('An error occurred while sending your message. Please try again.', 'error')
            print(str(e))  # Debugging, print the error to the console
    
    return render_template('contact.html')

#Signup page
@app.route('/signupform',methods=['GET', 'POST'])
def signup():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        email = request.form['email']
        company = request.form['company']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        _hashed_password=generate_password_hash(password)
        if not username or not email or not company or not phone or not password or not confirm_password:
            flash('Please fill out all fields!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+$', email):
            flash('Invalid email address!', 'error')
        elif not re.match(r'[A-Za-z0-9]+$', username):
            flash('Username must contain only letters and numbers!', 'error')
        elif password != confirm_password:
            flash('Passwords do not match!', 'error')
        else:
            # Check if account already exists
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()

            if account:
                flash('Account already exists!', 'error')
            else:
                # Hash the password and store the account
                hashed_password = generate_password_hash(password)
                cursor.execute("INSERT INTO users (username, email, company, phone, password) VALUES (%s, %s, %s, %s, %s)", 
                               (username, email, company, phone, hashed_password))
                conn.commit()
                flash('You have successfully registered!', 'success')
        #return redirect(url_for('login'))
    return render_template('signupform.html')

#log in page
@app.route('/login',methods=['GET','POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Fetch the account by username (assuming the username is unique)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            password_rs = account['password']  # The hashed password stored in the database
            print(password_rs)
            
            # Check if the entered password matches the stored hashed password
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['username'] = account['username']
                return redirect(url_for('predict'))
            else:
                flash('Incorrect password', 'error')
        else:
            flash('Account does not exist or incorrect username!', 'error')
        
    
    return render_template('login.html')
    
# FAQ page
@app.route('/containt')
def containt():
    return render_template('containt.html') 

#------------------------------------------------------------------------------------------------

#Prediction
@app.route('/predict',methods=['GET','POST'])
def predict():
    Country=sorted(data['Country'].unique())
    Balance=sorted(data['Balance'].unique())
    Product=sorted(data['Product'].unique())
    Month=sorted(data['Month'].unique())
    
    if request.method == 'POST': # We declar outside variables because to ensure they are initialized for both GET and POST requests
        predict=request.form['predict']
        return render_template('predict.html',predict=predict,Country=Country,Balance=Balance,Product=Product,Month=Month)
    return render_template('predict.html',Country=Country,Balance=Balance,Product=Product,Month=Month)    


@app.route('/price', methods=['GET', 'POST'])
def price_pred():
    try:
        Country = request.form.get('Country')
        Balance = request.form.get('Balance')
        Product = request.form.get('Product')
        Month = request.form.get('Month')
        Date = request.form.get('Date')
        
        # Validate Date
        if not Date : #Check the user must fill the date 
            return jsonify({"error": "Please fill up the date."}), 400
        
        if  not Date.isdigit() or int(Date) < 1 or int(Date) > 31:  #check if it's between 1 and 31
            return jsonify({"error": "Invalid Date. Please enter a valid date between 1 and 31."}), 400

        # Call the appropriate model based on Balance
        if Balance == "Net Electricity Production":
            predicted_value = model_2(Country, Balance, Product, Month, Date)
        else:
            predicted_value = model_1(Country, Balance, Product, Month, Date)

        return str(predicted_value)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ =='__main__':
    app.run(debug=True,port=7000)