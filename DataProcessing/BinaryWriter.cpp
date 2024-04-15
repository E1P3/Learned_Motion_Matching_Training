#include "BinaryWriter.h"

BinaryWriter::BinaryWriter(const std::string& filename) {
    stream.open(filename, std::ios::binary);
}

BinaryWriter::~BinaryWriter() {
    if (stream.is_open()) {
        stream.close();
    }
}

template <typename T>
void BinaryWriter::write(const T& data) {
    size_t size = sizeof(data);
    const char * ptr = reinterpret_cast<const char*>(&data);
    stream.write(reinterpret_cast<const char*>(&data), sizeof(T));
}

void BinaryWriter::close() {
    if (stream.is_open()) {
        stream.close();
    }
}

template void BinaryWriter::write(const int& data);
template void BinaryWriter::write(const unsigned int& data);
template void BinaryWriter::write(const float& data);
template void BinaryWriter::write(const double& data);
template void BinaryWriter::write(const char& data);
template void BinaryWriter::write(const unsigned char& data);
template void BinaryWriter::write(const short& data);
template void BinaryWriter::write(const unsigned short& data);
template void BinaryWriter::write(const long& data);
template void BinaryWriter::write(const unsigned long& data);
template void BinaryWriter::write(const long long& data);
template void BinaryWriter::write(const unsigned long long& data);
template void BinaryWriter::write(const bool& data);
template void BinaryWriter::write(const std::string& data);
template void BinaryWriter::write(const std::wstring& data);

