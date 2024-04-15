#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "Utils.h"
#include "AnimDataExtraction.h"
#include<fbxsdk.h>

std::vector<std::string> files = {
"jumps1_subject1",
"jumps1_subject2",
"jumps1_subject5",
"obstacles1_subject1",
"obstacles1_subject2",
"obstacles1_subject5",
"obstacles2_subject1",
"obstacles2_subject2",
"obstacles2_subject5",
"obstacles3_subject3",
"obstacles3_subject4",
"obstacles4_subject2",
"obstacles4_subject3",
"obstacles4_subject4",
"obstacles5_subject2",
"obstacles5_subject3",
"obstacles5_subject4",
"obstacles6_subject1",
"obstacles6_subject4",
"obstacles6_subject5",
"run1_subject2",
"run1_subject5",
"run2_subject1",
"run2_subject4",
"sprint1_subject2",
"sprint1_subject4",
"walk1_subject1",
"walk1_subject2",
"walk1_subject5",
"walk2_subject1",
"walk2_subject3",
"walk2_subject4",
"walk3_subject1",
"walk3_subject2",
"walk3_subject3",
"walk3_subject4",
"walk3_subject5",
"walk4_subject1",
"walk1_subject5",
"run1_subject5",
"pushAndStumble1_subject5"

};


std::vector<std::string> bonesToExtract = {
	"Hips",
	"LeftUpLeg",
	"LeftLeg",
	"LeftFoot",
	"LeftToe",
	"RightUpLeg",
	"RightLeg",
	"RightFoot",
	"RightToe",
	"Spine",
	"Spine1",
	"Spine2",
	"Neck",
	"Head",
	"LeftShoulder",
	"LeftArm",
	"LeftForeArm",
	"LeftHand",
	"RightShoulder",
	"RightArm",
	"RightForeArm",
	"RightHand"
};

void convertAssetsToBvh(std::string bvhFolderPath, std::string fbxFolderPath, std::vector<std::string> files) {
    for (int i = 0; i < files.size(); i++) {
		std::string bvhPath = bvhFolderPath + files[i] + ".bvh";
        std::string fbxPath = fbxFolderPath + files[i] + ".fbx";
		Utils::ConvertBvhToFbx(bvhPath.c_str(), fbxPath.c_str());
	}
}

void ExtractPoses(std::string fbxFolderPath, std::string binFolderPath, std::vector<std::string> files) {
	for (int i = 0; i < files.size(); i++) {
		std::string fbxPath = fbxFolderPath + files[i] + ".fbx";
		AnimationData* animData = AnimDataExtraction::ProcessFile(fbxPath.c_str(), bonesToExtract);
		std::string outputString = binFolderPath + files[i] + ".bin";
		const char* outputFilename = outputString.c_str();
		if (i == 0) {
			std::string boneInfoPath = binFolderPath + "boneParentInfo.bin";
			AnimDataExtraction::SaveParentsToFile(animData->boneParents, boneInfoPath.c_str());
		}
		AnimDataExtraction::SaveAnimationFrames(animData, outputFilename);
	}
}
int main(int argc, char** argv) {
	std::cout << argc << std::endl;

	std::string fbxFolderPath = argc > 1 ? argv[1] : "../Animations/LAFAN1FBX/";
	std::string binFolderPath = argc > 2 ? argv[2] : "../Animations/LAFAN1BIN/";
	std::string bvhFolderPath = argc > 3 ? argv[3] : "../Animations/LAFAN1BVH/";

	//Initialise Sdk Manager
	Utils::InitialiseSdk();

	if (bvhFolderPath != "") {
		convertAssetsToBvh(bvhFolderPath, fbxFolderPath, files);
	}

    ExtractPoses(fbxFolderPath.c_str(), binFolderPath, files);

    return 0;
}
