import mysql.connector
from wtforms import Form, DateField, IntegerField
from flask import Flask, render_template, request
from tabulate import tabulate


dates = {"begin": "", "end": ""}
global_available_cars = []

app = Flask(__name__, template_folder='templates')
app.secret_key = "123123123"


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="blabla",
    database="main"
)

mycursor = mydb.cursor(buffered=True)

mycursor.execute("DROP TABLE cars")
mycursor.execute("CREATE TABLE cars (order_id INT AUTO_INCREMENT PRIMARY KEY, id INT , carType VARCHAR(255), size INT, prize FLOAT, date_begin DATE, date_end DATE)")


sql = "INSERT INTO cars (id, carType, size, prize, date_begin, date_end) VALUES (%s, %s, %s, %s, %s, %s)"
val = [
    ('1','BMW X4', '5', '80', '1111-11-1', '1111-11-1'),
    ('2','Hyundai i20', "4", "35", '1111-11-1', '1111-11-1'),
    ('3',"Audi A3", "5", "48", '1111-11-1', '1111-11-1'),
    ('4',"Nissan X-Trail", "4", "60", '1111-11-1', '1111-11-1'),
    ('5',"BMW Z4 Roadster", "4", "107", '1111-11-1', '1111-11-1'),
]
mycursor.executemany(sql, val)


class RentalForm(Form):
    begin = DateField('Begin')
    end = DateField('End')
    print(begin)
    print(end)


class IdForm(Form):
    request_id = IntegerField('Request_id')


@app.route('/available/', methods=["GET", "POST"])
def available():
    form = RentalForm(request.form)
    if request.method == "POST":
        form = RentalForm(request.form)
        begin = form.begin.data
        end = form.end.data
        dates["begin"] = begin
        dates["end"] = end
        if begin > end:
            return("""Your selected starting day should be before your selected end day!
                               <br>
                               <br>
                               <form action="/" class="form-inline" method="post">
                                   <a> <button class="button" name="back"> Back </button> </a>
                               </form>"""
                )
        else:
            unavailable_cars = []
            mycursor.execute("SELECT id FROM cars WHERE date_begin <= %s AND date_end >= %s", [end, end])
            for x in mycursor.fetchall():
                unavailable_cars.append(x[0])

            mycursor.execute("SELECT id FROM cars WHERE date_begin <= %s AND date_end >= %s", [begin, begin])
            for x in mycursor.fetchall():
                unavailable_cars.append(x[0])

            mycursor.execute("SELECT id FROM cars WHERE date_begin >= %s AND date_end <= %s", [begin, end])
            for x in mycursor.fetchall():
                unavailable_cars.append(x[0])

            all_cars = []
            mycursor.execute("SELECT id FROM cars")
            for x in mycursor.fetchall():
                all_cars.append(x[0])
            global available_cars
            available_cars = list(set(all_cars).difference(set(unavailable_cars)))

            return show_results(available_cars)
    return render_template('available.html', form=form)


@app.route('/rent/', methods=["GET", "POST"])
def rent():
    form_id = IdForm(request.form)
    if form_id.request_id.data not in available_cars:
        return("""This car can not be rented right now!

               
                       <br>
                       <br>
                       <form action="/" class="form-inline" method="post">
                           <a> <button class="button" name="back"> Back </button> </a>

                       </form>"""
               )
    else:
        begin = dates["begin"]
        end = dates["end"]

        mycursor.execute("SELECT id, carType, size, prize, date_begin, date_end FROM cars WHERE id = %s", [form_id.request_id.data])
        temp = list(mycursor.fetchone())
        temp[4] = begin
        temp[5] = end
        sql = "INSERT INTO cars (id, carType, size, prize, date_begin, date_end) VALUES (%s, %s, %s, %s, %s, %s)"
        val = tuple(temp)
        mycursor.execute(sql, val)

        mycursor.execute("SELECT carType FROM cars WHERE id = %s", [form_id.request_id.data])
        result = mycursor.fetchone()


    mycursor.execute("SELECT * FROM cars")
    myresult = mycursor.fetchall()

    for x in myresult:
        print(x)
    return f"""Congratulations, your reservation for {result[0]} worked.
        <br>
        <br>
        <form action="/" class="form-inline" method="post">
            <a> <button class="button" name="back"> Back </button> </a>

        </form>"""


@app.route("/", methods=["GET","POST"])
def index():
    return render_template('index.html')


def show_results(available_cars):
    #mycursor.execute("SELECT * FROM cars")
    #myresult = mycursor.fetchall()
    #for x in myresult:
    #    print(x)
    if len(available_cars) > 0:
        car_names = []
        for id in available_cars:
            mycursor.execute("SELECT id, carType, size, prize FROM cars WHERE id = %s", [id])
            car_names.append(mycursor.fetchone())
        table = tabulate(car_names, tablefmt='html', headers=["ID", "Car Type", "Size", "Price in (€)"])

        return(f"The following cars are available in your selected time slot:" + table + """
        <br>
        <br>
        <form action="/rent/" class="form-inline" method="post">
            <input type="number" class="form-control" placeholder="Enter ID" name="request_id" value="{{request.form.request_id}}"/>
                        <input class="btn btn-default" type="submit" value="ID"/>

        </form>""")
    else:
        return("""There are no cars available in the requested timeslot.        
        <br>
        <br>
        <form action="/" class="form-inline" method="post">
            <a> <button class="button" name="back"> Back </button> </a>

        </form>""")


if __name__ == "__main__":
    app.run()