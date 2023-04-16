import torch
from lib import model, game


model_name = "saves/Model128/best_020_01800.dat"
# Load your trained model
mymodel = model.Net(input_shape=model.OBS_SHAPE, actions_n=game.GAME_COLS)
mymodel.load_state_dict(torch.load(model_name))
mymodel.eval()

# state_list = game.decode_binary(7688512152522457160)
state_list = [[]] * game.GAME_COLS
print (state_list)
print(model.state_lists_to_batch([state_list], [0]))
print(mymodel.forward(model.state_lists_to_batch([state_list], [0])))
batch_v = model.state_lists_to_batch([state_list], [0])

# Convert the model to TorchScript
traced_script_module = torch.jit.trace(mymodel, batch_v)

# Save the TorchScript model
traced_script_module.save(model_name + ".trace")
