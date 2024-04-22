# Learned_Motion_Matching_Training
Simple training pipeline for NN models required for motion matching in UE5.

# Data processing
To train the necessary modes, the animation dataset and the model of the character need to be established. Modify the "files" and "bonesToExtract" vectors in [FbxToBinConverter.cpp](https://github.com/E1P3/Learned_Motion_Matching_Training/blob/main/DataProcessing/FbxToBinConverter.cpp) to define those properties. Then simply build the VS project and run the program. The program expects Autodesk FBX SDK, which can be downloaded [here](https://aps.autodesk.com/developer/overview/fbx-sdk). Go to the install location and copy the files into the FBXSDK folder made in the DataProcessing folder. If not just link it using VSCode. The program itself just converts the bvh files to fbx and then extract that data to a binary to be used for Model Training.  

# Model Training 
To obtain the neural networks necessary for the character controller to work, a database binary has to be created. Run [generate_database.py](https://github.com/E1P3/Learned_Motion_Matching_Training/blob/main/ModelTraining/generate_database.py) to generate the database as well as feature vetors necessary for training. The next step is to train the decompressor by running [train_decompressor.py](https://github.com/E1P3/Learned_Motion_Matching_Training/blob/main/ModelTraining/train_decompressor.py). After the decompressor has been trained and latent.bin was generated, the projector and stepper networks can be trained ([train_projector.py](https://github.com/E1P3/Learned_Motion_Matching_Training/blob/main/ModelTraining/train_projector.py) and [train_stepper.py](https://github.com/E1P3/Learned_Motion_Matching_Training/blob/main/ModelTraining/train_stepper.py)).

And thats it! All that is left is to import the ONNX models generated in the "Models" folder into UE5 project that uses the LMM character controller, available [here](https://github.com/E1P3/Learned_Motion_Matching_UE5)

The actual demo of a working project is available [here](https://youtu.be/MKmNHGQb4Kk)

have fun :)

