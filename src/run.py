from model import DeepfakeModel
from visualization import create_model_visualization

def main():
    """Set up and run the model visualization server."""
    server = create_model_visualization(DeepfakeModel)
    server.port = 8521  # Default Mesa port
    server.launch()

if __name__ == "__main__":
    main() 