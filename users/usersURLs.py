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

    # connexion / authentification avec cookies JWT HttpOnly
    path(
        "login/",
        views.login_user,
        name="login_user"
    ),

    # deconnexion (invalidation refresh token et suppression cookies)
    path(
        "logout/",
        views.logout_user,
        name="logout_user"
    ),

    # deconnexion de toutes les sessions
    path(
        "logout-all/",
        views.logout_all_users,
        name="logout_all_users"
    ),

    # rafraichissement du token via cookie HttpOnly
    path(
        "token/refresh/",
        views.CookieTokenRefreshView.as_view(),
        name="token_refresh"
    ),

    # profil de l'utilisateur actuellement connecte (Angular session restore)
    path(
        "me/",
        views.me_user,
        name="me_user"
    ),

    # changement de mot de passe securise
    path(
        "change-password/",
        views.change_password,
        name="change_password"
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