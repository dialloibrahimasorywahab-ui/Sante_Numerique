# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [

    # creation d'un utilisateur
    path(
        "",
        views.create_user,
        name="create_user"
    ),

    # connexion / authentification (sans JWT)
    path(
        "login/",
        views.login_user,
        name="login_user"
    ),

    # recuperation d'un utilisateur par son id
    path(
        "<int:user_id>/",
        views.get_user,
        name="get_user"
    ),

    # recuperer tous les utilisateurs
    path(
        "all/",
        views.get_all_user,
        name="get_all_user"
    ),

    # Modifier les informations d'un utilisateur
    path(
        "<int:user_id>/update/",
        views.update_user,
        name="update_user"
    ),

    # Supprimer ou desactiver le compte d'un utilisateur
    path(
        "<int:user_id>/delete/",
        views.delete_user,
        name="delete_user"
    ),


]