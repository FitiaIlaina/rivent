Corrige ces codes car aucune information n'est insérée dans la base de donnée

extrait python:

@app.route("/ajout", methods = ['GET', 'POST'])
def ajout():
    message = ''
    if request.method == 'POST':
        titre = request.form.get('titre')
        type_event = request.form.get('type_event')
        lieu = request.form.get('lieu')
        date_heure = request.form.get('date_heure')
        organisateur = request.form.get('organisateur')
        description = request.form.get('description')
        prix_simple = request.form.get('prix_simple')
        prix_silver = request.form.get('prix_silver')
        prix_gold = request.form.get('prix_gold')
        prix_vip = request.form.get('prix_vip')
        entree = request.form.get('entree')
        plat_resistance = request.form.get('plat_resistance')
        dessert = request.form.get('dessert')
        nb_places_max = request.form.get('nb_places_max')
        plan_site = request.form.get('plan_site')
        affiche = request.form.get('affiche')

        if affiche:
            affiche_filename = secure_filename(affiche.filename) # type: ignore
            affiche.save(os.path.join('path/to/save', affiche_filename))
        else:
            
            message = 'Veuillez fournir une affiche pour l\'évènement.'
            return redirect(url_for('ajout'))
        
        cursor = con.cursor()
        
        cursor.execute('INSERT INTO events VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (
            titre, 
            type_event, 
            lieu, 
            date_heure, 
            organisateur, 
            description, 
            prix_simple, 
            prix_silver, 
            prix_gold, 
            prix_vip,
            entree,
            plat_resistance,
            dessert,
            nb_places_max,
            plan_site,
            affiche
        ))

        con.commit()
        cursor.close()

        
        message = 'Evénement ajouté avec succès'


    return render_template("add.html", message = message)


extrait html:

<form method="post" enctype="multipart/form-data">
            
            <h2 class="text-center">                
                
                <strong>Ajout de détails de l'évènements</strong>
            
            </h2>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="titre" placeholder="Titre" autofocus="">
            
            </div>

            <div class="form-group" style="font-size: 13px;">            
                
                <h1 style="font-size: 16px;">Type :</h1>
            
            </div>

            <div class="form-group">
                        
                <select name="type_event" class="form-control">
                    <option value="Spectacles et concerts">Spectacles et concerts</option>
                    <option value="Cabarets">Cabarets</option>
                    <option value="Dînner concert">Dînner concert</option>
                </select>
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="lieu" placeholder="Lieu" autofocus="">
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="date_heure" placeholder="Date et Heure" autofocus="">
            
            </div>

            <div class="form-group" style="font-size: 13px;">            
                
                <h1 style="font-size: 16px;">Organisateur :</h1>
                <output class="form-control" type="text" name="organisateur">
            </div>
            
            <div class="form-group">
                
                <textarea class="form-control" name="description" placeholder="Descriptions...." rows="14" style="height: 143px;"></textarea>
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="number"  min="500" max="999999" oninput="validateNumber(this)" name="prix_simple" placeholder="Prix billet simple en Ariary en Ariary (minimum: 10.000 Ariary)" required>
            
            </div>

            <div class="form-group">
                
                <input class="form-control" type="number"  min="500" max="999999" oninput="validateNumber(this)" name="prix_silver" placeholder="Prix billet silver en Ariary (minimum: 30.000 Ariary)" required>
            
            </div>

            <div class="form-group">
                
                <input class="form-control" type="number"  min="500" max="999999" oninput="validateNumber(this)" name="prix_gold" placeholder="Prix billet gold en Ariary (minimum: 80.000 Ariary)" required>
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="prix_vip" placeholder="Prix billet VIP en Ariary (minimum: 100.000 Ariary)" autofocus="">
            
            </div>
            
            <div class="form-group" style="font-size: 13px;">            
                
                <h1 style="font-size: 16px;">Plats :</h1>
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="entree" placeholder="Entrée" autofocus="">
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="plat_resistance" placeholder="Plat de résistance" autofocus="">
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="text" name="dessert" placeholder="Déssert" autofocus="">
            
            </div>
            
            <div class="form-group" style="font-size: 13px;">
                
                <h1 style="font-size: 16px;">Plan de site : </h1>
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="email" name="nb_places_max" placeholder="Entrer le nombre de place maximum" autofocus="">
                <br>
                <input class="form-control" type="file" name="plan_site" placeholder="Votre fichier" accept="image/*" required>

            </div>
            
            <div class="form-group" style="font-size: 13px;">
                
                <h1 style="font-size: 16px;">Votre affiche : <em>Votre évènement doit comporter un(1) affiche </em></h1>
            
            </div>
            
            <div class="form-group">
                
                <input class="form-control" type="file" name="affiche" placeholder="Votre fichier" accept="image/*" required>
            </div>
            
            <div class="form-group">
                
                <button class="btn btn-primary btn-block" type="submit" style="background: var(--info);">Confirmation de l'ajout</button>
            </div>
            
            <a class="already" href="#">Quitter</a>
        
        </form>