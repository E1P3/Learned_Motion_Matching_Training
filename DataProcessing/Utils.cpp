#include "Utils.h"

FbxManager* Utils::lSdkManager = nullptr;
FbxIOSettings* Utils::ios = nullptr;

void Utils::InitialiseSdk() {
	// The first thing to do is to create the FBX SDK manager which is the
	// object allocator for almost all the classes in the SDK.
	lSdkManager = FbxManager::Create();
	if (!lSdkManager) {
		FBXSDK_printf("Error: Unable to create FBX Manager!\n");
		exit(1);
	}
	else {
		FBXSDK_printf("Autodesk FBX SDK version %s\n", lSdkManager->GetVersion());
	}

	// Create the IO settings object.
	ios = FbxIOSettings::Create(lSdkManager, IOSROOT);
	lSdkManager->SetIOSettings(ios);
}

bool Utils::SaveScene(FbxDocument* pScene, const char* pFilename, int pFileFormat, bool pEmbedMedia) {
	int lMajor, lMinor, lRevision;
	bool lStatus;

	// Create an exporter.
	FbxExporter* lExporter = FbxExporter::Create(lSdkManager, "");

	if (pFileFormat < 0 || pFileFormat >= lSdkManager->GetIOPluginRegistry()->GetWriterFormatCount())
	{
		// Write in fall back format in less no ASCII format found
		pFileFormat = lSdkManager->GetIOPluginRegistry()->GetNativeWriterFormat();

		//Try to export in ASCII if possible
		int lFormatIndex, lFormatCount = lSdkManager->GetIOPluginRegistry()->GetWriterFormatCount();

		for (lFormatIndex = 0; lFormatIndex < lFormatCount; lFormatIndex++)
		{
			if (lSdkManager->GetIOPluginRegistry()->WriterIsFBX(lFormatIndex))
			{
				FbxString lDesc = lSdkManager->GetIOPluginRegistry()->GetWriterFormatDescription(lFormatIndex);
				const char* lASCII = "ascii";
				if (lDesc.Find(lASCII) >= 0)
				{
					pFileFormat = lFormatIndex;
					break;
				}
			}
		}
	}

	// Initialize the exporter.
	lStatus = lExporter->Initialize(pFilename, pFileFormat, lSdkManager->GetIOSettings());
	if (!lStatus) {
		FBXSDK_printf("Call to FbxExporter::Initialize() failed.\n");
		FBXSDK_printf("Error returned: %s\n\n", lExporter->GetStatus().GetErrorString());
		return false;
	}

	// Export the scene.
	lStatus = lExporter->Export(pScene);

	// Destroy the exporter.
	lExporter->Destroy();
	return lStatus;
}

FbxScene* Utils::ImportFbx(const char* fbxPath) {
	// Create the importer.
	FbxImporter* lImporterFBX = FbxImporter::Create(lSdkManager, "");

	// Use the first argument as the filename for the importer.
	if (!lImporterFBX->Initialize(fbxPath, -1, lSdkManager->GetIOSettings())) {
		FBXSDK_printf("Call to FbxImporter::Initialize() failed.\n");
		FBXSDK_printf("Error returned: %s\n\n", lImporterFBX->GetStatus().GetErrorString());
		exit(-1);
	}

	// Create a new scene so it can be populated by the imported file.
	FbxScene* lScene = FbxScene::Create(lSdkManager, "myScene");

	// Import the contents of the file into the scene.
	lImporterFBX->Import(lScene);

	// The file has been imported; we can get rid of the importer.
	lImporterFBX->Destroy();

	return lScene;
}	

FbxScene* Utils::ImportBvh(const char* bvhPath) {
	// Create the importer.
	FbxImporter* lImporterBVH = FbxImporter::Create(lSdkManager, "");

	int format = lSdkManager->GetIOPluginRegistry()->FindReaderIDByExtension("bvh");

	// Use the first argument as the filename for the importer.
	if (!lImporterBVH->Initialize(bvhPath, format, lSdkManager->GetIOSettings())) {
		FBXSDK_printf("Call to FbxImporter::Initialize() failed.\n");
		FBXSDK_printf("Error returned: %s\n\n", lImporterBVH->GetStatus().GetErrorString());
		exit(-1);
	}

	// Create a new scene so it can be populated by the imported file.
	FbxScene* lScene = FbxScene::Create(lSdkManager, "myScene");

	// Import the contents of the file into the scene.
	lImporterBVH->Import(lScene);

	// The file has been imported; we can get rid of the importer.
	lImporterBVH->Destroy();

	return lScene;
}	

void Utils::ConvertBvhToFbx(const char* bvhPath, const char* fbxPath) {
	FBXSDK_printf("Converting %s\n", bvhPath);
	FbxScene* lScene = ImportBvh(bvhPath);
	bool result = SaveScene(lScene, fbxPath, -1, false);
	if (!result) {
		FBXSDK_printf("Failed to save scene\n");
	}
	FBXSDK_printf("Saved as %s \n", fbxPath);

}