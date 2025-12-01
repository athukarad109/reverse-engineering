
#include <stdint.h>
#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <sys/ptrace.h>
#include <signal.h>

typedef int BOOL;
#define FALSE 0
#define TRUE 1
typedef uint8_t BYTE;
typedef uint16_t WORD;
typedef uint32_t DWORD;

#include <time.h>

#include <string.h>
#include <stdio.h>

#define DEBUGLINE fprintf(stderr, "DBG: %d\n", __LINE__)

#define S1(N) #N
#define S2(N) S1(N)
#define LINSTR S2(__LINE__)
#define SALT asm volatile (".intel_syntax noprefix\n\
	mov rax, 2\n\
	cmp rax, 2\n\
	je .skip_junk" LINSTR "\n\
	.byte 0x0f\n\
	.skip_junk" LINSTR ":\n\
	.att_syntax prefix\n\
	");

BOOL doCheck(char user[], unsigned char *key);

BOOL doCheckConvert(char user[], char keychars[])
{

	SALT;

	// DEBUGLINE;

	if (strlen(keychars) != 32)
	{
		return FALSE;
	}

	// DEBUGLINE;

	unsigned char key[16];

	char temp[3] = {0};
	char *check;
	for (int i = 0; i < 16; i++)
	{
		memcpy(temp, &keychars[2 * i], 2);
		key[i] = strtol(temp, &check, 16);
#ifdef _DEBUG
		fprintf(stderr, "key[%d] = %02hhx\n", i, key[i]);
#endif
		if (check != &temp[2])
		{
			return FALSE;
		}
	}

	// DEBUGLINE;
	SALT;
	return doCheck(user, key);
}

BOOL doCheck(char user[], unsigned char *key)
{

	SALT;

	EVP_MD_CTX *mdctx;

	BOOL bResult = FALSE;

	mdctx = EVP_MD_CTX_create();
	if (mdctx == NULL)
	{
		return FALSE;
	}

	// DEBUGLINE;

	bResult = EVP_DigestInit_ex(mdctx, EVP_sha1(), NULL);
	if (!bResult)
	{
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}

	// DEBUGLINE;

	SALT;
	bResult = EVP_DigestUpdate(mdctx, user, strlen(user));
	if (!bResult)
	{
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}

	// DEBUGLINE;

	BYTE sha1Data[20] = {0};
	DWORD cbHash = sizeof(sha1Data);

	SALT;
	bResult = EVP_DigestFinal_ex(mdctx, sha1Data, NULL);
	if (!bResult)
	{
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}

	// DEBUGLINE;

	EVP_MD_CTX_destroy(mdctx);

	// DEBUGLINE;

#if 0
	printf("SHA1(user) = ");
	for (int i = 0; i < cbHash; i++) {
		printf("%02hhx", sha1Data[i]);
	}
	printf("\n");
#endif
	SALT;
	WORD checkSHA1 = 0;

	for (int i = 0; i < cbHash; i++)
	{
		checkSHA1 *= 31;
		checkSHA1 += sha1Data[i];
	}

	WORD checkKey = 0;
	for (int i = 0; i < 16; i++)
	{
		checkKey *= 137;
		checkKey += key[i];
	}

#ifdef _DEBUG
	printf("checkSHA1 = %04x, checkKey = %04x\n", checkSHA1, checkKey);
#endif

	return checkSHA1 == checkKey;
}

void my_handler(int signum)
{
#ifdef _DEBUG
	printf("Handled signal %d\n", signum);
#endif

}


int main(int argc, char *argv[])
{
# if 0
	if (-1 == ptrace(PTRACE_TRACEME)){
		printf("You lose\n");
#ifdef _DEBUG
		printf("Anti-debugging: Tracer detected!\n");
#endif
		return FALSE;
	}
# endif

// 	signal(SIGTRAP, my_handler);
	
// 	struct timespec start, stop;
// 	clock_gettime(CLOCK_REALTIME, &start);
// 	asm volatile ("int3;\n");
// 	clock_gettime(CLOCK_REALTIME, &stop);

// 	printf("tv_sec: %d, tv_nsec: %d\n", stop.tv_sec, stop.tv_nsec);

// 	long seconds_passed = stop.tv_sec - start.tv_sec;
// 	long nseconds_passed = seconds_passed * 1000000000 + (stop.tv_nsec - start.tv_nsec);
	
// 	if (nseconds_passed < 1000000000) {
// 		printf("You lose\n");
// #ifdef _DEBUG
// 		printf("Anti-debugging: Debugger detected via timing!\n");
// #endif
// 		return FALSE;
// 	}


	ERR_load_crypto_strings();
	OpenSSL_add_all_algorithms();
	OPENSSL_config(NULL);

#ifdef _DEBUG
	if (argc == 2)
	{
		unsigned char key[16];
		srand(time(NULL));
		for (int i = 0; i < 16; i++)
		{
			key[i] = rand();
		}
		while (1)
		{
			printf("Key: ");
			for (int i = 0; i < 16; i++)
			{
				printf("%02hhx", key[i]);
			}
			printf(": ");
			if (doCheck(argv[1], key))
			{
				break;
			}
			for (int i = 15; i >= 0; i--)
			{
				key[i]++;
				if (key[i] != 0)
					break;
			}
			/*for (int i = 0; i < 16; i++) {
				key[i] = rand();
			}*/
		}
		printf("Found key: ");
		for (int i = 0; i < 16; i++)
		{
			printf("%02hhx", key[i]);
		}
		printf("\n");
		goto LAME_EXIT;
	}
#endif

	if (argc != 3)
	{
		fprintf(stderr, "Error: Please provide a username and key\n");
#ifdef WINDOWS
		getc(stdin);
#endif
		exit(-1);
	}

	if (doCheckConvert(argv[1], argv[2]))
	{
		printf("You're winner!\n");
	}
	else
	{
		printf("You lose\n");
	}

#ifdef _DEBUG
LAME_EXIT:
#endif

	exit(0);
}
