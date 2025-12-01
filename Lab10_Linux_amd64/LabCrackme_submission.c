
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

#define DEBUGLINE fprintf(stderr, "DBG: %d\n", __LINE__)

BOOL doCheck(char user[], unsigned char *key);

BOOL doCheckConvert(char user[], char keychars[])
{

	// DEBUGLINE;

	// SALT;

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
	return doCheck(user, key);
}

BOOL doCheck(char user[], unsigned char *key)
{

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

	bResult = EVP_DigestUpdate(mdctx, user, strlen(user));
	if (!bResult)
	{
		EVP_MD_CTX_destroy(mdctx);
		return FALSE;
	}

	// DEBUGLINE;

	BYTE sha1Data[20] = {0};
	DWORD cbHash = sizeof(sha1Data);

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

	WORD foldUser = 0;

	for (int i = 0; i < 20; i++){
		BYTE twisted = sha1Data[i] ^ 0xA5;
		foldUser = (WORD)((foldUser << 5) | (foldUser >> 11));
		foldUser ^= twisted;
	}

	WORD foldKey = 0;
	for (int i = 0; i < 16; i++){
		BYTE transformedKeyByte = key[i] ^ 0x3c;
		foldKey = (WORD)(foldKey * 131 + transformedKeyByte);
	}

#ifdef _DEBUG
	printf("foldUser = %04x, foldKey = %04x\n", foldUser, foldKey);
#endif

uint32_t tmp = foldUser;   

asm volatile(
    ".intel_syntax noprefix\n"
    "    mov eax, %0\n"              
    "    xor eax, 0xDEADBEEF\n"      
    "    xor eax, 0xDEADBEEF\n"      
    "    add eax, 1\n"               
    "    sub eax, 1\n"               
    "    mov %0, eax\n"              
    ".att_syntax prefix\n"
    : "+r"(tmp)                      
    :
    : "eax"                          
);

foldUser = (WORD)tmp;                


	return (foldUser == foldKey);
}

void my_handler(int signum)
{
#ifdef _DEBUG
	printf("Handled signal %d\n", signum);
#endif

}

#ifdef _DEBUG

void generateKey(char* user){
	unsigned char key[16];

	for (int i = 0; i < 16; i++){
		key[i] = rand() % 255;
	}

	DWORD attempt = 0;
	while (1){
		attempt++;
		if (doCheck(user, key)){
			printf("Found key after %d attempts: ", attempt);
			for (int i = 0; i < 16; i++){
				printf("%02hhx", key[i]);
			}
			printf("\nTotal attempts: %d\n", attempt);
			return;
		}

		for (int i = 15; i >= 0; i--){
			key[i]++;
			if (key[i] != 0){
				break;
			}
}
	}
}	

#endif


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

	
	ERR_load_crypto_strings();
	OpenSSL_add_all_algorithms();
	OPENSSL_config(NULL);

#ifdef _DEBUG
	if (argc == 2)
	{
		generateKey(argv[1]);
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
