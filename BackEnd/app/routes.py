from flask import Blueprint, request, jsonify

from pymongo import MongoClient

# Configuration MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mediaDB']
documents = db.documents
# Créer un Blueprint pour les routes
abonne_bp = Blueprint('abonne', __name__)
document_bp = Blueprint('documents', __name__)
@abonne_bp.route('/AddAbonnee', methods=['POST'])
def create_abonne():
    data = {
        "nom": request.form.get("nom"),
        "prenom": request.form.get("prenom"),
        "email": request.form.get("email"),
        "adresse": request.form.get("adresse"),
        "liste_emprunt_cours": request.form.get("liste_emprunt_cours"),
        "historique_emprunt": request.form.get("historique_emprunt"),
        "date_inscription": request.form.get("date_inscription")
    }

    # Validation des données
    if not data["email"]:
        return jsonify({"error": "L'email est requis."}), 400
    # Vérifier si l'email existe déjà
    existing_abonne = db.abonne.find_one({"email": data["email"]})
    if existing_abonne:
        return jsonify({"error": "Un abonné avec cet email existe déjà."}), 409
   
  
    # Insérer le nouvel abonné si non existant
    db.abonne.insert_one(data)
    return redirect(url_for('Abonnees'))  # Rediriger vers la page des abonnés après l'ajout


@abonne_bp.route('/abonne', methods=['GET'])
def get_abonnes():
    abonnes = list(db.abonne.find({}, {"_id": 0}))
    return jsonify(abonnes), 200

@abonne_bp.route('/abonne/<email>', methods=['PUT'])
def update_abonne(email):
    # Récupérer les données JSON envoyées dans la requête
    data = request.json

    if not data:
        return jsonify({"error": "Aucune donnée fournie pour la mise à jour"}), 400

    # Validation des données : suppression des clés vides
    valid_data = {key: value for key, value in data.items() if value is not None and value != ""}

    if not valid_data:
        return jsonify({"error": "Aucun champ valide fourni pour la mise à jour"}), 400

    # Mise à jour des champs dans MongoDB
    result = db.abonne.update_one({"email": email}, {"$set": valid_data})

    # Vérifiez si un document a été trouvé et mis à jour
    if result.matched_count == 0:
        return jsonify({"error": f"Aucun abonné trouvé avec l'email '{email}'"}), 404

    if result.modified_count == 0:
        return jsonify({"message": "Aucun changement détecté dans les données"}), 200

    return jsonify({"message": "Abonné mis à jour avec succès !"}), 200


@abonne_bp.route('/abonne/<email>', methods=['DELETE'])
def delete_abonne(email):
    db.abonne.delete_one({"email": email})
    return jsonify({"message": "Abonné supprimé avec succès !"}), 200

@abonne_bp.route('/abonne/delete', methods=['DELETE'])
def delete_all():
    try:
        # Suppression de tous les abonnés dans la collection
        result = db.abonne.delete_many({})

        # Vérifier si des abonnés ont été supprimés
        if result.deleted_count > 0:
            return jsonify({"message": f"{result.deleted_count} abonnés supprimés avec succès !"}), 200
        else:
            return jsonify({"message": "Aucun abonné trouvé à supprimer."}), 404

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression des abonnés: {str(e)}"}), 500



@document_bp.route('/delete_document/<titre>', methods=['POST'])
def delete_document(titre):
     # Tenter de supprimer 
    result = db.abonne.delete_one({"titre": titre})
    
    # Vérifier si existait
    if result.deleted_count == 0:
        return "Aucun document trouvé avec ce titre.", 404

    # Rediriger vers la liste des abonnés après suppression
    return redirect(url_for('catalogues'))

@document_bp.route('/document/delete', methods=['DELETE'])
def delete_all_documents():
    try:
        # Suppression de tous les documents dans la collection
        result = documents.delete_many({})

        # Vérifier si des documents ont été supprimés
        if result.deleted_count > 0:
            return jsonify({"message": f"{result.deleted_count} documents supprimés avec succès !"}), 200
        else:
            return jsonify({"message": "Aucun document trouvé à supprimer."}), 404

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression des documents: {str(e)}"}), 500
