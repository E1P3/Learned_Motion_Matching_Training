#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include<fbxsdk.h>

class Utils {
public:
	static bool SaveScene(FbxDocument* pScene, const char* pFilename, int pFileFormat, bool pEmbedMedia);
	static void ConvertBvhToFbx(const char* bvhPath, const char* fbxPath);
	static FbxScene* ImportFbx(const char* fbxPath);
	static FbxScene* ImportBvh(const char* bvhPath);
	static void InitialiseSdk();
	static FbxManager* GetSdkManager(){ return lSdkManager; }

private:
	static FbxManager* lSdkManager;
	static FbxIOSettings* ios;
};