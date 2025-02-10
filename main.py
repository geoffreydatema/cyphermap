from cyphermap import *

def main():

    data = {
        "name": "steve",
        "age": 100,
        "occupation": "intergalactic traveller"
    }

    print(jdump(data))

    encryptedData = stepcrypt(jdump(data), minihash("goodpassword"))
    print(encryptedData)

    decryptedData = destepcrypt(encryptedData, minihash("goodpassword"))
    print(decryptedData)

    writeCyphermap(bencode(jdump(data)), "unencrypted_data", r"C:\\Working\\cyphermap")

    print(jparse(bdecode(readCyphermap(r"C:\\Working\\cyphermap\\unencrypted_data.png"))))

    # !* write separate save/loads for encrypted and unencrypted cyphermaps
    # !* break utilities out into appropriate utils files

if __name__ == "__main__":
    main()