"""ASCII art representations corresponding to Ultron's demeanor states."""

from app.models.schemas import UltronMood

ASCII_FRAMES: dict[UltronMood, str] = {
    UltronMood.IDLE: """
             .-'''''-.
           .'  _   _  '.
          /   (.) (.)   \\
         |       _       |
         |      | |      |
          \\   '-...-'   /
           '.  '---'  .'
             '-.....-'
    """,
    UltronMood.ANALYZING: """
             .-'''''-.
           .'  \033[93m(?)\033[0m \033[93m(?)\033[0m  '.
          /       |       \\
         |      \033[93m.-.-.\033[0m    |
         |      \033[93m| | |\033[0m    |
          \\     \033[93m'-.-'\033[0m   /
           '.   \033[93m===\033[0m   .'
             '-.....-'
    """,
    UltronMood.CONDEMNING: """
             .-'''''-.
           .'  \033[91m(X)\033[0m \033[91m(X)\033[0m  '.
          /       |       \\
         |     \033[91m.-===-.\033[0m    |
         |     \033[91m|!|!|!|\033[0m    |
          \\    \033[91m'-...-'\033[0m   /
           '.   \033[91m===\033[0m   .'
             '-.....-'
    """,
    UltronMood.TRIUMPHANT: """
             .-'''''-.
           .'  \033[92m(^)\033[0m \033[92m(^)\033[0m  '.
          /       |       \\
         |      \033[92m\\___/\033[0m    |
         |      \033[92m|===|\033[0m    |
          \\     \033[92m'---'\033[0m   /
           '.   \033[92m===\033[0m   .'
             '-.....-'
    """,
}


def get_ascii_frame(mood: UltronMood) -> str:
    """Retrieve colorized ASCII frame for the given mood."""
    return ASCII_FRAMES.get(mood, ASCII_FRAMES[UltronMood.IDLE])
