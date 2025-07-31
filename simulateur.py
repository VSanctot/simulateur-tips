import json
import gspread
from google.oauth2.service_account import Credentials

# Connexion Google Sheets
def connect_google_sheets():
    try:
        creds_dict = dict(st.secrets["GOOGLE_SHEETS_CREDS"])   # Conversion en dict
        creds_json = json.loads(json.dumps(creds_dict))        # JSON valide

        # Créer les credentials Google
        credentials = Credentials.from_service_account_info(creds_json)

        # Connexion à Google Sheets
        gc = gspread.authorize(credentials)

        # ⚠️ Remplace par le NOM EXACT de ton Google Sheet
        sh = gc.open("TIPS_SIMULATEUR")  
        worksheet = sh.sheet1
        return worksheet
    except Exception as e:
        st.error(f"❌ Erreur Google Sheets : {e}")
        return None

# Sauvegarder les données
def save_to_google_sheets(capital, rendement, duree, resultats):
    worksheet = connect_google_sheets()
    if worksheet:
        try:
            worksheet.append_row([
                str(capital),
                str(rendement),
                str(duree),
                str(resultats["Compte titres"][-1]),
                str(resultats["Contrat de capitalisation"][-1])
            ])
            st.success("✅ Données envoyées dans la base TIPS (Google Sheets)")
        except Exception as e:
            st.error(f"❌ Impossible d'enregistrer dans Google Sheets : {e}")
