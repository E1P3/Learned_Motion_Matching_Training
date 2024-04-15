# Learned_Motion_Matching_Training
Simple training pipeline for NN models required for motion matching in UE5.
The pipeline consists of data extraction from raw mocap file adn flip it to X up orientation, as well as the actual training code for each mdoel.
The code for training is a slightly modified version of the solution made by Daniel Holden (https://github.com/orangeduck/Motion-Matching).
The changes were mainly to import the models into ONNX format to later import into UE5.
