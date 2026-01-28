from flask import Flask, redirect, url_for, render_template, jsonify, request, session, make_response, flash
from werkzeug.utils import secure_filename
import mysql.connector
import os
from datetime import datetime
import locale
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = "events"

# Définition du dossier de sauvegarde des fichiers uploadés
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


con = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='rivent'
)

@app.route("/Data")
def database():
    cursor = con.cursor()
    cursor.execute('SELECT * FROM inscription')
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

#connexion 
@app.route("/", methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT * FROM inscription WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        
        cursor.execute('SELECT * FROM organisateur WHERE email = %s AND password = %s', (email, password,))
        org_user = cursor.fetchone()
        
        cursor.execute('SELECT * FROM events ORDER BY date_heure DESC')
        items = cursor.fetchall()
        
        if user:
            session['loggedin'] = True
            session['id'] = int(user['id'])
            session['name'] = user['name']
            session['surname'] = user['surname']
            session['email'] = user['email']
            session['role'] = 'utilisateur'  
            flash('Vous êtes connectés !')           
            return render_template('index.html', message=message, items=items)
            
        elif org_user:
            session['loggedin'] = True
            session['id'] = int(org_user['id'])
            session['name'] = org_user['name']
            session['surname'] = org_user['surname']
            session['email'] = org_user['email']
            session['role'] = org_user['role']  
            flash('Vous êtes connectés en tant qu\'organisateur')
            return render_template('index.html', message=message, items=items)
        
        cursor.close()
        
    return render_template("login.html", message=message)

#deconnexion
@app.route('/deconnexion')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    session.pop('surname', None)
    session.pop('email', None)
    session.pop('role', None)  
    return redirect(url_for('login'))

#inscription
@app.route("/inscription", methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'surname' in request.form and 'email' in request.form and 'password' in request.form and 'confirm_password' in request.form:
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        confirm_password = request.form['confirm_password']
        password = request.form['password']
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT * FROM inscription WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Le compte existe déjà !'
        elif not email or not password:
            message = 'Veuillez remplir le formulaire !'
        elif password != confirm_password:
            message = 'Les mots de passe ne correspondent pas !'
            
        else:
            cursor.execute('INSERT INTO inscription VALUES (NULL, %s, %s, %s, %s)', (name, surname, email, password))
            con.commit()
            message = 'Compte enregistré avec succès'
            
            cursor.execute('SELECT * FROM inscription WHERE email = %s', (email,))
            newUser = cursor.fetchone()
            cursor.close()
            
            session['loggedin'] = True
            session['id'] = newUser['id']
            session['name'] = newUser['name']
            session['surname'] = newUser['surname']
            session['email'] = newUser['email']
            session['role'] = 'utilisateur' 
            return render_template('index.html', message=message)
            
    elif request.method == 'POST':
        message = 'Veuillez remplir le formulaire !'
    return render_template("signup.html", message=message)

#inscription organisateur
@app.route("/organisateur", methods=['GET', 'POST'])
def organisateur():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'surname' in request.form and 'email' in request.form and 'password' in request.form and 'confirm_password' in request.form:
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        tel = request.form['tel']
        
        organizer = 'organisateur' if 'organizer' in request.form else None
        
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT * FROM organisateur WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        if account:
            message = 'Le compte existe déjà !'
        elif not email or not password:
            message = 'Veuillez remplir le formulaire !'
        elif password != confirm_password:
            message = 'Les mots de passe ne correspondent pas !'
        else:
            cursor.execute('INSERT INTO organisateur (id, name, surname, email, password, tel, role) VALUES (NULL, %s, %s, %s, %s, %s, %s)', 
                         (name, surname, email, password, tel, organizer))
            con.commit()
            
            cursor.execute('SELECT * FROM organisateur WHERE email = %s', (email,))
            newUser = cursor.fetchone()
            cursor.close()
            
            session['loggedin'] = True
            session['id'] = newUser['id']
            session['name'] = newUser['name']
            session['surname'] = newUser['surname']
            session['email'] = newUser['email']
            session['role'] = newUser['role']  
    
            return redirect(url_for('home'))
    
    return render_template("organisateur.html", message=message)

#accueil
@app.route("/accueil")
def home():
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    cursor = con.cursor(dictionary=True)
    cursor.execute('SELECT * FROM events ORDER BY date_heure DESC')
    items = cursor.fetchall()
    cursor.close()
    
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", name=session['name'], items=items)

#code qr ticket
@app.route('/ticket')
def ticket():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    user_id = session['id']

    cursor = con.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM reservation WHERE user_id = %s ORDER BY reservation_date DESC LIMIT 1",
            (user_id,)
        )
        reservation = cursor.fetchone()
    finally:
        cursor.close()

    if not reservation:
        flash("Aucune réservation trouvée.")
        return render_template('profile.html', qr_code=None)

    # Utiliser le nom d'utilisateur de la session au lieu de reservation['user_id']
    utilisateur = session.get('name', 'Utilisateur')
  
    qr_data = (
        f"--- Ticket de Réservation ---\n"
        f"Réservation n°: {reservation['id']}\n"
        f"Événement: {reservation['event_title']}\n"
        f"Nom: {utilisateur}\n"
        f"Type de billet: {reservation['ticket_type']}\n"
        f"Quantité: {reservation['quantity']}\n"
        f"Place: {reservation['place_number']}\n"
        f"Date: {reservation['reservation_date']}\n"
        f"Prix total: {reservation['total_price']} Ariary\n"
        f"----------------------------"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code_b64 = base64.b64encode(buffered.getvalue()).decode()

    return render_template('profile.html', qr_code=qr_code_b64)


#liste des evenements
@app.route("/evenements")
def events():
    search_query = request.args.get('q', '').strip() 
    
    cursor = con.cursor(dictionary=True)
    
    if search_query:
        cursor.execute('SELECT * FROM events WHERE titre LIKE %s', ('%' + search_query + '%',))
    else:
        cursor.execute('SELECT * FROM events')
    
    items = cursor.fetchall()
    cursor.close()  
    
    # Convertir les champs date_heure en objets datetime si nécessaire
    for item in items:
        date_val = item.get('date_heure')
        if date_val and not isinstance(date_val, datetime):
            try:
                item['date_heure'] = datetime.strptime(str(date_val), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                item['date_heure'] = None

        # Ajout de l'affichage en français avec correction de l'encodage
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        except locale.Error:
            pass  # Ignore si la locale n'est pas disponible

        if item.get('date_heure'):
            try:
                item['date_heure_affiche'] = item['date_heure'].strftime('%a. %d %B %Y %H:%M')
            except Exception:
                item['date_heure_affiche'] = str(item['date_heure'])
        else:
            item['date_heure_affiche'] = 'Date non définie'

    no_results_message = "Aucun événement trouvé pour votre recherche." if not items else None
    
    return render_template("evenements.html", items=items, no_results_message=no_results_message)

#ajout de l'affiche
@app.route("/ajout", methods=['GET', 'POST'])
def ajout():
    if request.method == 'POST':
        titre = request.form.get('titre')
        type_event = request.form.get('type_event')
        lieu = request.form.get('lieu')
        date_heure = request.form.get('date_heure')
        organisateur_id = request.form.get('organisateur')  # This should be the ID from the form
        description = request.form.get('description')
        prix_simple = request.form.get('prix_simple')
        prix_silver = request.form.get('prix_silver')
        prix_gold = request.form.get('prix_gold')
        prix_vip = request.form.get('prix_VIP')
        entree = request.form.get('entree')
        plat_resistance = request.form.get('plat_resistance')
        dessert = request.form.get('dessert')
     
        affiche_file = request.files.get('affiche')

        if not all([titre, type_event, lieu, date_heure, organisateur_id, description, prix_simple, prix_silver, prix_gold, prix_vip, entree, plat_resistance, dessert, affiche_file]):
            flash('Veuillez remplir tous les champs obligatoires.')
            return redirect(url_for('ajout'))

        if not affiche_file or affiche_file.filename == '':
            flash('Veuillez fournir une affiche pour l\'évènement.')
            return redirect(url_for('ajout'))
        else:
            affiche_filename = secure_filename(affiche_file.filename)
            affiche_file.save(os.path.join(UPLOAD_FOLDER, affiche_filename))

        # if not plan_site_file or plan_site_file.filename == '':
        #     flash('Veuillez fournir un plan du site pour l\'évènement.')
        #     return redirect(url_for('ajout'))
        # else:
        #     plan_site_filename = secure_filename(plan_site_file.filename)
        #     plan_site_file.save(os.path.join(UPLOAD_FOLDER, plan_site_filename))

        # Get the organizer's name from the organisateur table using the ID
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT name FROM organisateur WHERE id = %s', (organisateur_id,))
        org_row = cursor.fetchone()
        if not org_row:
            cursor.close()
            flash("Organisateur introuvable.")
            return redirect(url_for('ajout'))
        organisateur_name = org_row['name']

        # Now insert the event with the organizer's name
        cursor = con.cursor()
        cursor.execute(
            '''
            INSERT INTO events (titre, type_event, lieu, date_heure, organisateur, description, prix_simple, prix_silver, prix_gold, prix_vip, entree, plat_resistance, dessert, affiche) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (titre, type_event, lieu, date_heure, organisateur_name, description, prix_simple, prix_silver, prix_gold, prix_vip, entree, plat_resistance, dessert, affiche_filename)
        )
        con.commit()
        cursor.close()

        flash('Evénement ajouté avec succès')
        return redirect(url_for('ajout'))

    # For GET: fetch all organizers to populate the select field
    cursor = con.cursor(dictionary=True)
    cursor.execute('SELECT id, name FROM organisateur')
    organisateurs = cursor.fetchall()
    cursor.close()
    return render_template("add.html", organisateurs=organisateurs)

#contact
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    message = ''
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        cursor = con.cursor()
        cursor.execute(
            'INSERT INTO contact VALUES (NULL, %s, %s, %s, %s)',
            (
                full_name,
                email,
                subject,
                message
            )
        )
        con.commit()
        cursor.close()

        flash('Message envoyé avec succès.')        
        return redirect(url_for('contact'))
    return render_template("contact.html", message=message)

#apropos
@app.route("/apropos")
def about():
    return render_template("about.html")

# @app.route("/details/<int:item_id>", methods=['GET', 'POST'])
# def details(item_id):
#     cursor = con.cursor(dictionary=True)
#     try:
#         cursor.execute('SELECT * FROM events WHERE id = %s', (item_id,))
#         item = cursor.fetchone()
#     finally:
#         cursor.close()

#     if item is None:
#         return "Il n'y a pas d'\u00e9l\u00e9ments", 404

#     try:
#         locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
#     except locale.Error:
#         flash("La configuration de la langue a \u00e9chou\u00e9. Utilisation de la langue par d\u00e9faut.")

#     if item['date_heure']:
#         try:
#             if isinstance(item['date_heure'], str):
#                 item['date_heure'] = datetime.strptime(item['date_heure'], "%Y-%m-%d %H:%M:%S")
#             item['date_heure_affiche'] = item['date_heure'].strftime('%a. %d %B %Y %H : %M')
#         except ValueError:
#             item['date_heure_affiche'] = 'Date invalide'
#     else:
#         item['date_event_affiche'] = 'Date non d\u00e9finie'

#     if request.method == 'POST':
#         if not session.get('loggedin'):
#             return redirect(url_for('login'))

#         user_id = session['id']
#         ticket_type = request.form.get('ticket_type')
#         quantity = request.form.get('quantity', 1)
#         total_price = request.form.get('total_price')

#         try:
#             quantity = int(quantity)
#             total_price = float(total_price)
#         except (ValueError, TypeError):
#             flash("Veuillez entrer des valeurs valides pour la quantit\u00e9 et le prix.")
#             return redirect(url_for('details', item_id=item_id))

#         if ticket_type not in ['SIMPLE', 'SILVER', 'GOLD', 'VIP']:
#             flash("Type de billet invalide.")
#             return redirect(url_for('details', item_id=item_id))

#         if quantity <= 0 or total_price <= 0:
#             flash("La quantit\u00e9 et le prix doivent \u00eatre sup\u00e9rieurs \u00e0 z\u00e9ro.")
#             return redirect(url_for('details', item_id=item_id))

#         cursor = con.cursor()
#         try:
#             reservation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#             cursor.execute(
#                 '''INSERT INTO reservation (event_id, user_id, ticket_type, quantity, total_price, reservation_date, event_title) 
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)''',
#                 (item_id, user_id, ticket_type, quantity, total_price, reservation_date, item['titre'])
#             )
            
#             con.commit()
#             flash("R\u00e9servation effectu\u00e9e avec succ\u00e8s !")
#         except mysql.connector.Error as err:
#             flash(f"Erreur lors de la r\u00e9servation : {err}")
#             con.rollback()
#         finally:
#             cursor.close()

#         return redirect(url_for('details', item_id=item_id))

#     return render_template("eventdetail.html", item=item)

#details de l'evenement
@app.route("/details/<int:item_id>", methods=['GET', 'POST'])
def details(item_id):
    cursor = con.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM events WHERE id = %s', (item_id,))
        item = cursor.fetchone()
    finally:
        cursor.close()

    if item is None:
        return "Il n'y a pas d'éléments", 404

   
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        flash("La configuration de la langue a échoué. Utilisation de la langue par défaut.")

    if item['date_heure']:
        try:
            if isinstance(item['date_heure'], str):
                item['date_heure'] = datetime.strptime(item['date_heure'], "%Y-%m-%d %H:%M:%S")
            item['date_heure_affiche'] = item['date_heure'].strftime('%a. %d %B %Y %H : %M')
        except ValueError:
            item['date_heure_affiche'] = 'Date invalide'
    else:
        item['date_heure_affiche'] = 'Date non définie'

    if request.method == 'POST':
        if not session.get('loggedin'):
            return redirect(url_for('login'))

        user_id = session['id']
        ticket_type = request.form.get('ticket_type')
        quantity = request.form.get('quantity', 1)
        total_price = request.form.get('total_price')
        place_number = request.form.get('place_number')

        try:
            quantity = int(quantity)
            total_price = float(total_price)
        except (ValueError, TypeError):
            flash("Veuillez entrer des valeurs valides pour la quantité et le prix.")
            return redirect(url_for('details', item_id=item_id))

        if ticket_type not in ['SIMPLE', 'SILVER', 'GOLD', 'VIP']:
            flash("Type de billet invalide.")
            return redirect(url_for('details', item_id=item_id))

        if quantity <= 0 or total_price <= 0:
            flash("La quantité et le prix doivent être supérieurs à zéro.")
            return redirect(url_for('details', item_id=item_id))

        cursor = con.cursor()
        try:
            reservation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(
                '''INSERT INTO reservation (event_id, user_id, ticket_type, quantity, total_price, reservation_date, event_title,place_number) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                (item_id, user_id, ticket_type, quantity, total_price, reservation_date, item['titre'], place_number)
            )
            con.commit()

            reservation_id = cursor.lastrowid

            qr_data = f"Réservation #{reservation_id} | Événement: {item['titre']} | Nom: {user_id} | Type: {ticket_type} | Quantité: {quantity} [Place: {place_number} | Date: {reservation_date}"

            session['qr_data'] = qr_data

            flash("Réservation effectuée avec succès ! Voici votre ticket.")

        except Exception as err:
            flash(f"Erreur lors de la réservation : {err}")
            con.rollback()
        finally:
            cursor.close()

        return redirect(url_for('ticket'))

    return render_template("eventdetail.html", item=item)



#***********************************************************Start of admin's code***********************************************************
#connexion de l'admin
@app.route('/admin', methods=['GET', 'POST'])
def adminlogin():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, password,))
            user = cursor.fetchone()
            
            if user:
                session['loggedin'] = True
                session['id'] = int(user['id'])
                session['email'] = user['email']
                session['role'] = 'admin'  
                flash('Vous êtes connecté en tant qu\'administrateur !')           
                return redirect(url_for('admin'))
            else:
                message = "Identifiants administrateur invalides."
        finally:
            cursor.close()
        
    return render_template("adminlogin.html", message=message)

#liste des utilisateurs admin           
@app.route("/admin/liste_utilisateur")
def admin():
    if not session.get('loggedin') or session.get('role') != 'admin':
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for('adminlogin'))
    
    users = []
    cursor = None
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT id, name, surname FROM inscription')
        users = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")
    finally:
        if cursor is not None:
            cursor.close()

    return render_template("admin.html", users=users, selected_user=None)

#details de l'utilisateur
@app.route("/admin/user/<int:user_id>")
def admin_user_details(user_id):
    users = []
    selected_user = None
    
    try:
        # Get selected user details
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id, name, surname, email FROM inscription WHERE id = %s', (user_id,))
            selected_user = cursor.fetchone()
        finally:
            cursor.close()

        # Get all users for the sidebar
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id, name, surname FROM inscription')
            users = cursor.fetchall()
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")
        
    return render_template("admin.html", users=users, selected_user=selected_user)

#supprimer l'utilisateur
@app.route("/admin/user/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id):
    try:
        cursor = con.cursor()
        try:
            cursor.execute('DELETE FROM inscription WHERE id = %s', (user_id,))
            con.commit()
            flash('Suppression terminée avec succès.')
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        con.rollback()
        flash(f"Erreur lors de la suppression: {err}")
        
    return redirect(url_for('admin'))

#modifocation de l'utilisateur
@app.route("/admin/user/<int:user_id>/modify", methods=['GET', 'POST'])
def admin_modify_user(user_id):
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')

        try:
            cursor = con.cursor()
            try:
                cursor.execute(
                    'UPDATE inscription SET name = %s, surname = %s, email = %s WHERE id = %s',
                    (name, surname, email, user_id)
                )
                con.commit()
                flash('Modification terminée avec succès.')
            finally:
                cursor.close()
        except mysql.connector.Error as err:
            con.rollback()
            flash(f"Erreur lors de la modification: {err}")
            
        return redirect(url_for('admin'))

    selected_user = None
    try:
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id, name, surname, email FROM inscription WHERE id = %s', (user_id,))
            selected_user = cursor.fetchone()
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")

    return render_template("admin_modify_user.html", user=selected_user)

# -------------------admin ----------------organisateur--------------------------
#liste des organisateurs
@app.route("/admin/organisateur")
def admin_org():
    users = []
    try:
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id, name, surname, tel FROM organisateur')
            users = cursor.fetchall()
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")
        
    return render_template("admin2.html", users=users, selected_user=None)

#details de l'organisateur
@app.route("/admin/organisateur/<int:org_id>")
def admin_org_details(org_id):
    cursor = con.cursor(dictionary=True)
    cursor.execute('SELECT id, name, surname, email, tel FROM organisateur WHERE id = %s', (org_id,))
    selected_user = cursor.fetchone()
    cursor.close()

    cursor = con.cursor(dictionary=True)
    cursor.execute('SELECT id, name, surname, tel FROM organisateur')
    users = cursor.fetchall()
    cursor.close()

    return render_template("admin2.html", users=users, selected_user=selected_user)

#suppression de l'organisateur
@app.route("/admin/organisateur/<int:org_id>/delete", methods=['POST'])
def delete_org(org_id):
    try:
        cursor = con.cursor()
        try:
            cursor.execute('DELETE FROM organisateur WHERE id = %s', (org_id,))
            con.commit()
            flash('Suppression terminée avec succès.')
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        con.rollback()
        flash(f"Erreur lors de la suppression: {err}")
        
    return redirect(url_for('admin_org'))


#modification de l'organisateur
@app.route("/admin/organisateur/<int:org_id>/modify", methods=['GET', 'POST'])
def admin_modify_org(org_id):
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        tel = request.form.get('tel')

        try:
            cursor = con.cursor()
            try:
                cursor.execute(
                    'UPDATE organisateur SET name = %s, surname = %s, email = %s, tel = %s WHERE id = %s',
                    (name, surname, email, tel, org_id)
                )
                con.commit()
                flash('Modification terminée avec succès.')
            finally:
                cursor.close()
        except mysql.connector.Error as err:
            con.rollback()
            flash(f"Erreur lors de la modification: {err}")
            
        return redirect(url_for('admin_org'))

    selected_user = None
    try:
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id, name, surname, email, tel FROM organisateur WHERE id = %s', (org_id,))
            selected_user = cursor.fetchone()
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")

    return render_template("admin_modify_org.html", user=selected_user)

# --------fin-----------admin ----------------organisateur--------------------------
#message venant de contact
@app.route('/admin/message')
def message():
    messageCont = []
    try:
        cursor = con.cursor(dictionary=True)
        try:
            cursor.execute('SELECT full_name, email, subject, message FROM contact')
            messageCont = cursor.fetchall()
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")
    
    return render_template("message.html", messageCont=messageCont)

#liste des reservations
@app.route('/admin/reservations')
def admin_reservation():
    reservations = []
    try:
        cursor = con.cursor(dictionary=True)
        try:
            # Join reservation with inscription to get user name and surname
            cursor.execute('''
                SELECT 
                    reservation.*, 
                    inscription.name, 
                    inscription.surname
                FROM reservation
                LEFT JOIN inscription ON reservation.user_id = inscription.id
                ORDER BY reservation.reservation_date DESC
            ''')
            reservations = cursor.fetchall()
        finally:
            cursor.close()
    except mysql.connector.Error as err:
        flash(f"Erreur de base de données: {err}")
    
    return render_template("admin_res.html", reservations=reservations)
#***********************************************************End of admin's code***********************************************************

@app.errorhandler(404)
def not_found(error):
    return render_template('notfound.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
