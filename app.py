from flask import Flask, render_template, request, redirect, url_for, flash
from Forms import CreateUserForm, LoginForm, SignUpForm, UserDetailsForm, ChangePasswordForm, AddressForm
import User, main, Product


app = Flask(__name__)
main.init()

# Main page
# Current is Login Page
@app.route('/')
def home():
    return render_template('home.html')


# Called For testing
# HF
@app.route('/testing/<choice>')
def testing(choice):
    #return 'Test successful, code is {}'.format(code)
    return render_template('users.html')


# Called when user successful logged in
# HF
@app.route('/users/<username>/<int:choice>', methods=['POST', 'GET'])
def users(choice, username):
    print("TESTTTTT")
    temp = main.db.return_keys("Users")
    user_form = UserDetailsForm(request.form)
    password_form = ChangePasswordForm(request.form)
    address_form = AddressForm(request.form)

    if request.method == 'POST':
        btn_pressed = request.form['submit']
        user_db = main.db.get_storage("Users")
        user = user_db[username]

        if btn_pressed == "Update Profile" and user_form.validate():
            user.set_username(user_form.username.data.lower())
            user.set_first_name(user_form.first_name.data)
            user.set_last_name(user_form.last_name.data)

            to_be_changed = main.db.get_storage("TEMP")
            to_be_changed["username"] = user.get_username()

            main.db.set_storage("TEMP", to_be_changed)

        elif btn_pressed == "Update Address" and address_form.validate():
            user.set_country(address_form.country.data)
            user.set_postal_code(address_form.postal_code.data)
            user.set_address(address_form.address.data)
            user.set_city(address_form.city.data)
            user.set_unit_number(address_form.unit_number.data)

        elif btn_pressed == "Change Password" and password_form.validate():
            user.set_password(password_form.password)

        del user_db[username]
        user_db[user.get_username()] = user
        main.db.set_storage("Users", user_db)

        return redirect(url_for('users', choice=1, username=user.get_username()))

    if temp != None and username in temp:

        temp2 = main.db.get_storage("Users")
        user_details = temp2[username]

        if choice == 1:
            temp_form = user_form
        elif choice == 2:
            temp_form = password_form
        elif choice == 3:
            temp_form = address_form


        return render_template('users.html', menu=choice, user=user_details, form=temp_form)

    else:
        print("ERRORRRRRR")




# Called when admin login
# HF
@app.route('/admin')
def admin():

    return render_template('admin.html')


# Called when sign up button is clicked from the login page
# HF
@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    signup_form = SignUpForm(request.form)
    if request.method == 'POST' and signup_form.validate():

        user = User.User(signup_form.first_name.data, signup_form.last_name.data, signup_form.username.data.lower(),
                         signup_form.password.data, signup_form.postal_code.data, signup_form.address.data,
                         signup_form.country.data, signup_form.city.data, signup_form.unit_number.data)

        # to create and check if the storage exist
        main.db.get_storage('Users', True, True)
        main.db.add_item('Users', user.get_username(), user)

        # create temporary storage
        main.db.get_storage("TEMP", True, True)
        main.db.add_item('TEMP', "username", user.get_username())

        return redirect(url_for('users', choice=1, username=user.get_username()))

    return render_template('signUp.html', form=signup_form)


# Called when user press submit at main page
# Two methods, GET is called when website request the page
# There is POST request only when user click the submit button
# HF
@app.route('/loginMenu', methods=['POST', 'GET'])
def loginMenu():
    login_form = LoginForm(request.form)

    # login if user already logged in before
    temp_exist = main.db.check_exist('TEMP')
    if temp_exist == True:

        session = main.db.get_storage('TEMP')
        s_keys = session.keys()

        if "username" in s_keys:
            username = session['username']
            return redirect(url_for('users', choice=1, username=username))


    # When a button is clicked
    if request.method == 'POST':
        btn_pressed = request.form['submit']

        # Login clicked
        # Validate only on a POST request
        if login_form.validate() and btn_pressed == "Login":
            login_name = login_form.username.data.lower()


            admin_acc = main.db.get_storage("ADMIN")
            temp = main.db.return_keys("Users")

            if admin_acc.get_username() == login_name:
                print("Admin Login")
                return redirect(url_for('admin'))

            elif temp != None and login_name in temp:
                temp2 = main.db.get_storage("Users")
                user = temp2[login_name]

                # create temporary storage
                main.db.get_storage("TEMP", True, True)
                main.db.add_item('TEMP', "username", user.get_username())

                return redirect(url_for('users', choice=1, username=user.get_username()))

            else:
                print("ERRORRRRRR")


        # Sign up clicked
        elif btn_pressed == "Sign Up":
            return redirect(url_for('sign_up'))

    # Get request will be skipped to this

    return render_template('userLogin.html', form=login_form)


# Figuring out carting system
# JH
# STILL TESTING
@app.route("/testAddItem", methods=["GET", "POST"])
def testAddItem():

    # if request.method == "POST":
    #     if request.form["submit_button"] == "Add":
    #         print("Add item button pressed")
    #     elif request.form["submit_button"] == "Delete":
    #         print("Delete item button pressed")

    if request.method == "POST":
        # Create the product object
        product = Product.Product(1, "Airpods", 239.00)
        # Add it into the database
        main.db.get_storage("Cart", True , True)
        main.db.add_item("Cart", "TestUser", product)
        print("-- TEST --")
        test = main.db.return_object("Cart")
        test = test["TestUser"]
        print(f"Product Name: {test.get_name()}, Cost: {test.get_cost()}, ID: {test.get_id()}")
        print("-- TEST --")
    return render_template("test.html")


# Shopping cart page
# JH
# STILL TESTING
@app.route("/cart")
def cart():
    main.db.get_storage("Cart", True, True)
    product_object = main.db.return_object("Cart")
    product_object = product_object["TestUser"]
    return render_template("userCart.html", item=product_object)



if __name__ == '__main__':
    app.run()