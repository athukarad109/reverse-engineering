// SimpleCrackMe.cpp : Defines the entry point for the console application.
//

#ifdef WINDOWS
#include <Windows.h>
#include <wincrypt.h>
#endif

#ifdef OSX
#include <CoreFoundation/CoreFoundation.h>
#include <Security/Security.h>
typedef int BOOL;
typedef UInt8 BYTE;
typedef UInt16 WORD;
typedef UInt32 DWORD;
#endif

#if LINUX
#include <stdint.h>
#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/err.h>
typedef int BOOL;
#define FALSE 0
#define TRUE 1
typedef uint8_t BYTE;
typedef uint16_t WORD;
typedef uint32_t DWORD;
#endif

#include <time.h>

#include <string.h>
#include <stdio.h>

#define DEBUGLINE fprintf(stderr, "DBG: %d\n", __LINE__)

BOOL doCheck(char user[], unsigned char* key);

BOOL doCheckConvert(char user[], char keychars[]) {

	//DEBUGLINE;

	if (strlen(keychars) != 32) {
		return FALSE;
	}

	//DEBUGLINE;

	unsigned char key[16];

	char temp[3] = { 0 };
	char* check;
	for (int i = 0; i < 16; i++) {
		memcpy(temp, &keychars[2 * i], 2);
		key[i] = strtol(temp, &check, 16);
#ifdef _DEBUG
		fprintf(stderr, "key[%d] = %02hhx\n", i, key[i]);
#endif
		if (check != &temp[2]) {
			return FALSE;
		}
	}

	//DEBUGLINE;
	return doCheck(user, key);
}

BOOL doCheck(char user[], unsigned char* key) {
#ifdef WINDOWS
	HCRYPTPROV hProv = 0;
	HCRYPTHASH hHash = 0;
#endif
#ifdef OSX
    CFErrorRef error = NULL;
    SecTransformRef digestTransform = NULL;
#endif
#ifdef LINUX
	EVP_MD_CTX* mdctx;
#endif

	BOOL bResult = FALSE;

#ifdef WINDOWS
	bResult = CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT);
	if (!bResult) {
		return FALSE;
	}
#endif
#ifdef OSX
    // Nothing
#endif
#ifdef LINUX
	mdctx = EVP_MD_CTX_create();
	if (mdctx == NULL) {
		return FALSE;
	}
#endif

	//DEBUGLINE;

#ifdef WINDOWS
	bResult = CryptCreateHash(hProv, CALG_SHA1, 0, 0, &hHash);
	if (!bResult) {
		CryptReleaseContext(hProv, 0);
		return FALSE;
	}
#endif
#ifdef OSX
    digestTransform = SecDigestTransformCreate(kSecDigestSHA1, 160, &error);
    if (error) {
        CFShow(error);
        CFRelease(error);
        return FALSE;
    }
#endif
#ifdef LINUX
	bResult = EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL);
	if (!bResult) {
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}
#endif

	//DEBUGLINE;

#ifdef WINDOWS
	bResult = CryptHashData(hHash, (const BYTE*)user, strlen(user), 0);
	if (!bResult) {
		CryptReleaseContext(hProv, 0);
		CryptDestroyHash(hHash);
		return FALSE;
	}
#endif
#ifdef OSX
    CFDataRef sourceData = CFDataCreate(kCFAllocatorDefault, (const UInt8*)user, strlen(user));
    if (!sourceData) {
        CFRelease(digestTransform);
        return FALSE;
    }
    SecTransformSetAttribute(digestTransform, kSecTransformInputAttributeName, (CFDataRef)sourceData, &error);
    if (error) {
        CFShow(error);
        CFRelease(error);
        CFRelease(sourceData);
        CFRelease(digestTransform);
        return FALSE;
    }
#endif
#ifdef LINUX
	bResult = EVP_DigestUpdate(mdctx, user, strlen(user));
	if (!bResult) {
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}
#endif

	//DEBUGLINE;

	BYTE sha1Data[20] = { 0 };
	DWORD cbHash = sizeof(sha1Data);
#ifdef WINDOWS
	bResult = CryptGetHashParam(hHash, HP_HASHVAL, sha1Data, &cbHash, 0);
	if (!bResult) {
		CryptReleaseContext(hProv, 0);
		CryptDestroyHash(hHash);
		return FALSE;
	}
#endif
#ifdef OSX
    CFDataRef outDataRef = (CFDataRef)SecTransformExecute(digestTransform, &error);
    if (error) {
        CFShow(error);
        CFRelease(error);
        CFRelease(sourceData);
        CFRelease(digestTransform);
        return FALSE;
    }
    if (20 != CFDataGetLength(outDataRef)) {
        fprintf(stderr, "Not 20 bytes?\n");
        CFRelease(sourceData);
        CFRelease(digestTransform);
        CFRelease(outDataRef);
        return FALSE;
    }
    memcpy(sha1Data, CFDataGetBytePtr(outDataRef), 20);
#endif
#ifdef LINUX
	bResult = EVP_DigestFinal_ex(mdctx, sha1Data, NULL);
	if (!bResult) {
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}
#endif

	//DEBUGLINE;

#ifdef WINDOWS
	CryptReleaseContext(hProv, 0);
	CryptDestroyHash(hHash);
#endif
#ifdef OSX
    CFRelease(sourceData);
    CFRelease(digestTransform);
    CFRelease(outDataRef);
#endif
#ifdef LINUX
	EVP_MD_CTX_destroy(mdctx);
#endif

	//DEBUGLINE;

#if 0
	printf("SHA1(user) = ");
	for (int i = 0; i < cbHash; i++) {
		printf("%02hhx", sha1Data[i]);
	}
	printf("\n");
#endif

	WORD checkSHA1 = 0;

	for (int i = 0; i < cbHash; i++) {
		checkSHA1 *= 31;
		checkSHA1 += sha1Data[i];
	}

	WORD checkKey = 0;
	for (int i = 0; i < 16; i++) {
		checkKey *= 127;
		checkKey += key[i];
	}

#ifdef _DEBUG
	printf("checkSHA1 = %04x, checkKey = %04x\n", checkSHA1, checkKey);
#endif

	return checkSHA1 == checkKey;
}

int main(int argc, char* argv[])
{
#ifdef LINUX
	ERR_load_crypto_strings();
	OpenSSL_add_all_algorithms();
	OPENSSL_config(NULL);
#endif
#ifdef _DEBUG
	if (argc == 2) {
		unsigned char key[16];
		srand(time(NULL));
		for (int i = 0; i < 16; i++) {
			key[i] = rand();
		}
		while (1) {
			printf("Key: ");
			for (int i = 0; i < 16; i++) {
				printf("%02hhx", key[i]);
			}
			printf(": ");
			if (doCheck(argv[1], key)) {
				break;
			}
			for (int i = 15; i >= 0; i--) {
				key[i]++;
				if (key[i] != 0) break;
			}
			/*for (int i = 0; i < 16; i++) {
				key[i] = rand();
			}*/
		}
		printf("Found key: ");
		for (int i = 0; i < 16; i++) {
			printf("%02hhx", key[i]);
		}
		printf("\n");
		goto LAME_EXIT;
	}
#endif

	if (argc != 3) {
		fprintf(stderr, "Error: Please provide a username and key\n");
#ifdef WINDOWS
		getc(stdin);
#endif
		exit(-1);
	}

	if (doCheckConvert(argv[1], argv[2])) {
		printf("You're winner!\n");
	}
	else {
		printf("You lose\n");
	}

#ifdef _DEBUG
LAME_EXIT:
#endif
#ifdef WINDOWS
	getc(stdin);
#endif
	exit(0);
}

