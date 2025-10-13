#include <stdio.h>
#include <string.h>
#include <sys/types.h>

#ifdef _WIN32
#include <WinSock2.h>
#include <WS2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#else
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

int main(int argc, char** argv) {
	if (argc != 2) {
		fprintf(stderr, "Usage: %s [SERVER_ADDRESS]\n", argv[0]);
		return -1;
	}
	struct sockaddr_in sa;

	int s = socket(AF_INET, SOCK_STREAM, 0);

	// Construct the address of the server, using port 12345
	sa.sin_family = AF_INET;
	struct hostent *hp;
	hp = gethostbyname(argv[1]); // parse the IP/hostname and resolve
	memcpy(&(sa.sin_addr.s_addr), hp->h_addr_list[0], hp->h_length);
	sa.sin_port = htons(12345);

	// Now, connect to the server
	connect(s, (struct sockaddr*) &sa, sizeof(sa));

	// Now send everything from stdin down the connection.
	// NOTE: Ctrl-D is how to input end-of-file.
	while (1) {
		int c = getchar();
		if (c == EOF) {
			break;
		}
		send(s, &c, 1, 0);
	}

	fprintf(stderr, "Closing connection\n");
	close(s);
	return 0;
}
