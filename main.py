"""
Star Wars: Darth Vader RPG - Main Entry Point
Launches the GUI version of the game.
"""

from src.gui import GameWindow


def main():
    """
    Main function - initializes and runs the game.
    """
    # Create the game window
    window = GameWindow(
        width=1280,
        height=720,
        title="Star Wars: Darth Vader - The Dark Times"
    )
    
    # Start the game loop
    window.run()


if __name__ == "__main__":
    main()