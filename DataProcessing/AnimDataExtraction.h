#pragma once

#include<fbxsdk.h>
#include<map>
#include <iostream>
#include <ostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <queue>
#include "Utils.h"
#include "BinaryWriter.h"

struct BoneData {
	FbxAMatrix globalTransform;
	FbxAMatrix localTransform;

	BoneData(const FbxAMatrix& pGlobalTransform = FbxAMatrix(), const FbxAMatrix& pLocalTransform = FbxAMatrix())
		: globalTransform(pGlobalTransform), localTransform(pLocalTransform) {
	}

	float* getWorldPosition() {
		float* pos = new float[3];
		FbxVector4 lT = globalTransform.GetT();
		pos[0] = lT[0];
		pos[1] = lT[1];
		pos[2] = lT[2];
		return pos;
	}

	float* getLocalPosition() {
		float* pos = new float[3];
		FbxVector4 lT = localTransform.GetT();
		pos[0] = lT[0];
		pos[1] = lT[1];
		pos[2] = lT[2];
		return pos;
	}

	float* getWorldRotation() {
		float* rot = new float[4];
		FbxVector4 lR = globalTransform.GetR();
		rot[0] = lR[0];
		rot[1] = lR[1];
		rot[2] = lR[2];
		rot[3] = lR[3];
		return rot;
	}

	float* getLocalRotation() {
		float* rot = new float[4];
		FbxVector4 lR = localTransform.GetR();
		rot[0] = lR[0];
		rot[1] = lR[1];
		rot[2] = lR[2];
		rot[3] = lR[3];
		return rot;
	}

	double* getLocalPositionDouble() {
		double* pos = new double[3];
		FbxVector4 lT = localTransform.GetT();
		pos[0] = lT[0];
		pos[1] = lT[1];
		pos[2] = lT[2];
		return pos;
	}

	double* getLocalRotationDouble() {
		double* rot = new double[4];
		FbxVector4 lR = localTransform.GetR();
		rot[0] = lR[0];
		rot[1] = lR[1];
		rot[2] = lR[2];
		rot[3] = lR[3];
		return rot;
	}

	double* getWorldPositionDouble() {
		double* pos = new double[3];
		FbxVector4 lT = globalTransform.GetT();
		pos[0] = lT[0];
		pos[1] = lT[1];
		pos[2] = lT[2];
		return pos;
	}

	double* getWorldRotationDouble() {
		double* rot = new double[4];
		FbxVector4 lR = globalTransform.GetR();
		rot[0] = lR[0];
		rot[1] = lR[1];
		rot[2] = lR[2];
		rot[3] = lR[3];
		return rot;
	}
};

struct AnimationData {
	std::vector<std::map<FbxNode*, BoneData>> frames;
	std::vector<FbxNode*> bones;
	std::vector<int> boneParents;
	std::string name;
};

class AnimDataExtraction {
public:

	static AnimationData* ProcessFile(const char* fbxPath, std::vector<std::string> boneNames) {
		FbxScene* lScene = Utils::ImportFbx(fbxPath);
		std::vector<FbxAnimStack*> animStacks = GetAnimStack(lScene);
		std::vector<FbxAnimLayer*> animLayers;
		for (int i = 0; i < animStacks.size(); i++) {
			std::vector<FbxAnimLayer*> stackLayers = GetAnimLayers(animStacks[i]);
			animLayers.insert(animLayers.end(), stackLayers.begin(), stackLayers.end());
		}
		std::vector<FbxNode*> bones = GetBoneData(lScene, boneNames);

		FbxString lOutputString = "SCENE INFO: \n\n";
		lOutputString += "\nAnim Stacks: \n\n";
		for (int i = 0; i < animStacks.size(); i++) {
			lOutputString += animStacks[i]->GetName();
			lOutputString += "\n";
		}
		lOutputString += "\nLayers: \n\n";
		for (int i = 0; i < animLayers.size(); i++) {
			lOutputString += animLayers[i]->GetName();
			lOutputString += "\n";
		}
		lOutputString += "\nBones: \n\n";
		for (int i = 0; i < bones.size(); i++) {
			lOutputString += bones[i]->GetName();
			lOutputString += "\n";
		}
		FBXSDK_printf(lOutputString);
		FbxAnimStack* lCurrentAnimationStack = lScene->GetCurrentAnimationStack();
		std::vector<std::map<FbxNode*, BoneData>> frames = GetAnimationData(lCurrentAnimationStack, bones, GetFrameRate(lScene));
		AnimationData* animData = new AnimationData();
		animData->frames = frames;
		animData->bones = bones;
		animData->name = getFileName(fbxPath);
		animData->boneParents = getBoneParents(bones);

		return animData;
	}

	static std::string getFileName(const char* filePath) {
		std::string lFilePath = filePath;
		std::string lFileName = lFilePath.substr(lFilePath.find_last_of("/") + 1, 4 - lFilePath.find_last_of("/") - 1);
		return lFileName;
	}

	static std::vector<int> getBoneParents(std::vector<FbxNode*> bones) {
		std::vector<int> parents;
		for (int i = 0; i < bones.size(); i++) {
			FbxNode* parent = bones[i]->GetParent();
			FbxString output = "Bone: ";
			output += i;
			output += bones[i]->GetName();
			output += " Parent: ";
			if (parent != NULL) {
				output += parent->GetName();
			}
			else {
				output += "NULL";
			}
			
			output += "\n";
			FBXSDK_printf(output);

			for (int j = 0; j < bones.size(); j++) {
				if (bones[j] == parent) {
					parents.push_back(j);
					break;
				}
				else {
					if (j == bones.size() - 1) {
						parents.push_back(-1);
					}
				}
			}
		}
		return parents;
	}

	static void SaveParentsToFile(std::vector<int> parents, const char* fileName) {
		BinaryWriter writer(fileName);
		writer.write((int)parents.size());
		for (int i = 0; i < parents.size(); i++) {
			writer.write(parents[i]);
		}
		writer.close();
	}

	/*
	Saving to binary file.

	1.First write num of frames and num of bones
	2.Write each frame as bones and their positions and rotations
		-in this case p1,p2,p3,r1,r2,r3,r4 for each bone in each frame
	*/
	static void SaveAnimationFrames(const AnimationData* pAnimData, const char* fileName, bool saveGlobal = false) {
		BinaryWriter writer(fileName);
		writer.write((float)pAnimData->frames.size());
		writer.write((float)pAnimData->bones.size()); //excluding fbx root node

		for (int i = 0; i < pAnimData->frames.size(); i++) {
			std::map<FbxNode*, BoneData> lFrame = pAnimData->frames[i];
			for (int j = 0; j < pAnimData->bones.size(); j++) {

				double* position = lFrame[pAnimData->bones[j]].localTransform.GetT().Buffer();
				double* rotation = lFrame[pAnimData->bones[j]].localTransform.GetQ().Buffer();
				double* globalPosition = lFrame[pAnimData->bones[j]].globalTransform.GetT().Buffer();
				double* globalRotation = lFrame[pAnimData->bones[j]].globalTransform.GetQ().Buffer();

				
				float positions[3] = { (float)position[0], -(float)position[1], (float)position[2] };
				float rotations[4] = { -(float)rotation[0], (float)rotation[1], -(float)rotation[2], (float)rotation[3] };
				float globalPositions[3] = { (float)globalPosition[0], -(float)globalPosition[1], (float)globalPosition[2] };
				float globalRotations[4] = { -(float)globalRotation[0], (float)globalRotation[1], -(float)globalRotation[2], (float)globalRotation[3] };

				writer.write(positions[0]);
				writer.write(positions[1]);
				writer.write(positions[2]);
				writer.write(rotations[0]);
				writer.write(rotations[1]);
				writer.write(rotations[2]);
				writer.write(rotations[3]);
				if (saveGlobal) {
					writer.write(globalPositions[0]);
					writer.write(globalPositions[1]);
					writer.write(globalPositions[2]);
					writer.write(globalRotations[0]);
					writer.write(globalRotations[1]);
					writer.write(globalRotations[2]);
					writer.write(globalRotations[3]);
				}

			}
		}
		writer.close();
		FbxString lOutputString = "Animation Frames Saved to: ";
		lOutputString += fileName;
		lOutputString += "\n";
		FBXSDK_printf(lOutputString);
	}

private:
	static std::vector<FbxAnimStack*> GetAnimStack(FbxScene* pScene) {
		std::vector<FbxAnimStack*> animStacks;
		for (int i = 0; i < pScene->GetSrcObjectCount<FbxAnimStack>(); i++) {
			FbxAnimStack* lAnimStack = pScene->GetSrcObject<FbxAnimStack>(i);
			animStacks.push_back(lAnimStack);
		}
		return animStacks;
	}

	static std::vector<FbxAnimLayer*> GetAnimLayers(FbxAnimStack* pAnimStack) {
		std::vector<FbxAnimLayer*> animLayers;
		int nbAnimLayers = pAnimStack->GetMemberCount<FbxAnimLayer>();
		FbxString lOutputString;

		for (int l = 0; l < nbAnimLayers; l++)
		{
			FbxAnimLayer* lAnimLayer = pAnimStack->GetMember<FbxAnimLayer>(l);
			animLayers.push_back(lAnimLayer);
		}
		return animLayers;
	}

	static std::vector<FbxNode*> GetBoneData(FbxScene* pScene, std::vector<std::string> boneNames) {
		std::queue<FbxNode*> nodeQueue;
		std::vector<FbxNode*> bones;
		FbxNode* lRootNode = pScene->GetRootNode();
		nodeQueue.push(lRootNode);
		while (!nodeQueue.empty()) {
			FbxNode* lCurrentNode = nodeQueue.front();
			nodeQueue.pop();
			for (int i = 0; i < boneNames.size(); i++) {
				if (lCurrentNode->GetName() == boneNames[i]) {
					bones.push_back(lCurrentNode);
				}
			}
			for (int i = 0; i < lCurrentNode->GetChildCount(); i++) {
				nodeQueue.push(lCurrentNode->GetChild(i));
			}
		}
		
		std::vector<FbxNode*> sortedBones;
		for(int i = 0; i < boneNames.size(); i++) {
			for (int j = 0; j < bones.size(); j++) {
				if (bones[j]->GetName() == boneNames[i]) {
					sortedBones.push_back(bones[j]);
				}
			}
		}

		return sortedBones;
	}

	static std::vector<std::map<FbxNode*, BoneData>> GetAnimationData(FbxAnimStack* pAnimStack, std::vector<FbxNode*> pBones, FbxTime::EMode pFrameRate) {
		FbxTime lStart, lStop;
		FbxTimeSpan lTimeSpan;
		lTimeSpan = pAnimStack->GetLocalTimeSpan();
		lStart = lTimeSpan.GetStart();
		lStop = lTimeSpan.GetStop();

		FbxLongLong lFrameCount = lStop.GetFrameCount(pFrameRate) - lStart.GetFrameCount(pFrameRate);

		std::vector<std::map<FbxNode*, BoneData>> lFrames;

		for (FbxLongLong i = 0; i < lFrameCount; i++) {
			if (i == lFrameCount - 1) {
				int a = 0;
			}
			FbxTime lCurrentTime;
			lCurrentTime.SetFrame(i, pFrameRate);
			std::map<FbxNode*, BoneData> lFrame = GetFrame(pBones, lCurrentTime);
			lFrames.push_back(lFrame);
		}

		return lFrames;
	}

	static std::map<FbxNode*, BoneData> GetFrame(std::vector<FbxNode*> pBones, FbxTime pTime) {
		std::map<FbxNode*, BoneData> lFrame;
		for (int i = 0; i < pBones.size(); i++) {
			lFrame[pBones[i]] = BoneData(pBones[i]->EvaluateGlobalTransform(pTime), pBones[i]->EvaluateLocalTransform(pTime));
		}
		return lFrame;
	}

	static FbxTime::EMode GetFrameRate(FbxScene* pScene) {
		FbxGlobalSettings& lGlobalSettings = pScene->GetGlobalSettings();
		FbxTime::EMode lFrameRate = lGlobalSettings.GetTimeMode();
		return lFrameRate;
	}

	static FbxTime::EMode SetFrameRate(int pFrameRate) {
		FbxTime::EMode lFrameRate;
		switch (pFrameRate) {
		case 24:
			lFrameRate = FbxTime::eFrames24;
			break;
		case 30:
			lFrameRate = FbxTime::eFrames30;
			break;
		case 60:
			lFrameRate = FbxTime::eFrames60;
			break;
		case 120:
			lFrameRate = FbxTime::eFrames120;
			break;
		case 1000:
			lFrameRate = FbxTime::eFrames1000;
			break;
		default:
			lFrameRate = FbxTime::eDefaultMode;
			break;
		}
		return lFrameRate;
	}

};