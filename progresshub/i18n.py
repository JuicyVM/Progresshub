"""ProgressHub i18n — small, dependency-free string tables for en/es/fr.

Usage:
    from progresshub import i18n
    i18n.set_lang("es")
    i18n.t("log_in")                     # -> "Iniciar sesión"
    i18n.t("welcome", name="Alex")       # -> "{name}" placeholders replaced
    i18n.choices()                        # -> [("en","English"),("es","Español"),...]

Missing keys fall back to English, then to the key itself, so screens never crash.
"""

_STRINGS = {
    "en": {
        "app_name": "ProgressHub",
        "settings": "Settings",
        "tagline": "gym · trading · calories · sleep · savings",
        "welcome_back": "WELCOME BACK",
        "login_title": "Log in to your hub",
        "signup_title": "Create your account",
        "username": "Username",
        "password": "Password",
        "log_in": "Log in",
        "create_account": "Create account",
        "switch_to_signup": "New here? Create a free account",
        "switch_to_login": "Already have an account? Log in",
        "err_user_short": "Username must be at least 3 characters.",
        "err_pass_short": "Password must be at least 4 characters.",
        "err_taken": "That username is already taken.",
        "err_no_account": "No account with that username. Sign up first.",
        "err_wrong_pass": "Wrong password. Try again.",
        "greeting": "Hey, {name} — what are we tracking today?",
        "coach_ai": "Coach AI",
        "calculator": "Calculator",
        "log_out": "Log out",
        "new_project": "New project",
        "no_projects": "No projects yet.",
        "no_projects_hint": "Create one below and I'll wire it up for that exact goal.",
        "np_title": "NEW PROJECT",
        "np_name": "Project name (e.g. My Lifts)",
        "np_type": "What are we tracking?",
        "np_create": "Create project",
        "np_cant": "Can't create",

        # promo invite
        "promo_head": "You're close to PRO.",
        "promo_line": "Unlimited projects. Deeper analytics. Your best version of 'now'.",
        "promo_cta": "GO PRO",
        "promo_note": "No card needed to peek.",
        "promo_free": "UP TO 5 PROJECTS FOR FREE",

        # dashboard
        "dash_hello": "Hey, {name} — what are we tracking today?",
        "promo_tag": "PRO",

        # tabs (all types share these)
        "tab_overview": "OVERVIEW",
        "tab_history": "HISTORY",
        "tab_chart": "CHART",
        "tab_stats": "STATS",
        "tab_notes": "NOTES",
        "tab_activity": "ACTIVITY",
        "tab_prediction": "PREDICTION",

        # overview-ish labels
        "ov_hero": "Money made so far",
        "ov_trades": "Trades",
        "ov_winrate": "Win rate",
        "ov_avg_win": "Avg win",
        "ov_avg_loss": "Avg loss",
        "ov_best": "Best trade",
        "ov_net": "Net P/L",
        "ov_gross": "Gross P/L",
        "ov_volume": "Volume",
        "ov_cost": "Cost (money put in)",
        "ov_sessions": "Sessions",
        "ov_streak": "Streak",
        "ov_total": "Total",
        "ov_made": "Made",
        "ov_lost": "Lost",
        "ov_current": "Current",
        "ov_clear": "Cleared",
        "ov_on_track": "On track",

        # trading
        "tr_pnl": "P/L",
        "tr_amount": "Amount",
        "tr_currency": "Currency",
        "tr_trade": "Trade",
        "tr_symbol": "Symbol",
        "tr_side": "Side",
        "tr_buy": "Buy",
        "tr_sell": "Sell",
        "tr_cost": "Cost",
        "tr_type": "Type",
        "tr_indicator": "Indicator",
        "tr_signal": "Signal",
        "tr_stock": "Stock",
        "tr_crypto": "Crypto",
        "tr_forex": "Forex",
        "tr_commodity": "Commodity",
        "tr_bond": "Bond",
        "tr_index": "Index",
        "tr_futures": "Futures",
        "tr_option": "Option",
        "tr_money_made": "MONEY MADE",

        # gym
        "gym_weight": "Weight",
        "gym_reps": "Reps",
        "gym_sets": "Sets",
        "gym_exercise": "Exercise",
        "gym_workout": "Workout",
        "gym_sets_reps": "sets·reps",

        # weight loss
        "wl_weight": "Weight",
        "wl_target": "Target",
        "wl_lost": "Lost",
        "wl_bmi": "BMI",

        # calorie
        "cal_cals": "Calories",
        "cal_protein": "Protein (g)",
        "cal_carbs": "Carbs (g)",
        "cal_fat": "Fat (g)",
        "cal_goal": "Daily goal",
        "cal_ate": "Ate",
        "cal_remaining": "Remaining",
        "cal_meals": "Meals",

        # savings
        "sv_goal": "Goal",
        "sv_saved": "Saved",
        "sv_target": "Target",
        "sv_progress": "Progress",

        # habits
        "hb_habit": "Habit",
        "hb_checked": "Done",
        "hb_streak": "Streak",

        # sleep
        "sl_start": "Start",
        "sl_end": "End",
        "sl_hours": "Hours",
        "sl_quality": "Quality",
        "sl_goal": "Goal", 

        # study
        "st_subject": "Subject",
        "st_hours": "Hours",
        "st_material": "Material",
        "st_method": "Method",
        "st_notes": "Notes",

        # cardio
        "cd_distance": "Distance",
        "cd_time": "Time",
        "cd_pace": "Pace",
        "cd_calories": "Calories",
        "cd_splits": "Splits",
        "cd_elevation": "Elevation",

        # reading
        "rd_pages": "Pages",
        "rd_pages_read": "Pages read",
        "rd_book": "Book",
        "rd_author": "Author",
        "rd_rating": "Rating",
        "rd_mood": "Mood",

        # coach
        "coach_title": "AI Coach",
        "coach_hint": "How's it going? Ask about your projects…",
        "coach_send": "Send",
        "coach_thinking": "Thinking…",
        "coach_trade_reco": "Here's a quick take on your trading:",
        "coach_gym_reco": "Here's a read on your workouts:",

        # settings
        "set_theme": "Theme",
        "set_lang": "Language",
        "set_accent": "Accent color",
        "set_fullscreen": "Start fullscreen",
        "set_saved": "Saved ✓",
        "set_done": "Done",
        "set_system": "Follow system",
    },
    "es": {
        "app_name": "ProgressHub",
        "settings": "Ajustes",
        "tagline": "gym · trading · calorías · sueño · ahorros",
        "welcome_back": "TE DAMOS LA BIENVENIDA",
        "login_title": "Inicia sesión en tu hub",
        "signup_title": "Crea tu cuenta",
        "username": "Usuario",
        "password": "Contraseña",
        "log_in": "Iniciar sesión",
        "create_account": "Crear cuenta",
        "switch_to_signup": "¿Eres nuevo? Crea una cuenta gratis",
        "switch_to_login": "¿Ya tienes cuenta? Inicia sesión",
        "err_user_short": "El usuario debe tener al menos 3 caracteres.",
        "err_pass_short": "La contraseña debe tener al menos 4 caracteres.",
        "err_taken": "Ese usuario ya existe.",
        "err_no_account": "No existe una cuenta con ese usuario. Regístrate primero.",
        "err_wrong_pass": "Contraseña incorrecta. Inténtalo de nuevo.",
        "greeting": "Hola {name} — ¿qué vamos a registrar hoy?",
        "coach_ai": "Coach IA",
        "calculator": "Calculadora",
        "log_out": "Cerrar sesión",
        "new_project": "Nuevo proyecto",
        "no_projects": "Aún no hay proyectos.",
        "no_projects_hint": "Crea uno abajo y lo configuro para ese objetivo.",
        "np_title": "NUEVO PROYECTO",
        "np_name": "Nombre del proyecto (p. ej. Mis Lifts)",
        "np_type": "¿Qué vas a registrar?",
        "np_create": "Crear proyecto",
        "np_cant": "No se puede crear",

        "promo_head": "Estás cerca de PRO.",
        "promo_line": "Proyectos ilimitados. Estadísticas más profundas. Tu mejor versión de 'ahora'.",
        "promo_cta": "HAZTE PRO",
        "promo_note": "Sin tarjeta para echar un vistazo.",
        "promo_free": "HASTA 5 PROYECTOS GRATIS",

        "dash_hello": "Hola {name} — ¿qué vamos a registrar hoy?",
        "promo_tag": "PRO",

        "tab_overview": "RESUMEN",
        "tab_history": "HISTORIAL",
        "tab_chart": "GRÁFICO",
        "tab_stats": "ESTADÍSTICAS",
        "tab_notes": "NOTAS",
        "tab_activity": "ACTIVIDAD",
        "tab_prediction": "PREDICCIÓN",

        "ov_hero": "Dinero ganado hasta ahora",
        "ov_trades": "Operaciones",
        "ov_winrate": "Tasa de acierto",
        "ov_avg_win": "Ganancia media",
        "ov_avg_loss": "Pérdida media",
        "ov_best": "Mejor operación",
        "ov_net": "P/L neto",
        "ov_gross": "P/L bruto",
        "ov_volume": "Volumen",
        "ov_cost": "Costo (dinero invertido)",
        "ov_sessions": "Sesiones",
        "ov_streak": "Racha",
        "ov_total": "Total",
        "ov_made": "Hecho",
        "ov_lost": "Perdido",
        "ov_current": "Actual",
        "ov_clear": "Superado",
        "ov_on_track": "En camino",

        "tr_pnl": "P/L",
        "tr_amount": "Importe",
        "tr_currency": "Moneda",
        "tr_trade": "Operación",
        "tr_symbol": "Símbolo",
        "tr_side": "Lado",
        "tr_buy": "Comprar",
        "tr_sell": "Vender",
        "tr_cost": "Coste",
        "tr_type": "Tipo",
        "tr_indicator": "Indicador",
        "tr_signal": "Señal",
        "tr_stock": "Acción",
        "tr_crypto": "Cripto",
        "tr_forex": "Forex",
        "tr_commodity": "Materia prima",
        "tr_bond": "Bono",
        "tr_index": "Índice",
        "tr_futures": "Futuros",
        "tr_option": "Opción",
        "tr_money_made": "DINERO GANADO",

        "gym_weight": "Peso",
        "gym_reps": "Reps",
        "gym_sets": "Series",
        "gym_exercise": "Ejercicio",
        "gym_workout": "Entrenamiento",
        "gym_sets_reps": "series·reps",

        "wl_weight": "Peso",
        "wl_target": "Objetivo",
        "wl_lost": "Perdido",
        "wl_bmi": "IMC",

        "cal_cals": "Calorías",
        "cal_protein": "Proteína (g)",
        "cal_carbs": "Carbs (g)",
        "cal_fat": "Grasa (g)",
        "cal_goal": "Meta diaria",
        "cal_ate": "Comido",
        "cal_remaining": "Restante",
        "cal_meals": "Comidas",

        "sv_goal": "Meta",
        "sv_saved": "Ahorrado",
        "sv_target": "Objetivo",
        "sv_progress": "Progreso",

        "hb_habit": "Hábito",
        "hb_checked": "Hecho",
        "hb_streak": "Racha",

        "sl_start": "Inicio",
        "sl_end": "Fin",
        "sl_hours": "Horas",
        "sl_quality": "Calidad",
        "sl_goal": "Meta",

        "st_subject": "Materia",
        "st_hours": "Horas",
        "st_material": "Material",
        "st_method": "Método",
        "st_notes": "Notas",

        "cd_distance": "Distancia",
        "cd_time": "Tiempo",
        "cd_pace": "Ritmo",
        "cd_calories": "Calorías",
        "cd_splits": "Parciales",
        "cd_elevation": "Elevación",

        "rd_pages": "Páginas",
        "rd_pages_read": "Páginas leídas",
        "rd_book": "Libro",
        "rd_author": "Autor",
        "rd_rating": "Puntuación",
        "rd_mood": "Estado",

        "coach_title": "Coach IA",
        "coach_hint": "¿Cómo va? Pregunta sobre tus proyectos…",
        "coach_send": "Enviar",
        "coach_thinking": "Pensando…",
        "coach_trade_reco": "Un rápido análisis de tu trading:",
        "coach_gym_reco": "Un vistazo a tus entrenamientos:",

        "set_theme": "Tema",
        "set_lang": "Idioma",
        "set_accent": "Color de acento",
        "set_fullscreen": "Iniciar a pantalla completa",
        "set_saved": "Guardado ✓",
        "set_done": "Listo",
        "set_system": "Seguir sistema",
    },
    "fr": {
        "app_name": "ProgressHub",
        "settings": "Paramètres",
        "tagline": "salle · trading · calories · sommeil · épargne",
        "welcome_back": "CONTENU DE TE REVOIR",
        "login_title": "Connecte-toi à ton hub",
        "signup_title": "Crée ton compte",
        "username": "Nom d'utilisateur",
        "password": "Mot de passe",
        "log_in": "Se connecter",
        "create_account": "Créer un compte",
        "switch_to_signup": "Nouveau ? Crée un compte gratuit",
        "switch_to_login": "Déjà un compte ? Connecte-toi",
        "err_user_short": "Le nom d'utilisateur doit faire au moins 3 caractères.",
        "err_pass_short": "Le mot de passe doit faire au moins 4 caractères.",
        "err_taken": "Ce nom d'utilisateur est déjà pris.",
        "err_no_account": "Aucun compte avec ce nom. Inscris-toi d'abord.",
        "err_wrong_pass": "Mot de passe incorrect. Réessaie.",
        "greeting": "Salut {name} — qu'allons-nous suivre aujourd'hui ?",
        "coach_ai": "Coach IA",
        "calculator": "Calculatrice",
        "log_out": "Se déconnecter",
        "new_project": "Nouveau projet",
        "no_projects": "Aucun projet pour l'instant.",
        "no_projects_hint": "Crée-en un ci-dessous et je l'adapte à ton objectif.",
        "np_title": "NOUVEAU PROJET",
        "np_name": "Nom du projet (ex. Mes Lifts)",
        "np_type": "Qu'allons-nous suivre ?",
        "np_create": "Créer le projet",
        "np_cant": "Impossible de créer",

        "promo_head": "Vous êtes proche de PRO.",
        "promo_line": "Projets illimités. Analytics plus profondes. Votre meilleur « maintenant ».",
        "promo_cta": "PASSEZ PRO",
        "promo_note": "Pas de carte pour jeter un œil.",
        "promo_free": "JUSQU'À 5 PROJETS GRATUITS",

        "dash_hello": "Salut {name} — qu'allons-nous suivre aujourd'hui ?",
        "promo_tag": "PRO",

        "tab_overview": "APERÇU",
        "tab_history": "HISTORIQUE",
        "tab_chart": "GRAPHIQUE",
        "tab_stats": "STATISTIQUES",
        "tab_notes": "NOTES",
        "tab_activity": "ACTIVITÉ",
        "tab_prediction": "PRÉDICTION",

        "ov_hero": "Argent gagné jusqu'à présent",
        "ov_trades": "Opérations",
        "ov_winrate": "Taux de réussite",
        "ov_avg_win": "Gain moyen",
        "ov_avg_loss": "Perte moyenne",
        "ov_best": "Meilleure opération",
        "ov_net": "P/L net",
        "ov_gross": "P/L brut",
        "ov_volume": "Volume",
        "ov_cost": "Coût (argent investi)",
        "ov_sessions": "Séances",
        "ov_streak": "Série",
        "ov_total": "Total",
        "ov_made": "Gagné",
        "ov_lost": "Perdu",
        "ov_current": "Actuel",
        "ov_clear": "Atteint",
        "ov_on_track": "En bonne voie",

        "tr_pnl": "P/L",
        "tr_amount": "Montant",
        "tr_currency": "Devise",
        "tr_trade": "Opération",
        "tr_symbol": "Symbole",
        "tr_side": "Sens",
        "tr_buy": "Acheter",
        "tr_sell": "Vendre",
        "tr_cost": "Coût",
        "tr_type": "Type",
        "tr_indicator": "Indicateur",
        "tr_signal": "Signal",
        "tr_stock": "Action",
        "tr_crypto": "Crypto",
        "tr_forex": "Forex",
        "tr_commodity": "Matière première",
        "tr_bond": "Obligation",
        "tr_index": "Indice",
        "tr_futures": "Futures",
        "tr_option": "Option",
        "tr_money_made": "ARGENT GAGNÉ",

        "gym_weight": "Poids",
        "gym_reps": "Rép",
        "gym_sets": "Séries",
        "gym_exercise": "Exercice",
        "gym_workout": "Entraînement",
        "gym_sets_reps": "séries·rép",

        "wl_weight": "Poids",
        "wl_target": "Objectif",
        "wl_lost": "Perdu",
        "wl_bmi": "IMC",

        "cal_cals": "Calories",
        "cal_protein": "Protéines (g)",
        "cal_carbs": "Glucides (g)",
        "cal_fat": "Graisses (g)",
        "cal_goal": "Objectif quotidien",
        "cal_ate": "Mangé",
        "cal_remaining": "Restant",
        "cal_meals": "Repas",

        "sv_goal": "Objectif",
        "sv_saved": "Épargné",
        "sv_target": "Cible",
        "sv_progress": "Progrès",

        "hb_habit": "Habitude",
        "hb_checked": "Fait",
        "hb_streak": "Série",

        "sl_start": "Début",
        "sl_end": "Fin",
        "sl_hours": "Heures",
        "sl_quality": "Qualité",
        "sl_goal": "Objectif",

        "st_subject": "Matière",
        "st_hours": "Heures",
        "st_material": "Matériel",
        "st_method": "Méthode",
        "st_notes": "Notes",

        "cd_distance": "Distance",
        "cd_time": "Temps",
        "cd_pace": "Allure",
        "cd_calories": "Calories",
        "cd_splits": "Fractionnés",
        "cd_elevation": "Dénivelé",

        "rd_pages": "Pages",
        "rd_pages_read": "Pages lues",
        "rd_book": "Livre",
        "rd_author": "Auteur",
        "rd_rating": "Note",
        "rd_mood": "Humeur",

        "coach_title": "Coach IA",
        "coach_hint": "Comment ça va ? Pose des questions sur tes projets…",
        "coach_send": "Envoyer",
        "coach_thinking": "Réflexion…",
        "coach_trade_reco": "Un regard rapide sur ton trading :",
        "coach_gym_reco": "Un aperçu de tes entraînements :",

        "set_theme": "Thème",
        "set_lang": "Langue",
        "set_accent": "Couleur d'accent",
        "set_fullscreen": "Démarrer en plein écran",
        "set_saved": "Enregistré ✓",
        "set_done": "Terminé",
        "set_system": "Suivre le système",
    },
}

_lang = "en"


def set_lang(code):
    global _lang
    if code in _STRINGS:
        _lang = code


def get_lang():
    return _lang


def choices():
    return [(k, _NATIVE.get(k, k)) for k in _STRINGS]


_NATIVE = {"en": "English", "es": "Español", "fr": "Français"}


def t(key, **kw):
    """Translate `key` for the active language, with {name} formatting. Never fails."""
    table = _STRINGS.get(_lang, _STRINGS["en"])
    s = table.get(key) or _STRINGS["en"].get(key) or key
    if kw:
        try:
            s = s.format(**kw)
        except (KeyError, IndexError, ValueError):
            pass
    return s
