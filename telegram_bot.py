#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configuration
BOT_TOKEN = "7553192698:AAGU4yYCTjYJ5iVYVtbMREKIDbLbZZ6cb7s"

# ⚠️ IMPORTANT : Remplacez par l'ID ou le username de votre canal
# Format ID : -1001234567890
# Format username : @votre_canal
CANAL_REQUIS = "@ziablowcontent"  # À modifier !

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def verifier_abonnement(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Vérifie si l'utilisateur est abonné au canal requis
    
    Args:
        user_id: ID de l'utilisateur Telegram
        context: Contexte du bot
        
    Returns:
        True si l'utilisateur est abonné, False sinon
    """
    try:
        member = await context.bot.get_chat_member(chat_id=CANAL_REQUIS, user_id=user_id)
        # Statuts possibles : creator, administrator, member, restricted, left, kicked
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'abonnement: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Gère la commande /start
    Affiche le message de bienvenue avec le bouton de vérification
    """
    user = update.effective_user
    
    # Création du clavier avec le bouton de vérification
    keyboard = [
        [InlineKeyboardButton("✅ Vérifier mon abonnement", callback_data='verifier')],
        [InlineKeyboardButton("📢 S'abonner au canal", url=f"https://t.me/{CANAL_REQUIS.replace('@', '')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🤖 Bienvenue {user.first_name} !

Pour accéder au contenu de ce bot, vous devez d'abord vous abonner à notre canal :

📢 Canal : {CANAL_REQUIS}

👇 Cliquez sur le bouton ci-dessous pour vous abonner, puis vérifiez votre abonnement.
"""
    
    await update.message.reply_text(message, reply_markup=reply_markup)


async def verifier_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Gère le callback du bouton de vérification
    Vérifie l'abonnement et affiche le résultat
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_name = query.from_user.first_name
    
    # Vérification de l'abonnement
    est_abonne = await verifier_abonnement(user_id, context)
    
    if est_abonne:
        # L'utilisateur est abonné
        keyboard = [
            [InlineKeyboardButton("🚀 Accéder au contenu", callback_data='acceder_contenu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
✅ Parfait {user_name} !

Vous êtes bien abonné au canal {CANAL_REQUIS}

Vous pouvez maintenant accéder au contenu du bot ! 🎉
"""
        await query.edit_message_text(message, reply_markup=reply_markup)
        
    else:
        # L'utilisateur n'est pas abonné
        keyboard = [
            [InlineKeyboardButton("📢 S'abonner au canal", url=f"https://t.me/{CANAL_REQUIS.replace('@', '')}")],
            [InlineKeyboardButton("🔄 Vérifier à nouveau", callback_data='verifier')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
❌ Désolé {user_name}...

Vous n'êtes pas encore abonné au canal {CANAL_REQUIS}

👉 Veuillez vous abonner au canal, puis cliquez sur "Vérifier à nouveau"
"""
        await query.edit_message_text(message, reply_markup=reply_markup)


async def acceder_contenu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Gère l'accès au contenu après vérification réussie
    """
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Vérification finale avant d'accéder au contenu
    est_abonne = await verifier_abonnement(user_id, context)
    
    if est_abonne:
        message = """
🎉 Accès accordé !

Voici le contenu réservé aux abonnés :

📝 [Le contenu sera ajouté ici plus tard]

Utilisez /start pour revenir au menu principal.
"""
        await query.edit_message_text(message)
    else:
        await query.edit_message_text("❌ Erreur : Vous devez être abonné pour accéder au contenu.")


def main() -> None:
    """
    Point d'entrée principal du bot
    """
    # Création de l'application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Gestionnaires de commandes
    application.add_handler(CommandHandler("start", start))
    
    # Gestionnaires de callbacks
    application.add_handler(CallbackQueryHandler(verifier_callback, pattern='^verifier$'))
    application.add_handler(CallbackQueryHandler(acceder_contenu, pattern='^acceder_contenu$'))
    
    # Lancement du bot
    logger.info("🤖 Bot démarré avec succès !")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
