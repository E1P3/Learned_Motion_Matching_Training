The code for training is a slightly modified version of the solution made by Daniel Holden (https://github.com/orangeduck/Motion-Matching).
The changes were mainly to import the models into ONNX format to later import into UE5.

To train simply drop the binaries from Animations/LAFAN1BIN to the Data folder, specify them in generate_database.py and run it to create the db for training.
The train each model just run the corresponding .py file. Make sure to train the decompressor first before anything else. 

The files needed for UE5 project are the ONNX models in Models folder as well as features.bin in the Database folder. 
