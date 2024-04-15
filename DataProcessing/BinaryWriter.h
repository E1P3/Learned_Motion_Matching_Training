#ifndef BINARY_WRITER_H
#define BINARY_WRITER_H

#include <fstream>

class BinaryWriter {
private:
    std::ofstream stream;

public:
    BinaryWriter(const std::string& filename);
    ~BinaryWriter();
    template <typename T>
    void write(const T& data);
    void close();
};

#endif // BINARY_WRITER_H
