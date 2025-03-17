from model import ContentSpreadModel
from visualization import create_model_visualization

# Create and launch the server
server = create_model_visualization(ContentSpreadModel)
server.port = 8521  # The default
server.launch() 