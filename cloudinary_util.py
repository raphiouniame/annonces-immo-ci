"""
Utilitaires pour l'intégration de Cloudinary.
Permet d'uploader, supprimer et gérer des fichiers (images, vidéos) dans le cloud.
Utilise les upload presets : immo_upload (images) et immo_upload_video (vidéos).
"""

import cloudinary
import cloudinary.uploader
import os
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Noms des upload presets
PRESET_IMAGE = "immo_upload"
PRESET_VIDEO = "immo_upload_video"

# Dossiers Cloudinary
FOLDER_IMAGE = "annonces/images"
FOLDER_VIDEO = "annonces/videos"


def init_cloudinary():
    """
    Initialise Cloudinary à partir des variables d'environnement.
    Lève une exception si les variables critiques sont manquantes.
    À appeler une seule fois au démarrage de l'application.
    """
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if not cloud_name or not api_key or not api_secret:
        missing = [key for key, val in {
            'CLOUDINARY_CLOUD_NAME': cloud_name,
            'CLOUDINARY_API_KEY': api_key,
            'CLOUDINARY_API_SECRET': api_secret
        }.items() if not val]
        error_msg = f"Cloudinary non configuré : variables manquantes — {', '.join(missing)}"
        logger.critical(error_msg)
        raise RuntimeError(error_msg)

    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True  # Toujours utiliser HTTPS
        )
        logger.info("Cloudinary configuré avec succès.")
    except Exception as e:
        logger.critical(f"Échec de la configuration de Cloudinary : {e}")
        raise RuntimeError("Impossible d'initialiser Cloudinary.") from e


def upload_file(file, resource_type='image'):
    """
    Téléverse un fichier vers Cloudinary en utilisant le bon upload preset.

    :param file: Fichier (FileStorage, bytes, tempfile, etc.)
    :param resource_type: 'image', 'video', 'raw'
    :return: Dict avec 'public_id', 'url', 'type' ou None en cas d'erreur
    """
    if resource_type not in {'image', 'video', 'raw'}:
        logger.warning(f"Type de ressource invalide : {resource_type}")
        return None

    # Déterminer le preset et le dossier
    if resource_type == 'image':
        preset = PRESET_IMAGE
        folder = FOLDER_IMAGE
    elif resource_type == 'video':
        preset = PRESET_VIDEO
        folder = FOLDER_VIDEO
    else:
        preset = None
        folder = None

    upload_options = {
        'resource_type': resource_type,
        'preset': preset,           # Utilise le preset Cloudinary
        'folder': folder,           # Organise dans un dossier
        'use_filename': True,       # Garde le nom original
        'unique_filename': True,    # Génère un ID unique si conflit
        'overwrite': False,         # Ne remplace pas les fichiers
        'timeout': 10,
    }

    try:
        result = cloudinary.uploader.upload(file, **upload_options)
        logger.info(f"Fichier uploadé : {result['public_id']} ({result['secure_url']})")
        return {
            'public_id': result['public_id'],
            'url': result['secure_url'],
            'type': resource_type
        }
    except Exception as e:
        logger.error(f"[Cloudinary] Échec de l'upload : {str(e)}", exc_info=True)
        return None


def delete_file(public_id):
    """
    Supprime un fichier sur Cloudinary.

    :param public_id: Identifiant du fichier
    :return: True si supprimé, False sinon
    """
    if not public_id:
        logger.warning("Tentative de suppression avec public_id vide.")
        return False

    try:
        result = cloudinary.uploader.destroy(public_id)
        success = result.get('result') == 'ok'
        if success:
            logger.info(f"Fichier supprimé : {public_id}")
        else:
            logger.warning(f"Échec de suppression (pas trouvé ou déjà supprimé) : {public_id}")
        return success
    except Exception as e:
        logger.error(f"[Cloudinary] Impossible de supprimer {public_id} : {str(e)}", exc_info=True)
        return False


def detect_resource_type(filename):
    """
    Détecte le type de ressource à partir de l'extension du fichier.

    :param filename: Nom du fichier (ex: 'ma_photo.jpg')
    :return: 'image', 'video', ou None si inconnu
    """
    if not filename or '.' not in filename:
        return None

    ext = filename.rsplit('.', 1)[-1].lower().strip()

    image_exts = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}
    video_exts = {'mp4', 'mov', 'avi', 'wmv', 'flv', 'webm', 'mkv', 'm4v'}

    if ext in image_exts:
        return 'image'
    elif ext in video_exts:
        return 'video'
    else:
        logger.debug(f"Extension non reconnue pour Cloudinary : .{ext}")
        return None