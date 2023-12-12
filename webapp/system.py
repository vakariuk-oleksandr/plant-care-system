import streamlit as st
import sqlite3
import pandas as pd

    # Add a style block to the head section of the page
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call the function to load the CSS file
#local_css("style.css")
# Connect to the SQLite database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create PlantTable if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS PlantTable 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, plant_id INTEGER, plant_name TEXT, plant_date TEXT, add_note TEXT)''')
conn.commit()

import streamlit as st

def issue_plant_form():
    st.header("Призначити рослину")
    # plant_Name = st.text_input("Назва рослини:")
    # plant_name = st.text_input("Ім'я користувача:")
    
    plant_options = [row[0] for row in c.execute("SELECT Name FROM plants WHERE status = 'Доступно'")]
    plant_Name = st.selectbox("Назва рослини:", plant_options)

    users_options = [row[0] for row in c.execute("SELECT name FROM users")]
    users_name = st.selectbox("Ім'я користувача:", users_options)

    
    plant_date = st.date_input("Дата призначення:")
    add_note = st.date_input("Термін виконання:")
    submit_button = st.button("Призначити рослину")

    if submit_button:
        issue_plant(plant_Name, users_name, plant_date, add_note)
        st.success(f"{plant_Name} було призначено {users_name} до {add_note}.")

def issue_plant(plant_Name, plant_name, plant_date, add_note):
    c.execute("SELECT * FROM plants where Name = ?",(plant_Name,))
    plant = c.fetchall()
    c.execute("UPDATE plants SET status = 'issued' WHERE Name = ?", (plant_Name,))
    c.execute("INSERT INTO PlantTable (id, plant_id, plant_name, plant_date, add_note) VALUES (NULL,?, ?, ?, ?)",
                   (plant[0][0], plant_name, plant_date, add_note))
    conn.commit()
    # conn.close()  # Remove this line

def users_registration():
    st.header("Реєстрація користувача")
    name = st.text_input("Ім'я:")
    email = st.text_input("Email:")
    address = st.text_input("Адреса:")
    submit_button = st.button("Надіслати")

    if submit_button:
        register_users(name, email, address)
        st.success("Користувач успішно зареєстрований.")

def register_users(name, email, address):
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, address TEXT)''')
    c.execute("INSERT INTO users (id, name, email, address)VALUES (NULL, ?, ?, ?)", (name, email, address))
    conn.commit()
    conn.close()

def view_users():
    # users_df = pd.read_sql_query("SELECT * FROM users", conn)
    # conn.close()
    # st.table(users_df)
    c.execute('''SELECT PlantTable.id, plants.Name, PlantTable.plant_name, PlantTable.plant_date, PlantTable.add_note 
                  FROM PlantTable INNER JOIN plants ON PlantTable.plant_id = plants.id''')

    data = c.fetchall()
    if data:
        st.write("Список всіх користувачів:")
        df = pd.DataFrame(data, columns=["ID", "Назва рослини", "Ім'я користувача", "Дата призначення", "Термін виконання"])
        st.table(df)
    else:
        st.warning("Користувачів не знайдено.")
# Define a class to represent a plant
class Plant:
    def __init__(self, Name, Location, Note, status):
        self.Name = Name
        self.Location = Location
        self.Note = Note
        self.status=status

# Define a function to add a plant to the database
def add_plant(Name, Location, Note, status):
    plant = Plant(Name, Location, Note, status)
    c.execute("INSERT INTO plants VALUES (NULL, ?, ?, ?, ?)", (plant.Name, plant.Location, plant.Note, plant.status))
    conn.commit()



# Create a function to search for plants
def search_plants(query):
    c.execute("SELECT * FROM plants WHERE Name LIKE ? OR Location LIKE ? OR Note LIKE ?", ('%'+query+'%', '%'+query+'%', '%'+query+'%'))
    plants = c.fetchall()
    conn.close()
    return plants

def delete_plant(Name):
    c.execute('DELETE FROM plants WHERE Name=?', (Name,))
    conn.commit()
    st.success('Рослина видалена')

# Define a function to display the plants in a table
def view_plants():
    c.execute('SELECT * FROM plants')
    plants = c.fetchall()
    if not plants:
        st.write("Рослин не виявлено.")
    else:
        plant_table = [[plant[0], plant[1], plant[2], plant[3], plant[4]] for plant in plants]
        headers = ["ID", "Назва", "Розташування","Примітка","Статус"]
        plant_df = pd.DataFrame(plant_table, columns=headers)
        st.write(plant_df.to_html(escape=False), unsafe_allow_html=True)



# Define a function to retrieve all plants from the database
def get_all_plants():
    c.execute("SELECT * FROM plants")
    plants = c.fetchall()
    return plants

# Define a function to search for plants by Name or Location
def search_plants(search_term):
    c.execute("SELECT * FROM plants WHERE Name LIKE ? OR Location LIKE ?", ('%' + search_term + '%', '%' + search_term + '%'))
    matching_plants = c.fetchall()
    return matching_plants

def view_users_with_plant():
    c.execute('''SELECT PlantTable.id, plants.Name, PlantTable.plant_name, PlantTable.plant_date, PlantTable.add_note 
              FROM PlantTable INNER JOIN plants ON PlantTable.plant_id = plants.id''')
    data = c.fetchall()
    if data:
        st.write("Список всіх користувачів:")
        df = pd.DataFrame(data, columns=["ID", "Назва рослини", "Ім'я користувача", "Дата призначення", "Термін виконання"])
        st.table(df)
    else:
        st.warning("Користувачів не знайдено.")
# Define the Streamlit app
def main():
    st.title("Система управління рослинами")

    menu = ["Додати рослину", "Переглянути рослини", "Пошук рослин",'Видалити рослину','Реєстрація користувача','Перегляд призначень','Призначити рослину']
    choice = st.sidebar.selectbox("Виберіть опцію", menu)

    if choice == "Додати рослину":
        st.subheader("Додати рослину")
        Name = st.text_input("Введіть ім'я рослини")
        Location = st.text_input("Введіть локацію рослини")
        Note = st.text_input("Введіть примітку")
        status="Доступно"
        if st.button("Додати"):
            add_plant(Name, Location, Note, status)
            st.success("Рослину додано!")
    elif choice == "Переглянути рослини":
        st.subheader("Список рослин")
        plants = get_all_plants()
        if not plants:
            st.write("Рослин не виявлено.")
        else:
            plant_table = [[plant[0], plant[1], plant[2], plant[3], plant[4]] for plant in plants]
            headers = ["ID", "Назва", "Розташування","Примітка","Статус"]
            plant_df = pd.DataFrame(plant_table, columns=headers)
            st.write(plant_df.to_html(escape=False), unsafe_allow_html=True)

    elif choice == "Пошук рослин":
        st.subheader("Пошук рослин")
        
        query = st.text_input("Введіть пошуковий запит")
        serach_button=st.button("Пошук")
        if query:
            if serach_button:
                plants = search_plants(query)
                if not plants:
                    st.write("Рослин не знайдено.")
                else:
                    plant_table = [[plant[0], plant[1], plant[2], plant[3], plant[4]] for plant in plants]
                    headers = ["ID", "Назва", "Розташування","Примітка","Статус"]
                    plant_df = pd.DataFrame(plant_table, columns=headers)
                    st.write(plant_df.to_html(escape=False), unsafe_allow_html=True)

    elif choice == 'Видалити рослину':
        st.header("Видалити рослину")
        Name = st.text_input("Введіть назву росилни для видалення:")
        delete_button = st.button("Видалити")
        st.subheader("Список рослин")
        view_plants()

        if Name:
            if delete_button:
                delete_plant(Name)
                st.success(f"{Name} було вилучено з бібліотеки.")
            else:
                st.warning(f"{Name} не знайдено в бібліотеці.")        
    elif choice == "Реєстрація користувача":
        users_registration()
    elif choice == "Перегляд призначень":
        view_users_with_plant()
        # view_users()
    elif choice == "Призначити рослину":
        issue_plant_form()
    
if __name__ == "__main__":
    main()
